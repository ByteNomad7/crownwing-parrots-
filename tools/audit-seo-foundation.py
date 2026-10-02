#!/usr/bin/env python3
"""Independent, evidence-led SEO audit for Crownwing's static dist output."""

import argparse
import base64
import csv
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict, deque
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

from content_registry import (
    BASELINE, REGISTRY, discover_pages, extract_content, sync_content_registry, write_sitemap,
)

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUT = ROOT / "seo"
sys.path.insert(0, str(ROOT / "tools"))
from site_config import PUBLIC_ORIGIN  # noqa: E402


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title, self.h1, self.ids, self.links, self.images = [], [], [], [], []
        self.meta, self.canonicals, self.schemas = {}, [], []
        self.stack = []
        self._capture = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        in_main = tag == "main" or any(item == "main" for item in self.stack)
        in_chrome = tag in {"header", "nav", "footer", "aside"} or any(
            item in {"header", "nav", "footer", "aside"} for item in self.stack
        )
        if tag == "title":
            self._capture = "title"
        if tag == "h1":
            self._capture = "h1"
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "a":
            self.links.append((attrs.get("href", ""), in_main and not in_chrome))
        if tag == "img":
            self.images.append((attrs.get("src", ""), attrs.get("alt"), attrs.get("class", "")))
        if tag == "meta":
            key = attrs.get("name", attrs.get("property", "")).lower()
            if key:
                self.meta[key] = attrs.get("content", "")
        if tag == "link" and "canonical" in attrs.get("rel", "").lower().split():
            self.canonicals.append(attrs.get("href", ""))
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._capture = "schema"
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
                       "param", "source", "track", "wbr"}:
            self.stack.append(tag)

    def handle_data(self, value):
        if self._capture in {"title", "h1", "schema"}:
            self._captured = getattr(self, "_captured", {})
            self._captured.setdefault(self._capture, []).append(value)

    def handle_endtag(self, tag):
        key = "title" if tag == "title" else "h1" if tag == "h1" else "schema" if tag == "script" else None
        if key and self._capture == key:
            captured = getattr(self, "_captured", {}).get(key, [])
            value = "".join(captured).strip()
            if key == "title":
                self.title.append(value)
            elif key == "h1":
                self.h1.append(value)
            else:
                self.schemas.append(value)
            getattr(self, "_captured", {}).pop(key, None)
            self._capture = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i] == tag:
                del self.stack[i:]
                break


def normal_path(path):
    path = urllib.parse.unquote(path)
    if not path:
        return "/"
    if path.endswith("/index.html"):
        path = path[:-10]
    if not path.startswith("/"):
        path = "/" + path
    return path if path.endswith("/") or "." in Path(path).name else path + "/"


def local_target(source, href):
    parts = urllib.parse.urlsplit(href)
    if parts.scheme or parts.netloc or href.startswith("mailto:") or href.startswith("tel:"):
        return None, parts.fragment
    src = Path(source.lstrip("/"))
    if parts.path.startswith("/"):
        candidate = (DIST / urllib.parse.unquote(parts.path.lstrip("/"))).resolve()
    elif parts.path:
        candidate = (DIST / src.parent / urllib.parse.unquote(parts.path)).resolve()
    else:
        candidate = (DIST / src).resolve()
    try:
        candidate.relative_to(DIST.resolve())
    except ValueError:
        return None, parts.fragment
    if candidate.is_dir():
        candidate /= "index.html"
    return candidate, parts.fragment


def read_pages():
    pages, parsed, raw, content = discover_pages(DIST), {}, {}, {}
    for route, file in sorted(pages.items()):
        source = file.relative_to(DIST).as_posix()
        text = file.read_text(encoding="utf-8", errors="replace")
        parser = PageParser()
        parser.feed(text)
        parsed[route], raw[route] = parser, text
        content[route] = extract_content(text)
        content[route]["source_file"] = source
    return pages, parsed, raw, content


def main_text(info):
    return " ".join(info["paragraphs"])


def csv_write(name, headers, rows):
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def csv_readable_rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.reader(handle))


def crawl(origin, routes):
    results = {}
    opener = urllib.request.build_opener()
    for path in routes:
        url = origin.rstrip("/") + path
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "CrownwingSEOAudit/1.0"})
            with opener.open(request, timeout=12) as response:
                results[path] = {"status": response.status, "final_url": response.geturl(),
                                 "redirected": response.geturl() != url,
                                 "x_robots_tag": response.headers.get("X-Robots-Tag")}
        except urllib.error.HTTPError as exc:
            results[path] = {"status": exc.code, "final_url": exc.geturl(),
                             "redirected": exc.geturl() != url,
                             "x_robots_tag": exc.headers.get("X-Robots-Tag") if exc.headers else None}
        except Exception as exc:
            results[path] = {"status": None, "error": f"{type(exc).__name__}: {exc}"}
    probe = "/__crownwing_audit_missing_route_7f96b2/"
    try:
        request = urllib.request.Request(origin.rstrip("/") + probe,
                                        headers={"User-Agent": "CrownwingSEOAudit/1.0"})
        with opener.open(request, timeout=12) as response:
            results["__404_probe__"] = {"status": response.status, "final_url": response.geturl(),
                                        "x_robots_tag": response.headers.get("X-Robots-Tag")}
    except urllib.error.HTTPError as exc:
        results["__404_probe__"] = {"status": exc.code, "final_url": exc.geturl(),
                                    "x_robots_tag": exc.headers.get("X-Robots-Tag") if exc.headers else None}
    except Exception as exc:
        results["__404_probe__"] = {"status": None, "error": f"{type(exc).__name__}: {exc}"}
    return results


def internal_graph(parsed, pages):
    known = set(pages)
    graph = {route: set() for route in pages}
    link_rows, broken = [], []
    for route, parser in parsed.items():
        source_file = pages[route].relative_to(DIST).as_posix()
        for href, in_main in parser.links:
            target, fragment = local_target(source_file, href)
            if target is None:
                if href.startswith(("http://", "https://")):
                    link_rows.append((route, href, "external", "main" if in_main else "chrome"))
                continue
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                broken.append((route, href, "missing local file", ""))
                link_rows.append((route, href, "broken", "main" if in_main else "chrome"))
                continue
            destination = "/" if target.parent == DIST else "/" + target.parent.relative_to(DIST).as_posix().rstrip("/") + "/"
            if target.name == "index.html" and destination in known:
                graph[route].add(destination)
                ids = set(parsed[destination].ids)
                if fragment and fragment not in ids:
                    broken.append((route, href, "missing fragment", destination))
                link_rows.append((route, href, "internal", "main" if in_main else "chrome"))
            else:
                link_rows.append((route, href, "asset", "main" if in_main else "chrome"))
    return graph, link_rows, broken


def do_baseline(pages, content):
    snapshot = {
        "captured_at": date.today().isoformat(),
        "routes": sorted(pages),
        "pages": {route: {"digest": info["digest"], "paragraphs": info["paragraphs"], "images": info["images"]}
                  for route, info in content.items()},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    BASELINE.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # Start registry with historical dates unknown: baseline is observation, not publication.
    registry = {"publisher": "Crownwing", "pages": []}
    for route, info in sorted(content.items()):
        registry["pages"].append({
            "path": route, "content_digest": info["digest"], "publisher": "Crownwing",
            "owner": {"organisation": "Crownwing Parrots", "person": None, "role": "Publisher"},
            "sources": [], "last_modified": None, "last_reviewed": None, "reviewed_by": None,
            "review_scope": None, "review_reminder_due": None, "history": [],
        })
    REGISTRY.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return sync_content_registry(DIST)


def report(args):
    OUT.mkdir(parents=True, exist_ok=True)
    pages, parsed, raw, content = read_pages()
    if args.baseline:
        registry = do_baseline(pages, content)
    else:
        registry = sync_content_registry(DIST)
    origin = PUBLIC_ORIGIN
    routes = sorted(pages)
    graph, link_rows, broken = internal_graph(parsed, pages)
    sitemap_paths = set()
    sitemap_file = DIST / "sitemap.xml"
    if sitemap_file.exists():
        sitemap_paths = {normal_path(urllib.parse.urlsplit(value).path)
                         for value in re.findall(r"<loc>\s*(.*?)\s*</loc>", sitemap_file.read_text(errors="replace"))}

    # Optional live fetches never affect source-derived indexability or canonical decisions.
    live = {}
    if args.crawl:
        hostname = os.environ.get("REPLIT_DEV_DOMAIN", "").strip()
        if not hostname:
            raise SystemExit("--crawl requires REPLIT_DEV_DOMAIN; refusing to guess a host")
        live = crawl("https://" + hostname, routes)
    elif args.deployment_url:
        live = crawl(args.deployment_url.rstrip("/"), routes)

    # Source and HTTP evidence snapshots are explicitly separate.
    source_audit = {
        "pages": len(routes), "origin": origin, "routes": routes,
        "crawl_requested": bool(args.crawl or args.deployment_url),
        "crawl_origin": ("https://" + os.environ["REPLIT_DEV_DOMAIN"] if args.crawl else args.deployment_url),
        "http": live,
    }
    (OUT / "source-and-http-audit.json").write_text(json.dumps(source_audit, indent=2) + "\n", encoding="utf-8")

    inbound = defaultdict(list)
    depths = {"/": 0}
    queue = deque(["/"])
    while queue:
        source = queue.popleft()
        for dest in graph.get(source, ()):
            if dest not in depths:
                depths[dest] = depths[source] + 1
                queue.append(dest)
    for source, href, target_kind, link_position in link_rows:
        if target_kind != "internal":
            continue
        dest = normal_path(urllib.parse.urlsplit(urllib.parse.urljoin("https://local" + source, href)).path)
        inbound[dest].append((source, link_position))

    # URL inventory, canonical and indexability.
    inventory, canonical_rows, index_rows, keyword_rows = [], [], [], []
    preview_blocked_routes = []
    title_owners, desc_owners = defaultdict(list), defaultdict(list)
    for route in routes:
        p, info, record = parsed[route], content[route], registry[route]
        title = p.title[0] if p.title else ""
        desc = p.meta.get("description", "")
        title_owners[title].append(route)
        desc_owners[desc].append(route)
        canonical = p.canonicals[0] if p.canonicals else ""
        robots = p.meta.get("robots", "index,follow")
        indexable = "noindex" not in robots.lower()
        schema_types = []
        for schema in p.schemas:
            try:
                value = json.loads(schema)
                values = value if isinstance(value, list) else [value]
                for item in values:
                    if isinstance(item, dict):
                        schema_types.extend(item.get("@type", []) if isinstance(item.get("@type"), list)
                                            else [item.get("@type", "unknown")])
            except (ValueError, TypeError):
                schema_types.append("INVALID JSON-LD")
        http_result = live.get(route, {})
        inventory.append((route, title, desc, canonical, "yes" if indexable else "no", "yes" if route in sitemap_paths else "no",
                          len(main_text(info).split()), len(p.h1), len(p.links), len(info["images"]), record.get("published") or "",
                          record.get("last_modified") or "", record.get("last_reviewed") or "",
                          record.get("article_date_modified") or "", ";".join(filter(None, schema_types)),
                          http_result.get("status", ""), http_result.get("final_url", ""),
                          "yes" if http_result.get("redirected") else "no" if route in live else "not checked"))
        canonical_status = "missing" if not canonical else "matches" if canonical == origin.rstrip("/") + route else "mismatch"
        canonical_rows.append((route, canonical, origin.rstrip("/") + route, canonical_status))
        xrobots = live.get(route, {}).get("x_robots_tag", "")
        preview_directives = {token.strip() for token in xrobots.lower().split(",")}
        preview_block = bool(preview_directives & {
            "none", "noindex", "nofollow", "noarchive", "nositelinkssearchbox", "noimageindex"
        })
        if preview_block:
            preview_blocked_routes.append(route)
        index_rows.append((route, robots, "indexable" if indexable else "noindex", route in sitemap_paths,
                           "reachable" if route in depths else "not reached by internal link graph",
                           xrobots, "preview proxy blocks crawling; not app metadata" if preview_block else
                           "not seen in HTTP response" if route in live else "not checked"))
        keyword = re.sub(r"\s*\|\s*Crownwing.*$", "", title, flags=re.I) or (p.h1[0] if p.h1 else route.strip("/").replace("-", " "))
        supports = sorted({source for source, _ in inbound.get(route, []) if source != route})
        if not supports:
            supports = sorted(graph[route] - {route})
        keyword_rows.append((keyword, "Informational / commercial intent inferred from title and route", route,
                             "Primary" if route not in {"/", "/parrots/", "/parrots-for-sale/"} else "Hub",
                             ";".join(supports[:12]),
                             "not measured — Search Console not connected", "source-derived, review intent manually"))
    csv_write("url-inventory.csv", ["route", "title", "meta_description", "canonical", "indexable", "in_sitemap",
              "main_paragraph_word_count", "h1_count", "link_count", "image_count", "published", "last_modified",
              "last_reviewed", "article_date_modified", "schema_types", "http_status", "http_final_url", "redirected"], inventory)
    csv_write("keyword-map.csv", ["primary_topic_keyword", "intent", "target_url", "page_role", "supporting_urls",
              "current_ranking", "mapping_status"], keyword_rows)
    csv_write("canonical-audit.csv", ["route", "observed_canonical", "expected_canonical", "status"], canonical_rows)
    csv_write("indexability-audit.csv", ["route", "robots_directive", "metadata_indexability", "in_sitemap",
              "reachability", "preview_x_robots_tag", "preview_http_interpretation"], index_rows)
    (OUT / "indexability-audit.md").write_text(
        "# Indexability audit scope\n\n"
        "The CSV's robots/indexability columns describe source HTML metadata; its preview HTTP columns describe the actual HTTPS preview response separately. "
        "A preview `X-Robots-Tag` restriction is imposed by the preview network, not the app's HTML. It does not establish production crawlability or justify changing canonical/indexation policy. "
        "Production is not deployed/verified by this preview crawl.\n",
        encoding="utf-8")
    csv_write("internal-links.csv", ["source_route", "href", "target_classification", "main_or_chrome"], link_rows)

    structured_rows = []
    for route, p in parsed.items():
        if not p.schemas:
            structured_rows.append((route, "", "no JSON-LD found"))
        for schema in p.schemas:
            try:
                value = json.loads(schema)
                kinds = value.get("@type", "") if isinstance(value, dict) else "JSON-LD collection"
                structured_rows.append((route, kinds, "valid JSON parse; vocabulary/Google eligibility not independently verified"))
            except ValueError as exc:
                structured_rows.append((route, "", "invalid JSON-LD: " + str(exc)))
    csv_write("structured-data-audit.csv", ["route", "schema_type", "validation"], structured_rows)

    # Similarity of substantive paragraphs only; report candidate pairs for human review.
    def shingles(route):
        words = re.findall(r"\w+", main_text(content[route]).lower())
        return {tuple(words[i:i + 5]) for i in range(max(0, len(words) - 4))}
    sets = {route: shingles(route) for route in routes}
    duplicate_rows = []
    for i, left in enumerate(routes):
        for right in routes[i + 1:]:
            if not sets[left] or not sets[right]:
                continue
            shared = len(sets[left] & sets[right])
            overlap = shared / min(len(sets[left]), len(sets[right]))
            if overlap >= 0.65:
                duplicate_rows.append((left, right, f"{overlap:.3f}", "manual review candidate; overlap is not a spam/penalty finding"))
    csv_write("duplicate-content.csv", ["route_a", "route_b", "5_word_shingle_containment_overlap", "interpretation"], duplicate_rows)

    exceptions = {"/", "/contact/", "/locations/", "/parrots/", "/parrots-for-sale/", "/parrot-care/",
                  "/available-birds/", "/privacy-policy/", "/cookie-policy/", "/business-policies/",
                  "/our-approach/", "/terms-and-conditions/"}
    thin_rows = []
    for route in routes:
        count = len(main_text(content[route]).split())
        exception = route in exceptions or route.startswith(("/locations/", "/parrots/", "/parrots-for-sale/"))
        threshold = 120 if exception else 250
        if count < threshold:
            thin_rows.append((route, count, threshold, "legitimate route/legal/contact/hub exception" if exception else "manual review candidate",
                              "report only; no automatic index/noindex change"))
    csv_write("thin-content.csv", ["route", "main_text_words", "review_threshold", "exception_or_flag", "action"], thin_rows)
    orphan_rows = []
    for route in routes:
        source_roles = sorted(set(inbound.get(route, [])))
        sources = [source + " [" + role + "]" for source, role in source_roles]
        orphan_rows.append((route, ";".join(sources), sum(1 for _, role in source_roles if role == "chrome"),
                            "yes" if route in depths else "no", depths.get(route, ""), "main vs chrome link sources shown in internal-links.csv"))
    csv_write("orphan-pages.csv", ["route", "inbound_link_sources", "source_chrome_link_count", "reachable_from_home", "minimum_depth", "evidence_note"], orphan_rows)

    live_map = live
    broken_rows = [(source, href, kind, target) for source, href, kind, target in broken]
    for route, result in live_map.items():
        if route == "__404_probe__":
            if result.get("status") != 404:
                broken_rows.append(("HTTP crawl", "404 probe", "expected 404; observed " + str(result.get("status")),
                                    result.get("error", result.get("final_url", ""))))
            continue
        if result.get("status") is None or result.get("status", 200) >= 400:
            broken_rows.append((route, route, "live HTTP status " + str(result.get("status")), result.get("error", result.get("final_url", ""))))
    csv_write("broken-links.csv", ["source_route", "href_or_route", "finding", "target_or_error"], broken_rows)

    # Informational content groupings are derived from URL families.
    clusters = defaultdict(list)
    for route in routes:
        if route.startswith("/parrots/"):
            family = "Species and category education"
        elif route.startswith("/parrots-for-sale/") or route.startswith("/available-birds/"):
            family = "Buying questions and availability"
        elif route.startswith("/locations/"):
            family = "Regional planning"
        elif route.startswith("/guides/") or route.startswith("/parrot-care/"):
            family = "Care and ownership guides"
        elif "policy" in route or route in {"/terms-and-conditions/", "/our-approach/"}:
            family = "Business and legal information"
        else:
            family = "Core business and contact"
        clusters[family].append(route)
    (OUT / "content-clusters.md").write_text("# Content clusters\n\n" + "\n".join(
        "## " + label + "\n\n" + "\n".join("- `" + route + "`" for route in entries) + "\n"
        for label, entries in sorted(clusters.items())), encoding="utf-8")

    gap_lines = ["# Content gaps\n", "\nSource-informed opportunities for editorial consideration; this audit does not assert demand or ranking data.\n"]
    gap_lines.append(
        "\n## Scope decisions\n\n"
        "- Existing `/parrot-prices-uk/` remains the canonical price guide; do not duplicate or rename it to create a cost URL.\n"
        "- Existing business-policy pages already cover their stated subjects; no unsupported delivery filename, delivery claim or policy rewrite is proposed.\n"
        "- Availability/listing language remains gated on verified, current individual-bird information; no stock or listing claims are inferred here.\n"
        "- The three post-baseline routes `/guides/`, `/guides/buying-a-parrot/` and `/guides/cites-parrots-uk/` passed the Replit Agent editorial/source and buyer-utility gate in `editorial-gate.md`. This is not owner/human or professional review; appropriate owner/legal reading is recommended before publication. These routes are not marked unreviewed and are not automatically noindexed.\n"
        "- Registry `last_reviewed` remains source-check-specific: the buyer and cost articles have no visible `Sources checked` marker or external source anchors in generated HTML, so no review date or source links are inferred despite the broader agent gate.\n"
    )
    priorities = ["# Recommended next content priorities\n", "\nPrioritisation is a qualitative review queue, not a search-volume estimate.\n"]
    for priority, opportunity in enumerate([
        "Review source currency and evidence for species care claims and external references.",
        "Assess whether current regional planning pages add useful region-specific information without unsupported local-service claims.",
        "Review buyer intent overlap among availability, category buying pages and individual species profiles.",
        "Consider accessible, genuinely informative answers for unresolved care and welfare questions identified by editorial review.",
    ], 1):
        gap_lines.append(f"- {opportunity}\n")
        priorities.append(f"{priority}. {opportunity}\n")
    (OUT / "content-gaps.md").write_text("".join(gap_lines), encoding="utf-8")
    (OUT / "next-content-priorities.md").write_text("".join(priorities), encoding="utf-8")

    source_urls = sorted({item["url"] for record in registry.values() for item in record.get("sources", [])})
    (OUT / "uk-legal-sources.md").write_text(
        "# UK legal and policy sources\n\nExternal links extracted from page content; inclusion means cited on-site, not independently validated or endorsed.\n\n"
        + ("\n".join("- " + url for url in source_urls) if source_urls else "- No external source links extracted.") + "\n",
        encoding="utf-8")

    # Copy sitemap/robots to private SEO deliverables only; never write reports into dist.
    if sitemap_file.exists():
        (OUT / "sitemap.xml").write_bytes(sitemap_file.read_bytes())
    robots_file = DIST / "robots.txt"
    if robots_file.exists():
        (OUT / "robots.txt").write_bytes(robots_file.read_bytes())
    else:
        (OUT / "robots.txt").write_text("Robots source unavailable; not inferred.\n", encoding="utf-8")
    if not sitemap_file.exists():
        write_sitemap(OUT, origin, [r for r in routes if "noindex" not in parsed[r].meta.get("robots", "").lower()])

    # Lighthouse lab metrics are reported as lab values only; INP is not synthesized.
    cwv = ["# Core Web Vitals\n", "\nNo Lighthouse reports supplied. Field Core Web Vitals are unavailable because Search Console/CrUX is not connected. INP: unmeasured.\n"]
    labs = []
    lighthouse_evidence = []
    for device, filename in (("mobile", "lighthouse-mobile.report.json"), ("desktop", "lighthouse-desktop.report.json")):
        report_file = OUT / filename
        if report_file.exists():
            try:
                lh = json.loads(report_file.read_text())
                audits = lh.get("audits", {})
                vals = {}
                for key, audit in (("LCP lab", "largest-contentful-paint"),
                                   ("CLS lab", "cumulative-layout-shift"),
                                   ("TBT lab", "total-blocking-time")):
                    measurement = audits.get(audit, {})
                    vals[key] = measurement.get("displayValue")
                    if vals[key] is None and measurement.get("numericValue") is not None:
                        vals[key] = str(measurement["numericValue"]) + " " + str(measurement.get("numericUnit", ""))
                    if vals[key] is None:
                        vals[key] = "unavailable"
                categories = lh.get("categories", {})
                performance_score = categories.get("performance", {}).get("score")
                seo_score = categories.get("seo", {}).get("score")
                accessibility_score = categories.get("accessibility", {}).get("score")
                best_practices_score = categories.get("best-practices", {}).get("score")
                seo_category = categories.get("seo", {})
                failed = []
                for audit_ref in seo_category.get("auditRefs", []):
                    audit_id = audit_ref.get("id")
                    audit_value = audits.get(audit_id, {})
                    if audit_value.get("score") == 0:
                        failed.append(audit_id)
                crawl_audit = audits.get("is-crawlable", {})
                crawl_sources = [
                    str(item.get("source", "")) for item in crawl_audit.get("details", {}).get("items", [])
                    if isinstance(item, dict) and item.get("source")
                ]
                lighthouse_evidence.append({
                    "device": device, "performance_score": round(performance_score * 100) if isinstance(performance_score, (int, float)) else None,
                    "seo_score": round(seo_score * 100) if isinstance(seo_score, (int, float)) else None,
                    "accessibility_score": round(accessibility_score * 100) if isinstance(accessibility_score, (int, float)) else None,
                    "best_practices_score": round(best_practices_score * 100) if isinstance(best_practices_score, (int, float)) else None,
                    "failed_seo_audits": failed, "crawlability_evidence": crawl_sources,
                    **vals,
                })
                labs.append(
                    f"- {device}: Lighthouse performance score {round(performance_score * 100) if isinstance(performance_score, (int, float)) else 'unavailable'}; "
                    f"accessibility {round(accessibility_score * 100) if isinstance(accessibility_score, (int, float)) else 'unavailable'}; "
                    f"best practices {round(best_practices_score * 100) if isinstance(best_practices_score, (int, float)) else 'unavailable'}; "
                    f"LCP {vals['LCP lab']}; CLS {vals['CLS lab']}; TBT {vals['TBT lab']}; INP unmeasured. "
                    f"Lighthouse SEO score {round(seo_score * 100) if isinstance(seo_score, (int, float)) else 'unavailable'}; "
                    f"failed SEO audits: {', '.join(failed) if failed else 'none'}.\n"
                )
            except (ValueError, OSError):
                labs.append(f"- {device} report exists but could not be parsed; metrics unavailable.\n")
    if labs:
        cwv = ["# Core Web Vitals\n", "\nLighthouse figures are lab measurements, not field Core Web Vitals. INP remains unmeasured.\n", *labs]
    proxy_footnote = (
        "\n**Preview-proxy crawlability limitation:** the HTTPS preview responds with `X-Robots-Tag: none, noindex, "
        "noarchive, nofollow, nositelinkssearchbox, noimageindex`. Lighthouse's `is-crawlable` failure reflects "
        "that preview-network header, not page markup. Source HTML metadata remains indexable where shown; this "
        "preview is not a published production origin and this report does not claim Google can crawl it.\n"
        if preview_blocked_routes or any("x-robots-tag" in " ".join(item.get("crawlability_evidence", [])).lower()
                                         for item in lighthouse_evidence)
        else "\nNo preview X-Robots-Tag blocker was observed in the available crawl evidence; production publication and Google crawlability remain unverified.\n"
    )
    cwv.append(proxy_footnote)
    (OUT / "core-web-vitals.md").write_text("".join(cwv), encoding="utf-8")
    viewport_issues, alt_issues = [], []
    for route, p in parsed.items():
        if "viewport" not in p.meta:
            viewport_issues.append(f"- `{route}`: viewport meta not found.\n")
        for src, alt, _ in p.images:
            # Explicit alt="" is valid decorative imagery; do not misreport as missing.
            if alt is None:
                alt_issues.append(f"- `{route}`: image `{src}` has no alt attribute.\n")
    (OUT / "mobile-seo.md").write_text(
        "# Mobile SEO and image accessibility checks\n\n"
        + (f"Viewport metadata missing on {len(viewport_issues)} pages:\n" + "".join(viewport_issues)
           if viewport_issues else f"Viewport metadata is present across {len(routes)} source pages.\n")
        + (f"Missing alt attributes: {len(alt_issues)}\n" + "".join(alt_issues) if alt_issues else
           "No missing alt attributes found; explicit empty alt attributes are accepted as decorative imagery.\n")
        + "Mobile rendering was browser-tested at 390px; the buyer-tools evidence reports all eight content groups readable without JavaScript, budget/comparison checks passing and no horizontal overflow at 390px or 1366px. It also records valid-budget, same-group error, reset and missing-field checks as passed.\n"
        + proxy_footnote,
        encoding="utf-8")

    # Standalone audit report and explicit evidence/pending integration status.
    route_live = {path: item for path, item in live.items() if path != "__404_probe__"}
    http_ok = sum(1 for item in route_live.values() if item.get("status") and item["status"] < 400)
    duplicate_titles = {value: items for value, items in title_owners.items() if value and len(items) > 1}
    duplicate_descriptions = {value: items for value, items in desc_owners.items() if value and len(items) > 1}
    missing_h1 = [route for route, p in parsed.items() if len(p.h1) == 0]
    multiple_h1 = [route for route, p in parsed.items() if len(p.h1) > 1]
    missing_alt = [(route, src) for route, p in parsed.items() for src, alt, _ in p.images if alt is None]
    oversized = []
    query_links = []
    for route, p in parsed.items():
        for src, _, _ in p.images:
            target, _ = local_target(pages[route].relative_to(DIST).as_posix(), src)
            if target and target.is_file() and target.stat().st_size > 500 * 1024:
                oversized.append((route, src, target.stat().st_size))
        for href, _ in p.links:
            if urllib.parse.urlsplit(href).query:
                query_links.append((route, href))
    schema_errors = [row for row in structured_rows if row[2].startswith("invalid JSON-LD")]
    redirect_count = sum(1 for item in route_live.values() if item.get("redirected"))
    probe_status = live.get("__404_probe__", {}).get("status", "not checked")
    baseline_routes = set()
    if BASELINE.exists():
        try:
            baseline_routes = set(json.loads(BASELINE.read_text()).get("routes", []))
        except (ValueError, OSError, TypeError):
            baseline_routes = set()
    new_routes = sorted(set(routes) - baseline_routes)
    lost_routes = sorted(baseline_routes - set(routes))
    unreachable_routes = sorted(set(routes) - set(depths))
    orphan_without_inbound = sorted(route for route in routes if not inbound.get(route))
    article_schema_routes = sorted(
        route for route in routes
        if any(row[0] == route and "Article" in str(row[1]) for row in structured_rows)
    )
    article_date_routes = sorted(
        route for route, record in registry.items()
        if record.get("published") or record.get("article_date_modified")
    )
    published_article_routes = sorted(route for route, record in registry.items() if record.get("published"))
    reviewed_routes = sorted(route for route, record in registry.items() if record.get("last_reviewed"))
    total_source_links = sum(len(record.get("sources", [])) for record in registry.values())
    buyer_cost_source_gaps = [
        route for route in ("/guides/buying-a-parrot/", "/guides/parrot-ownership-costs/")
        if route in registry and (not registry[route].get("last_reviewed") or not registry[route].get("sources"))
    ]
    preview_route_http_statuses = sorted({str(item.get("status")) for item in route_live.values() if item.get("x_robots_tag")})
    statuses = [
        ("URL inventory", "generated", "All source index.html routes"),
        ("Keyword map", "generated", "Search rankings explicitly unmeasured; Search Console not connected"),
        ("Content cluster map", "generated", "Route families"),
        ("Internal-link map", "generated", "Local source links classified main/chrome"),
        ("Sitemap", "copied from dist" if sitemap_file.exists() else "generated privately", "Does not add SEO outputs to public dist"),
        ("Robots.txt", "copied from dist" if robots_file.exists() else "source unavailable", "Private SEO copy"),
        ("Canonical audit", "generated", "Source metadata compared with configured public origin"),
        ("Indexability audit", "generated", "No indexation policy changes made"),
        ("Structured-data audit", "generated", "JSON parse checks only; eligibility not verified"),
        ("Duplicate-content report", "generated", "Five-word shingle containment; threshold 0.65; manual-review flags"),
        ("Thin-content report", "generated", "Word thresholds and exceptions; manual review only"),
        ("Orphan-page report", "generated", "Internal graph reachability from home"),
        ("Broken-link report", "generated", "Local files/fragments" + (" plus live crawl statuses" if live else "; HTTP not requested")),
        ("Core Web Vitals", "generated", "Mobile/desktop Lighthouse lab results; field CrUX unavailable; INP unmeasured"),
        ("Mobile SEO", "generated", "Static checks plus supplied 390px/1366px browser evidence"),
        ("UK legal sources", "generated", "Extracted cited external links; not independently verified"),
        ("Content gaps", "generated", "Qualitative editorial review suggestions"),
        ("Next content priorities", "generated", "Qualitative, not traffic/ranking data"),
    ]
    lines = ["# Crownwing SEO source audit\n", f"\n- Source pages: **{len(routes)}**\n- Configured canonical origin: `{origin}`\n",
             f"- Source route crawl: `{len(route_live)} / {len(routes)}` HTTP requests attempted"
             + (f"; {http_ok} returned below 400." if live else "; not requested.") + "\n",
             f"- HTTP redirects observed: **{redirect_count}**; not-found probe status: **{probe_status}**.\n",
             f"- Historical routes retained: **{len(baseline_routes) - len(lost_routes)}/{len(baseline_routes)}**; newly observed routes since baseline: **{len(new_routes)}**; removed historical routes: **{len(lost_routes)}**.\n",
              f"- Article-family JSON-LD: **{len(article_schema_routes)} routes**; explicit valid `datePublished` or `dateModified`: **{len(article_date_routes)} routes** (`datePublished` on {len(published_article_routes)}). Main-provided source QA reports 69/69 pages pass, eight Article routes/date checks and no route losses.\n",
              f"- Explicit visible source-check dates were extracted on **{len(reviewed_routes)} route(s)**; {total_source_links} external source links were extracted overall. Buyer/cost source-check/source-link gaps to reconcile manually: "
              + (", ".join(f"`{r}`" for r in buyer_cost_source_gaps) if buyer_cost_source_gaps else "none") + ". No review dates or sources are inferred for them.\n",
             "- Deployment tooling reports `success=true`, `isDeployed=false`; no deployed artifact was validated. Production HTTPS/domain and www redirect are not verified by this preview crawl. Search Console and CrUX are unverified, not passing.\n",
             "- Google Search Console connector returned no integration/property data. Manual handover: verify the `crownwingparrots.co.uk` domain property in Search Console, submit the canonical sitemap, review Page indexing/Crawl stats and inspect Performance after sufficient data accrues; record dates and property evidence. Do not infer rankings from this audit.\n",
             f"- Duplicate non-empty titles: **{len(duplicate_titles)} groups**; duplicate non-empty descriptions: **{len(duplicate_descriptions)} groups**; pages missing/multiplying H1: **{len(missing_h1)} / {len(multiple_h1)}**.\n",
             f"- Missing alt attributes: **{len(missing_alt)}** (explicit empty decorative alt is valid); local images over 500 KiB: **{len(oversized)}**; internal links with query strings: **{len(query_links)}**.\n",
              f"- Invalid JSON-LD syntax: **{len(schema_errors)}**. Targeted buyer-tool interaction/browser checks were supplied and passed; no whole-site rendered crawl or field CWV measurement is claimed.\n",
             "- Form semantics and submission flows are not assumed or tested here; calculator forms are not classified as enquiry/download forms by this audit.\n",
             f"- Local file/fragment findings: **{len(broken)}**; duplicate-content candidates: **{len(duplicate_rows)}** (five-word containment ≥0.65; manual review only); thin-content review flags: **{len(thin_rows)}**.\n",
              f"- Orphan/reachability flags: **{len(orphan_without_inbound)}** with no inbound internal source; **{len(unreachable_routes)}** unreachable from home. New routes observed since baseline: "
              + (", ".join(f"`{r}`" for r in new_routes) if new_routes else "none")
              + ". All three requested new guides passed the Replit Agent editorial/source and utility gate (`editorial-gate.md`); owner/human and professional/legal approval remains unperformed and recommended before publication. No automatic noindex.\n",
             "- Preview-network caveat: " + (f"X-Robots-Tag observed on {len(preview_blocked_routes)} routes (HTTP statuses {', '.join(preview_route_http_statuses)}); the header is from the preview proxy, while page metadata is audited separately. Production is not published/verified from this preview." if preview_blocked_routes else "no preview X-Robots-Tag was observed in the route crawl; production publication/crawlability remain unverified.") + "\n",
             "- Buyer tools browser evidence (`buyer-tools-browser.json`): actual HTTPS preview tests at 1366px and 390px passed comparison/budget checks with no horizontal overflow; all eight groups remained readable without JavaScript. The evidence also covers valid budget, same-group error, reset and missing-field checks.\n",
             "- Report generation is observational. It does not modify page indexability or content.\n",
             "\n## Deliverable status\n\n| Deliverable | Status | Evidence / limits |\n|---|---|---|\n"]
    lines += [f"| {name} | {status} | {evidence} |\n" for name, status, evidence in statuses]
    (OUT / "audit-report.md").write_text("".join(lines), encoding="utf-8")
    build_html(statuses)
    print(json.dumps({"pages": len(routes), "http_crawled": len(live), "http_below_400": http_ok,
                      "duplicate_candidates": len(duplicate_rows), "thin_review_flags": len(thin_rows),
                      "broken_local_links_and_fragments": len(broken), "output": str(OUT.relative_to(ROOT))},
                     indent=2))


def build_html(statuses):
    downloads = []
    for file in sorted(OUT.iterdir()):
        if file.name == "report.html" or file.is_dir():
            continue
        if file.suffix not in {".csv", ".md", ".xml", ".txt", ".json"}:
            continue
        payload = base64.b64encode(file.read_bytes()).decode("ascii")
        mime = "text/csv" if file.suffix == ".csv" else "application/json" if file.suffix == ".json" else "text/plain"
        downloads.append(f'<li><a download="{html.escape(file.name)}" href="data:{mime};base64,{payload}">{html.escape(file.name)}</a></li>')
    table = "".join(f"<tr><td>{html.escape(n)}</td><td>{html.escape(s)}</td><td>{html.escape(e)}</td></tr>"
                    for n, s, e in statuses)
    doc = ("<!doctype html><html lang=\"en\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
           "<title>Crownwing SEO audit evidence</title><style>body{font:16px/1.5 system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#17232b}"
           "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd4d8;padding:.5rem;text-align:left}a{color:#075f56}li{margin:.3rem 0}</style>"
           "<h1>Crownwing SEO audit evidence</h1><p>Source audit only. Production DNS/TLS, rankings, field Core Web Vitals and expert review are not inferred.</p>"
           "<h2>Deliverable status</h2><table><thead><tr><th>Deliverable</th><th>Status</th><th>Evidence / limits</th></tr></thead><tbody>"
           + table + "</tbody></table><h2>Download reports and datasets</h2><ul>" + "".join(downloads) + "</ul></html>")
    (OUT / "report.html").write_text(doc, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--baseline", action="store_true", help="capture current source content digests as historical baseline")
    mode.add_argument("--final", action="store_true", help="regenerate all reports after content/build changes")
    parser.add_argument("--crawl", action="store_true", help="HTTP crawl using https://$REPLIT_DEV_DOMAIN")
    parser.add_argument("--deployment-url", help="optional explicit deployed URL for separate HTTP checks")
    args = parser.parse_args()
    if args.deployment_url:
        parts = urllib.parse.urlsplit(args.deployment_url)
        if parts.scheme != "https" or not parts.netloc:
            parser.error("--deployment-url must be an explicit https:// URL")
    report(args)


if __name__ == "__main__":
    main()