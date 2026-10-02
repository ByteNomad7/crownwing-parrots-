#!/usr/bin/env python3
"""Read-only site audit and editorial reports. Never changes dist or URL policy."""

import csv
import hashlib
import html
import importlib.util
import itertools
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

from classification_decisions import DECISIONS
from content_registry import ContentParser, BASELINE, ROOT
from site_config import PUBLIC_ORIGIN

OUT = ROOT / "seo"
spec = importlib.util.spec_from_file_location("foundation", ROOT / "tools/audit-seo-foundation.py")
foundation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foundation)


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images, self.resources, self.headings, self.query_links = [], [], [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img":
            self.images.append(a)
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append(int(tag[1]))
        if tag in {"img", "script", "source"} and a.get("src"):
            self.resources.append(a["src"])
        if tag == "link" and a.get("rel") in {"stylesheet", "icon", "preload"} and a.get("href"):
            self.resources.append(a["href"])
        if tag == "a" and a.get("href") and "?" in a["href"] and not urllib.parse.urlsplit(a["href"]).netloc:
            self.query_links.append(a["href"])


def schema_types(value):
    found = set()
    if isinstance(value, dict):
        t = value.get("@type", [])
        found.update(t if isinstance(t, list) else [t])
        for child in value.values():
            found.update(schema_types(child))
    elif isinstance(value, list):
        for child in value:
            found.update(schema_types(child))
    return found - {""}


def write_csv(name, rows, columns=None):
    with (OUT / name).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def fetch(origin, route):
    url = origin + route
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={
            "User-Agent": "CrownwingContentAudit/1.0",
        }), timeout=20) as response:
            body = response.read()
            return route, dict(status=response.status, final_url=response.geturl(),
                               x_robots_tag=response.headers.get("X-Robots-Tag", ""),
                               content_type=response.headers.get("Content-Type", ""),
                               body_sha256=hashlib.sha256(body).hexdigest(),
                               body=body.decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as error:
        return route, dict(status=error.code, final_url=error.geturl(),
                           x_robots_tag=error.headers.get("X-Robots-Tag", ""),
                           content_type=error.headers.get("Content-Type", ""), body="")
    except Exception as error:
        return route, dict(status=None, error=str(error), body="")


def md_value(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def markdown_to_html(text):
    """Small renderer for the controlled audit markdown; no external dependencies."""
    lines, output, table = text.splitlines(), [], False
    def inline(value):
        value = html.escape(value)
        value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
        return re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    for line in lines:
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(re.fullmatch(r"[-: ]+", c) for c in cells):
                continue
            if not table:
                output.append('<div class="table-wrap"><table>')
                table = True
            output.append("<tr>" + "".join("<td>" + inline(c) + "</td>" for c in cells) + "</tr>")
            continue
        if table:
            output.append("</table></div>")
            table = False
        if line.startswith("#"):
            n = min(len(line) - len(line.lstrip("#")), 6)
            output.append(f"<h{n}>" + inline(line[n:].strip()) + f"</h{n}>")
        elif line == "---":
            output.append("<hr>")
        elif line.strip():
            output.append("<p>" + inline(line) + "</p>")
    if table:
        output.append("</table></div>")
    return "\n".join(output)


def audit():
    if not os.environ.get("REPLIT_DEV_DOMAIN"):
        raise RuntimeError("A running development preview is required; do not silently substitute source-only evidence.")
    pages, parsed, raw, content = foundation.read_pages()
    routes = sorted(pages)
    if set(routes) != set(DECISIONS):
        raise RuntimeError(f"Classification mismatch: missing={set(routes)-set(DECISIONS)}, extra={set(DECISIONS)-set(routes)}")
    baseline = set(json.loads(BASELINE.read_text())["routes"])
    if len(baseline) != 66 or not baseline <= set(routes):
        raise RuntimeError("Original 66-page cohort cannot be reconciled")
    origin = "https://" + os.environ["REPLIT_DEV_DOMAIN"]
    probes = ["/robots.txt", "/sitemap.xml", "/__classification_missing_page_892c/",
              "/parrots-for-sale/?species=conure&size=small", "/index.html",
              "/guides/index.html", "/parrots-for-sale", "/PARROTS-FOR-SALE/"]
    with ThreadPoolExecutor(max_workers=6) as pool:
        http = dict(pool.map(lambda r: fetch(origin, r), routes + probes))
    graph, links, broken = foundation.internal_graph(parsed, pages)
    inbound, main_in, main_out = defaultdict(set), defaultdict(set), defaultdict(set)
    for source, targets in graph.items():
        for target in targets:
            if source != target:
                inbound[target].add(source)
    for source, href, kind, role in links:
        if kind == "internal" and role == "main":
            target = urllib.parse.urlsplit(urllib.parse.urljoin(source, href)).path
            target = foundation.normal_path(target)
            if source != target:
                main_out[source].add(target)
                main_in[target].add(source)
    depth = {"/": 0}
    queue = deque(["/"])
    while queue:
        source = queue.popleft()
        for target in graph[source]:
            if target not in depth:
                depth[target] = depth[source] + 1
                queue.append(target)
    source_sitemap = ET.fromstring((ROOT / "dist/sitemap.xml").read_text())
    sitemap_urls = [n.text for n in source_sitemap.findall("{*}url/{*}loc")]
    sitemap_set = set(sitemap_urls)
    robots_source = (ROOT / "dist/robots.txt").read_text()
    counts = Counter(d["classification"] for d in DECISIONS.values())
    text, facts, shingles = {}, {}, {}
    title_counter = Counter(tuple(p.title) for p in parsed.values())
    description_counter = Counter(p.meta.get("description", "") for p in parsed.values())
    external_links = sorted({href for p in parsed.values() for href, _ in p.links if href.startswith(("http://", "https://"))})
    image_rows, technical_rows = [], []

    for route in routes:
        cp, markup = ContentParser(), Markup()
        cp.feed(raw[route])
        markup.feed(raw[route])
        text[route] = " ".join(" ".join(cp.body_fragments).split())
        tokens = re.findall(r"\b[\w'-]+\b", text[route].lower())
        shingles[route] = set(zip(*(tokens[i:] for i in range(5))))
        p, d, issues = parsed[route], DECISIONS[route], []
        expected = PUBLIC_ORIGIN + route
        if len(p.title) != 1 or not p.title[0]:
            issues.append("missing or multiple title")
        elif title_counter[tuple(p.title)] > 1:
            issues.append("duplicate title")
        if not p.meta.get("description"):
            issues.append("missing description")
        elif description_counter[p.meta["description"]] > 1:
            issues.append("duplicate description")
        if len(p.h1) != 1:
            issues.append("H1 count is not one")
        if p.canonicals != [expected]:
            issues.append("canonical does not match expected unique route")
        if expected not in sitemap_set:
            issues.append("missing from current sitemap")
        if http[route].get("status") != 200:
            issues.append("live page status is not 200")
        if hashlib.sha256(raw[route].encode()).hexdigest() != http[route].get("body_sha256"):
            issues.append("served body differs from generated HTML")
        missing_og = [key for key in ("og:title", "og:description", "og:image", "og:url") if not p.meta.get(key)]
        if missing_og:
            issues.append("missing Open Graph: " + ", ".join(missing_og))
        if any(b > a + 1 for a, b in zip(markup.headings, markup.headings[1:])):
            issues.append("heading-level jump needs review")
        types = set()
        for value in p.schemas:
            try:
                types.update(schema_types(json.loads(value)))
            except (ValueError, TypeError):
                issues.append("invalid JSON-LD syntax")
        if not p.schemas:
            issues.append("no JSON-LD")
        for src in markup.resources:
            target, _ = foundation.local_target(content[route]["source_file"], src)
            if target is not None and not target.is_file():
                issues.append("missing local resource: " + src)
        for image in markup.images:
            meaningful = bool(image.get("alt", "").strip())
            findings = []
            if "alt" not in image:
                findings.append("missing alt")
            if meaningful and (not image.get("width") or not image.get("height")):
                findings.append("meaningful image missing dimensions")
            if meaningful and not image.get("srcset") and not "logo" in image.get("class", "") and not "brand" in image.get("class", ""):
                findings.append("review responsive source")
            if image.get("fetchpriority") == "high" and image.get("loading") == "lazy":
                findings.append("priority/lazy conflict")
            target, _ = foundation.local_target(content[route]["source_file"], image.get("src", ""))
            size = target.stat().st_size if target and target.is_file() else None
            if meaningful and size and size > 500000:
                findings.append("source over 500kB; assess selected responsive variant")
            image_rows.append({
                "URL": expected, "Source": image.get("src", ""), "Alt": image.get("alt", "<missing>"),
                "Role": "meaningful" if meaningful else "decorative/repeated label; verify context",
                "Width": image.get("width", ""), "Height": image.get("height", ""),
                "Srcset": image.get("srcset", ""), "Loading": image.get("loading", "browser default"),
                "Fetch priority": image.get("fetchpriority", "auto"),
                "Source bytes": size or "", "Findings": "; ".join(findings) or "No mechanical finding; identity/stock not inferred",
            })
            if "missing alt" in findings:
                issues.append("image missing alt")
        source_indexable = not bool(re.search(r"\bnoindex\b", p.meta.get("robots", ""), re.I))
        facts[route] = dict(
            url=expected, cohort="Original 66" if route in baseline else "Later buyer-library addition",
            title=" | ".join(p.title), h1=" | ".join(p.h1), words=len(tokens),
            description=p.meta.get("description", ""), meta_robots=p.meta.get("robots", "default index/follow"),
            source_indexable=source_indexable, canonical="; ".join(p.canonicals),
            schema=sorted(types), images=len(markup.images), internal_in=len(inbound[route]),
            internal_out=len(graph[route]), main_in=len(main_in[route]), main_out=len(main_out[route]),
            depth=depth.get(route), issues=issues, query_links=markup.query_links,
            html_sha256=hashlib.sha256(raw[route].encode()).hexdigest(),
            body_sha256=hashlib.sha256(text[route].encode()).hexdigest(),
            headings=content[route]["headings"], paragraph_excerpt=content[route]["paragraphs"][1:4],
        )
        technical_rows.append({
            "URL": expected, "Status": http[route].get("status"), "Canonical": facts[route]["canonical"],
            "Meta robots": facts[route]["meta_robots"], "Preview X-Robots-Tag": http[route].get("x_robots_tag", ""),
            "Sitemap included": expected in sitemap_set, "Description": facts[route]["description"],
            "H1 count": len(p.h1), "Heading sequence": ",".join(map(str, markup.headings)),
            "Open Graph": "Complete" if not missing_og else ";".join(missing_og),
            "Schema": "; ".join(sorted(types)), "HTML bytes": pages[route].stat().st_size,
            "Viewport": p.meta.get("viewport", ""), "Source findings": "; ".join(issues) or "None",
            "Important content": "Present in response HTML; no client-side route needed",
            "Mobile": "See all-route live browser evidence", "Field CWV": "Not available",
        })
    similarities = []
    max_sim = {r: (0, "") for r in routes}
    for a, b in itertools.combinations(routes, 2):
        denominator = min(len(shingles[a]), len(shingles[b]))
        score = len(shingles[a] & shingles[b]) / denominator if denominator else 0
        similarities.append({"URL A": PUBLIC_ORIGIN+a, "URL B": PUBLIC_ORIGIN+b,
                             "Five-word containment": round(score, 5),
                             "Automated review flag": score >= .65})
        for route, other in ((a, b), (b, a)):
            if score > max_sim[route][0]:
                max_sim[route] = score, other
    similarities.sort(key=lambda pair: pair["Five-word containment"], reverse=True)
    write_csv("crownwing-content-similarity.csv", similarities)
    write_csv("crownwing-technical-audit.csv", technical_rows)
    write_csv("crownwing-image-audit.csv", image_rows)
    groups = defaultdict(list)
    for route, d in DECISIONS.items():
        if d["classification"] == "C":
            groups[d["target"]].append(route)
    inventory = []
    for route in routes:
        f, d = facts[route], DECISIONS[route]
        overlap = "; ".join(groups.get(route, []))
        if d["classification"] == "C":
            overlap = d["target"] + "; " + "; ".join(r for r in groups[d["target"]] if r != route)
        inventory.append({
            "URL": f["url"], "Page title": f["title"], "H1": f["h1"], "Page type": d["page_type"],
            "Word count": f["words"],
            "Indexable?": ("YES in source" if f["source_indexable"] else "NO in source") +
                "; preview header=" + (http[route].get("x_robots_tag") or "none observed") + "; Google index UNKNOWN",
            "Canonical URL": f["canonical"], "Status code": http[route].get("status"),
            "Primary topic": d["keyword"], "Search intent": d["intent"], "Primary keyword": d["keyword"],
            "Secondary keywords": d["secondary"], "Internal links in": f["internal_in"],
            "Internal links out": f["internal_out"], "Duplicate/similar pages": overlap or "No verified same-intent merge; see all-pairs metrics",
            "Schema types": "; ".join(f["schema"]), "Image count": f["images"],
            "Content uniqueness": f"Max five-word containment {max_sim[route][0]:.3f} with {max_sim[route][1]}; lexical metric is not intent judgment",
            "Recommended action": d["classification"] + " — " + d["action"], "Priority": d["priority"],
            "Classification": d["classification"], "Cohort": f["cohort"],
            "Contextual inbound sources": f["main_in"], "Contextual outbound targets": f["main_out"],
            "Minimum clicks from home": f["depth"], "Body fingerprint": f["body_sha256"],
        })
    write_csv("crownwing-66-page-inventory.csv", inventory)
    keyword_rows = []
    for route in routes:
        d = DECISIONS[route]
        keyword_rows.append({
            "Keyword": d["keyword"], "Intent": d["intent"], "Target URL": PUBLIC_ORIGIN+d["target"],
            "Current URL": PUBLIC_ORIGIN+route, "Page classification": d["classification"],
            "Search demand": "Not measured", "Competition": "Not measured", "Priority": d["priority"],
            "Notes": ("Merge-source intent; target owns this topic after approval. " if d["classification"] == "C" else "") +
                "Intent-based editorial mapping; web examples do not prove volume or ranking. " +
                ("Exact offered-species scope requires owner confirmation." if route.count("/") == 4 and route.startswith("/parrots/") else ""),
            "Keyword role": "Primary", "Current ranking": "Unknown — no Search Console/rank-tracking access",
        })
    commercial = "/parrots-for-sale/"
    extra_keywords = [
        ("parrot for sale UK", commercial, "Transactional enquiry", "Variant of the national commercial intent."),
        ("buy a parrot UK", commercial, "Transactional enquiry", "Commercial purchase intent; how-to intent goes to the separate buying guide."),
        ("parrots for sale", commercial, "Transactional enquiry", "UK-scoped national hub; not another URL."),
        ("pet parrots", commercial, "Commercial investigation", "Commercial modifier only; research discovery can use /parrots/."),
        ("parrots UK", commercial, "Commercial investigation", "Broad phrase; no keyword stuffing or claim of exclusive intent."),
        ("talking parrot for sale UK", "/parrots-for-sale/talking-parrots/", "Commercial investigation", "Potential speech is never a guarantee or a verified individual listing."),
        ("tame parrots", commercial, "Commercial investigation", "Background/handling enquiry only; no blanket tameness claim."),
        ("hand reared parrots", commercial, "Commercial investigation", "Individual rearing/weaning questions; do not claim all stock is hand-reared."),
        ("baby parrots", commercial, "Commercial investigation", "Known age/weaning questions only; no invented baby stock or age-specific landing page."),
        ("African Grey Parrot UK", "/parrots/african-parrots/", "Commercial investigation / informational", "Research overview; explicit for-sale modifier belongs to its separate commercial route."),
        ("African Grey Parrot for sale UK", "/parrots-for-sale/african-grey-parrots/", "Transactional enquiry", "Confirmed offered group; not proof of an exact individual."),
        ("macaw for sale UK", "/parrots-for-sale/macaws/", "Transactional enquiry", "Map singular query to existing macaw commercial category."),
        ("cockatoo for sale UK", "/parrots-for-sale/cockatoos/", "Transactional enquiry", "Use existing offered-group category."),
        ("Amazon Parrot UK", "/parrots/amazons/", "Commercial investigation / informational", "Research overview; for-sale variant belongs to its commercial category."),
        ("conure for sale UK", "/parrots-for-sale/conures/", "Transactional enquiry", "Use existing offered-group category."),
        ("Eclectus Parrot UK", "/parrots/eclectus/", "Commercial investigation / informational", "Research overview; exact taxonomy and individual must be checked."),
        ("cockatiel for sale UK", "/parrots-for-sale/cockatoos/", "Transactional enquiry", "CONDITIONAL: logical group enquiry, not a confirmed Crownwing cockatiel offer. Owner must confirm before active targeting; no new page."),
        ("how much does a parrot cost UK", "/parrot-prices-uk/", "Commercial investigation", "Purchase-price reading; lifetime/recurring-cost reading belongs to the ownership-cost guide."),
        ("best parrot for first time owner", "/guides/choosing-a-parrot/", "Commercial investigation", "Compare needs, not an unsupported best/easiest ranking."),
        ("are parrots good pets", "/guides/choosing-a-parrot/", "Informational", "Household suitability, noise/time and long-term responsibility."),
        ("how long do parrots live", "/parrots/", "Informational", "Existing hub leads to specific lifespans; do not give one number for all parrots."),
        ("how much does it cost to keep a parrot", "/guides/parrot-ownership-costs/", "Informational", "Recurring, setup and uncertain costs; not purchase price."),
        ("parrot care", "/parrot-care/", "Informational discovery", "Focused directory leading to substantive care guides."),
        ("parrot toys", "/guides/parrot-housing-enrichment/", "Informational", "Enrichment/safety intent only; Crownwing does not claim to sell accessories."),
        ("parrot training", "/guides/choosing-a-parrot/", "Informational", "Partial coverage through group/species profiles and reward-based handling; genuine content gap, not proof of a complete training manual."),
        ("parrot behaviour", "/guides/choosing-a-parrot/", "Informational", "Comparison and individual observations; partial coverage, not a specialist behaviour service."),
        ("parrot socialisation", "/guides/preparing-for-a-parrot/", "Informational", "Settling-in and supervised boundaries; deepen the existing resource before a new URL."),
        ("parrot documentation UK", "/guides/cites-parrots-uk/", "Regulatory/legal", "Scientific identification, transaction and jurisdiction-specific checks."),
        ("parrot import UK", "/guides/cites-parrots-uk/", "Regulatory/legal", "Border-check introduction and official links, not an import service or complete permitting manual."),
        ("parrot registration UK", "/guides/cites-parrots-uk/", "Regulatory/legal", "Distinguish CITES from bird-keeper registration and housing exemptions."),
        ("bird keeper registration UK", "/guides/cites-parrots-uk/", "Regulatory/legal", "England/Wales, Scotland and NI sources; no single UK-wide rule."),
    ]
    for keyword, target, intent, notes in extra_keywords:
        keyword_rows.append({
            "Keyword": keyword, "Intent": intent, "Target URL": PUBLIC_ORIGIN+target,
            "Current URL": PUBLIC_ORIGIN+target, "Page classification": DECISIONS[target]["classification"],
            "Search demand": "Not measured", "Competition": "Not measured", "Priority": "HIGH" if "sale" in keyword else "MEDIUM",
            "Notes": notes, "Keyword role": "Secondary / intent variant",
            "Current ranking": "Unknown — no Search Console/rank-tracking access",
        })
    write_csv("crownwing-keyword-map.csv", keyword_rows)
    index_rows = [{
        "URL": facts[r]["url"], "Current source state": "INDEX" if facts[r]["source_indexable"] else "NOINDEX",
        "Recommended state": "REDIRECT" if DECISIONS[r]["classification"] == "C" else "INDEX",
        "Target": PUBLIC_ORIGIN+DECISIONS[r]["target"], "Classification": DECISIONS[r]["classification"],
        "Reason": DECISIONS[r]["reason"], "Implementation state": "Recommendation only; no source/indexation changes",
        "Google index": "Unknown", "Preview header": http[r].get("x_robots_tag", ""),
    } for r in routes]
    write_csv("crownwing-indexation-matrix.csv", index_rows)

    # Reports deliberately distinguish observed facts from the proposed smaller architecture.
    mobile = json.loads((OUT / "crownwing-mobile-rendering.json").read_text())
    mobile_by_route = {p["route"]: p for p in mobile["pages"]}
    mobile_problems = [p for p in mobile["pages"] if p.get("error") or p.get("status") != 200 or p.get("overflow")
                       or len(p.get("h1", [])) != 1 or not p.get("menuOpens") or p.get("pageErrors")]
    if set(mobile_by_route) != set(routes):
        raise RuntimeError("Mobile audit does not cover the exact current route set")
    source_problem_pages = [r for r, f in facts.items() if f["issues"]]
    proxy_blocked = [r for r in routes if "noindex" in http[r].get("x_robots_tag", "").lower()]
    orphan = [r for r in routes if r != "/" and not inbound[r]]
    unreachable = [r for r in routes if r not in depth]
    near_duplicates = [p for p in similarities if p["Automated review flag"]]
    cohort_counts = {name: dict(Counter(DECISIONS[r]["classification"] for r in cohort)) for name, cohort in [
        ("Original 66", baseline), ("Later 3", set(routes)-baseline)]}
    summary = dict(audited_at=datetime.now(timezone.utc).isoformat(), counts=dict(counts),
                   cohort_counts=cohort_counts, routes=len(routes), current_source_indexable=sum(f["source_indexable"] for f in facts.values()),
                   proposed_indexable=len(routes)-counts["C"], semantic_incomplete_pages=7,
                   species_expansion_pages=16, semantic_overlap_groups=len(groups), lexical_flags=len(near_duplicates),
                   orphan_pages=orphan, unreachable_pages=unreachable, broken_local_links=broken,
                   source_problem_pages=source_problem_pages, mobile_problem_pages=mobile_problems,
                   preview_noindex_pages=len(proxy_blocked), google_index="Unknown")
    snapshot = dict(summary=summary, pages={r: dict(**facts[r], editorial=DECISIONS[r]) for r in routes},
                    http={r: {k:v for k,v in value.items() if k != "body"} for r,value in http.items()},
                    probe_bodies={r: http[r].get("body", "")[:1500] for r in ("/robots.txt", "/sitemap.xml")},
                    limits="No verified published-host crawl, Search Console, numeric keyword demand/difficulty, backlink history, field INP/CWV or expert legal/veterinary review.")
    (OUT / "crownwing-classification-before.json").write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n")
    dashboard = f"""# Crownwing Parrots — complete page classification

Audit date: {summary['audited_at']}. Recommendations, not an implementation log.

Total pages audited: **69** — all **66 original URLs** plus **3 previously added buyer-library URLs**. The filename requested in the brief is retained; no page is omitted to force a total of 66.

| Classification | Original 66 | Later 3 | Current total |
|---|---:|---:|---:|
"""
    for label, name in [("A", "Keep & strengthen"), ("B", "Expand"), ("C", "Merge"), ("D", "Noindex/remove"), ("E", "Redirect")]:
        dashboard += f"| {label} — {name} | {cohort_counts['Original 66'].get(label,0)} | {cohort_counts['Later 3'].get(label,0)} | {counts.get(label,0)} |\n"
    dashboard += f"""
## Summary dashboard

- Thin/incomplete standalone task coverage: **7** pages. Additional **16** species profiles need evidence and species-specific practical depth; they are not condemned merely for their length.
- Local independent-value flags: **13** sources proposed for consolidation (12 Great Britain city guides and their directory).
- Duplicate/overlapping-intent groups: **{len(groups)} editorial groups**; automated five-word-containment flags at 0.65: **{len(near_duplicates)}**. Suspected intent overlap is not proven Google ranking cannibalisation.
- Orphan pages: **{len(orphan)}**; unreachable from home: **{len(unreachable)}**.
- Broken local file/fragment links: **{len(broken)}**; external content fetches are separately recorded, not silently counted as HTTP-200 links.
- Missing titles: **{sum(not p.title for p in parsed.values())}**; duplicate title groups: **{sum(n > 1 for n in title_counter.values())}**.
- Missing descriptions: **{sum(not p.meta.get('description') for p in parsed.values())}**; duplicate description groups: **{sum(n > 1 for value,n in description_counter.items() if value)}**.
- Canonical source problems: **{sum(f['canonical'] != f['url'] for f in facts.values())}**.
- JSON-LD syntax failures: **{sum('invalid JSON-LD syntax' in f['issues'] for f in facts.values())}**. Appropriate-type and visible-claim review does not imply Google rich-result validation.
- Current sitemap mismatches: **{len(sitemap_set ^ {PUBLIC_ORIGIN+r for r in routes})}**; duplicate sitemap entries: **{len(sitemap_urls)-len(sitemap_set)}**.
- Source robots/index blockers: **{sum(not f['source_indexable'] for f in facts.values())} meta-noindex pages**. Separate environment issue: preview `X-Robots-Tag: noindex` affects **{len(proxy_blocked)}** audited URLs; production headers/indexing are unknown.
- Other mechanical source-findings pages: **{len(source_problem_pages)}**; all-route mobile rendering/navigation problems at 390px: **{len(mobile_problems)}**.

Current source policy includes 69 URLs. If the 13 recommended merges are approved and correctly served as permanent redirects, the result is **56 canonical indexable pages** (53 original survivors plus 3 later resources), not 69. D/E have zero primary page assignments because this crawl found no obsolete individual listings or useless utility landing pages. C sources ultimately redirect; they are classified C exactly once, not counted again as E.

## Scope and evidence limits

All routes are static HTML. There are no dynamic individual-bird/product pages, sold-bird archives, search routes or generated query/filter pages. Comparison selections and budget inputs are local tools, not additional landing pages. The probe query returns the same commercial-page body and base canonical. `/index.html` and trailing-slash variants are aliases, not extra pages; case variants return 404 rather than inventing a second page.

Each real URL has a separate editorial decision below. Metrics supplement, rather than replace, intent and usefulness judgments. Inventory word counts include substantive headings, lists and tables, excluding shared chrome and repeated CTA/form blocks. Similarity uses five-word containment over those substantive tokens and all 2,346 page pairs.

Public UK-worded web searches were performed and raw results saved. They support a qualitative intent map, not measured volume, keyword difficulty, UK-localised Google positions or Crownwing rankings. No competitor prices, services or credentials are adopted as Crownwing facts.

Eight offered groups are owner-confirmed. The exact 16 named species, current individual stock, prices, ages, rearing and transport are not confirmed by a photograph. Species-profile retention as an actual offered-species commercial target requires that owner check. Until then, profiles remain clearly educational; no stock/Product schema is manufactured.

The real national hub is `/parrots-for-sale/`. The example `/parrots-for-sale-uk/` does not require a second near-duplicate page or gratuitous migration. Keep care, purchase enquiries, purchase quotes, ownership costs, and documentation as distinct reader tasks.

Published-host crawl/indexing, backlink history, Search Console and field CWV remain unverified. Existing lab evidence is specific to the choosing guide: mobile performance 87 / LCP 2.9s / CLS 0 / TBT 0; desktop 99 / LCP 0.8s / CLS 0.011. It is not an all-page performance or INP measurement. Accessibility/best-practices scores of 100 apply to that tested page, not every route.

Source artifact hashes, live HTTP observations, all-route mobile checks, external source extracts, image details and every pairwise similarity score are in the companion evidence files. `crownwing-implementation-plan.md` is the next-stage plan. No page was deleted, merged, redirected or visually redesigned during this audit.

---
"""
    sections = [dashboard]
    for number, route in enumerate(routes, 1):
        f, d = facts[route], DECISIONS[route]
        duplication = ("Same reader task as " + d["target"] + "; see semantic group, not a claim of exact-copy text."
                       if d["classification"] == "C" else
                       ("Receives proposed useful material from " + ", ".join(groups[route]) + "; preserve its dominant intent."
                        if route in groups else
                        "No same-intent merge justified. Shared layout/group names do not prove duplication; lexical maximum " +
                        f"{max_sim[route][0]:.3f} with {max_sim[route][1]}."))
        linking = f"{f['internal_in']} distinct inbound page sources; {f['main_in']} contextual inbound sources; {f['main_out']} contextual targets; home depth {f['depth']}. "
        linking += ("After approval, remove links to this retiring source and link directly to its appropriate destination/contact."
                    if d["classification"] == "C" else
                    "Ensure useful reader-next-step links, especially buying checklist, care, costs and documentation; do not inflate the footer.")
        technical = ("; ".join(f["issues"]) if f["issues"] else "No mechanical source failure observed: HTTP 200, unique metadata, route-specific canonical and sitemap inclusion.")
        technical += f" Mobile H1/navigation/containment checked at 390px; {len(mobile_by_route[route].get('pageErrors', []))} page errors. Preview noindex is external; production index and per-route field CWV unknown."
        quality = ("Useful but incomplete: " + d["weakness"] if d["classification"] == "B" else
                   "Useful advice lacks independent location-search justification." if d["classification"] == "C" else
                   "Useful for the stated page role; strengthen evidence and pathways without word-count padding.")
        sections.append(f"""## {number:02d} — {f['url']}

**Classification:** {d['classification']}

**Page type:**  
{d['page_type']}

**Primary intent:**  
{d['intent']}

**Primary keyword:**  
{d['keyword']}

**Secondary topics:**  
{d['secondary']}

**Current strengths:**  
{d['strength']}

**Current weaknesses:**  
{d['weakness']}

**Content quality:**  
{quality} Substantive word count: {f['words']}; cohort: {f['cohort']}.

**Search opportunity:**  
Serve the stated {d['intent'].lower()} need through the mapped topic; demand/competition/ranking are unmeasured, not assigned invented scores.

**Duplicate/cannibalisation issues:**  
{duplication}

**Internal-link issues:**  
{linking}

**Technical SEO issues:**  
{technical}

**Recommended action:**  
{d['action']}

**Priority:** {d['priority']}

**Reason:**  
{d['reason']}

---
""")
    classification = "\n".join(sections)
    (OUT / "crownwing-page-classification.md").write_text(classification)
    thin = ["# Thin/incomplete content review\n",
            "This is an intent/usefulness review, not a minimum-word-count rule. No automatic expansion or deletion.\n",
            "Seven incomplete standalone-task pages, sixteen species-depth/evidence gaps and thirteen local independent-value flags are distinguished below. The contact and care hubs are legitimate short-purpose exceptions.\n"]
    for route in routes:
        d = DECISIONS[route]
        if d["classification"] not in {"B", "C"}:
            continue
        thin.append(f"## {route}\n\nClassification: **{d['classification']}**. Substantive words: {facts[route]['words']}.\n\n"
                    f"**Why flagged:** {d['weakness']}\n\n**What is missing:** Independent city-specific value, not just longer prose.\n\n"
                    f"**How to improve:** {d['action']}\n" if d["classification"] == "C" else
                    f"## {route}\n\nClassification: **B**. Substantive words: {facts[route]['words']}.\n\n"
                    f"**Why flagged / what is missing:** {d['weakness']}\n\n**How to improve:** {d['action']}\n")
    thin.append("## Short-purpose exceptions\n\n/contact/: direct contact/support and truthful download-only form; keep.\n\n"
                "/parrot-care/: focused resource navigation; keep. Neither needs generic filler to pass a numeric threshold.\n\n"
                "No evidence establishes AI authorship. Repeated structure alone is not a detector of AI content; no such accusation is made.\n")
    (OUT / "thin-content-report.md").write_text("\n".join(thin))
    duplicate = [f"# Duplicate and overlapping-intent review\n\nCompared every pair: **{len(similarities)}**. "
                 f"Five-word containment ≥0.65 flags: **{len(near_duplicates)}**. Boilerplate/chrome excluded. "
                 "Containment is |shared shingles| / min(|A|,|B|); it is directional-content containment, not a semantic confidence score.\n\n"
                 f"There are **{len(groups)} manually assessed overlapping-reader-task groups**. These are not claims of proven Google cannibalisation or exact duplicated prose.\n"]
    for target, sources in sorted(groups.items()):
        duplicate.append("## Group: " + target + "\n\n**Keep:** " + target +
                         " (current classification " + DECISIONS[target]["classification"] + ").\n\n**Merge sources:** " +
                         ", ".join(sources) + ".\n\n**Why:** The sources' useful household/planning tasks belong in this stronger topical resource; a city label does not provide an independent service or local evidence.\n\n"
                         "**Action:** Combine genuinely useful detail, omit repetition, update contextual links, preserve enquiry access through contact, and use single-hop 301s only after approval and production-host configuration. Do not redirect without first preserving useful material.\n")
    duplicate.append("## Reviewed and not merged\n\n"
                     "- Eight commercial group pages versus eight educational group pages: buying versus care/research intent.\n"
                     "- Sixteen individual species profiles: shared headings, but distinct anatomy/identity and meaningful species differences; B for evidence/practical depth, not species-name-swap removal.\n"
                     "- Price versus ongoing ownership costs: purchase quote versus lifetime budget.\n"
                     "- National commercial hub versus branded availability directory: national buying journey versus offered-group/current-details enquiry.\n"
                     "- Buying cornerstone versus checklist versus preparation: full process, recordable seller questions, and home-readiness tasks. Strengthen those differences.\n"
                     "- Belfast: Northern Ireland movement/authority checks provide a real differentiator, but the existing source coverage needs expansion.\n"
                     "- No genuine product/individual-bird pages or duplicated sold listings found.\n\n"
                     "The lexical shortlist below is a review aid, not an automatic merge list. Every metric is in crownwing-content-similarity.csv.\n\n"
                     "| URL A | URL B | Containment |\n|---|---|---|\n")
    for pair in similarities[:15]:
        duplicate.append(f"| {pair['URL A']} | {pair['URL B']} | {pair['Five-word containment']:.3f} |")
    (OUT / "duplicate-content-report.md").write_text("\n".join(duplicate))
    linking = f"""# Internal-linking audit and implementation plan

Current source graph: {len(routes)} pages; {len(orphan)} non-home orphans; {len(unreachable)} unreachable; {len(broken)} broken file/fragment links. Counts in the inventory are distinct referring/target pages, not repeated link occurrences. Contextual counts exclude header/nav/footer/aside. Current page depth is separately recorded.

## Desired roles and pathways

- Homepage → existing /parrots-for-sale/ national hub → eight group buying categories → clearly educational group/species information.
- Educational group/species pages → choosing comparison, relevant diet/housing/preparation, ongoing costs and documentation.
- National hub and group buying pages → buying cornerstone, seller checklist, purchase quotes, confirmed business policies and contact.
- /guides/ → all buyer/care/regulatory resources; /parrot-care/ remains a focused care entry.
- Ownership budget → purchase quote guidance and backup-care preparation; no arbitrary cross-links to unrelated birds.
- Documentation guide → official authorities and Belfast/NI movement aid, with jurisdiction-sensitive anchor wording.
- Every download-only enquiry path → visible instructions to send manually; never imply a backend submission.

## Priority contextual additions

"""
    for route in routes:
        d, f = DECISIONS[route], facts[route]
        if d["classification"] == "C":
            linking += f"- {route} → {d['target']}: update all internal references after approval; keep contact and preserve useful content before retirement.\n"
        elif d["page_type"] in {"Commercial", "Species"}:
            linking += f"- {route}: {f['main_in']} main-content inbound sources. Link at the relevant question to seller checklist, exact care group, costs and CITES checks, rather than relying on footer links.\n"
    linking += """
## Footer and discovery

Keep branding, contact and all confirmed policy links. Footer links are not a replacement for topic-context links. Do not add every species/city to the footer. After approved merges remove the regional directory navigation and link directly to the appropriate buyer resources plus the NI aid; do not label generic guides as local branches.

## Verification after implementation

Recompute reachability, unique contextual in/out counts, missing fragments and source/HTTP statuses. Internal links should go directly to surviving canonical URLs, not through retirement redirects. Preserve existing responsive menu and no-JS readability.
"""
    (OUT / "internal-linking-plan.md").write_text(linking)
    matrix = "# Proposed indexation matrix\n\nRecommendations only. Current source includes 69 pages; actual Google indexing is unknown. Preview noindex headers are not application meta policy. Do not block retired/noindex URLs in robots.txt before crawlers can see their directive/status.\n\n| URL | Index? | Reason |\n|---|---|---|\n"
    for row in index_rows:
        matrix += f"| {row['URL']} | {row['Recommended state']} | {md_value(row['Reason'])} |\n"
    matrix += "\nIf approved, sitemap contains only the 56 surviving canonical INDEX URLs; sources returning 301 are excluded. Keep current sitemap until actual redirects are supported and served.\n"
    (OUT / "crownwing-indexation-matrix.md").write_text(matrix)
    technical = f"""# Technical SEO and experience evidence

## Coverage

- All {len(routes)} canonical routes crawled through the running HTTPS preview; HTTP 200 count {sum(http[r].get('status') == 200 for r in routes)}.
- Every route rendered at 390×900 with JavaScript, live H1/canonical/link checks, overflow containment and mobile-menu opening; observed failures {len(mobile_problems)}.
- Every source checked for metadata, headings, assets, image attributes, schema syntax/types and sitemap inclusion.
- No client-side route shell; meaningful main content and normal href links are in response HTML.
- Current generated HTML and served body hashes compared, including all 69 pages.
- Query probe is identical to the canonical commercial response: {http['/parrots-for-sale/?species=conure&size=small'].get('body_sha256') == http['/parrots-for-sale/'].get('body_sha256')}.
- A nonexistent route returns {http['/__classification_missing_page_892c/'].get('status')}; uppercase probe returns {http['/PARROTS-FOR-SALE/'].get('status')}.
- Existing index-document/slash aliases resolve to canonical routes; source tests cover combined www/HTTPS/path handling. No published-host www/DNS/redirect assertion is made.

## Indexing and sitemap

Source robots content:

{robots_source.strip()}

The actual preview robots response starts with: {http['/robots.txt'].get('body','')[:100]!r}. Sitemap response content type: {http['/sitemap.xml'].get('content_type')}. Source sitemap has {len(sitemap_urls)} entries; {len(sitemap_set ^ {PUBLIC_ORIGIN+r for r in routes})} current route mismatches.

Development-proxy noindex affects {len(proxy_blocked)} routes. Do not change truthful canonicals or application policy to raise a preview Lighthouse SEO score. Published-host headers and Search Console need a separate check.

## Structured data

Recursive @graph/type extraction is used; graph containers are not falsely reported as unknown schema. JSON syntax is checked. Organization/WebSite, WebPage/CollectionPage, BreadcrumbList and Article types should match visible roles. No Product/Offer/Review/AggregateRating is justified by educational photos or group-by-enquiry pages. Publication/expert-review dates and reviewers remain unknown unless genuinely supported; no requirement is solved by fabricating them.

## Images and external references

Every source image occurrence is in crownwing-image-audit.csv, including alt role, dimensions, source bytes, responsive sources and loading/priority. Decorative labelled thumbnails and branding are treated differently from meaningful bird photos. Filename/alt correctness and ambiguous mutation/hybrid identities require owner/editorial verification; a present alt is not proof of exact species or current stock. Compression analysis uses source bytes, not full browser transfer size.

All 20 distinct external href references returned readable content through webFetch and are saved in crownwing-external-source-checks.json. This is not a raw HTTP-status claim or legal/veterinary endorsement. SpeciesPlus requires interactive species-specific lookup. Older Eclectus roratus references can refer to a broader pre-split complex: do not present them as Papuan-specific taxonomy evidence. External information and rules can change.

## Page speed, accessibility and limits

Existing choosing-guide Lighthouse results remain applicable because public pages were not changed: mobile 87 / LCP 2.9s / CLS 0 / TBT 0; desktop 99 / LCP 0.8s / CLS 0.011. Mobile LCP is above the 2.5s good threshold in that lab run. Investigate font/image resource timing on representative homepage, commercial, image-heavy species and legal templates before claiming site-wide performance.

No field CWV/INP, production CrUX, complete route-by-route Lighthouse run, screen-reader audit or WCAG conformance claim. All-page mobile structural/navigation checks are broader than the previous two-tool tests, but do not cover every gallery/form interaction. Existing buyer-tools-browser.json covers desktop/mobile comparison and budget interactions plus no-JS safeguards.

## Mechanical source findings

"""
    technical += ("\n".join("- " + r + ": " + "; ".join(facts[r]["issues"]) for r in source_problem_pages) or "None observed.")
    (OUT / "crownwing-technical-audit.md").write_text(technical)
    plan = f"""# Audit-led implementation plan

Audit and classification completed before public changes. This plan is separate from approval and from an implementation log.

## 1. Safe strengthening of A pages

Retain URLs, brand, logo/favicon, nature-led H1 and existing visual design. Keep /parrots-for-sale/ as the strong national commercial hub rather than manufacturing /parrots-for-sale-uk/. Improve contextual buying/policy/documentation links and an accurate offered-groups availability title. Preserve care/buying and purchase/ownership-cost intent boundaries.

## 2. Substantive B expansion

Expand the four practical guides as task-based checklists/examples, not word-count padding. Develop purchase-quote comparison without fictitious prices. Strengthen the NI movement aid with verified DAERA/APHA references and the documentation cornerstone. About/process needs owner-confirmed first-party facts.

Each of the 16 species profiles has a specific expansion brief in the classification report. Source-check taxonomy and numeric claims and add useful species-dependent home/routine tasks. Owner must first confirm these exact species are in Crownwing's intended offered range; an educational image is not stock evidence. Do not solve the gap with fabricated author credentials, prices, rearing, certificates or experiences.

## 3. Proposed C consolidation — owner decision needed

Retire 12 generic Great Britain city search pages plus their directory. Preserve useful topic sections in the strongest existing guides, maintain enquiry access through /contact/, and retain the distinct Belfast/NI aid with tighter source-backed scope.

**Consequence:** 13 existing URLs cease to be standalone landing pages, and their separate city-labelled download forms are replaced by the shared enquiry path. Saved URLs/backlinks should resolve directly to relevant guides through permanent 301s. No buyer records are deleted: these forms do not store records. Without Search Console/backlink data, historical traffic/value cannot be verified.

**Hosting gate:** Current instructions publish dist as static files; the Python server's preview-only redirects do not automatically exist on a static published host. Before any retirement, select and verify a production-supported redirect mechanism or supported server-hosted setup. Do not silently substitute JavaScript/meta-refresh for requested HTTP 301s, and do not delete old HTML before correct production handling exists.

| Source | Strongest destination |
|---|---|
"""
    for r in routes:
        if DECISIONS[r]["classification"] == "C":
            plan += f"| {r} | {DECISIONS[r]['target']} |\n"
    plan += f"""
## 4. D/E and technical clean-up

No primary D/E page recommendations in this evidence set; do not manufacture removals. Existing path aliases are separately handled, not counted as extra classified pages. After approved C implementation, remove all 13 redirect sources from sitemap, update internal links directly, and verify single-hop status/Location and no chains/loops. Remaining proposed indexable count: {len(routes)-counts['C']}.

Do not use robots disallow as noindex. Keep policy/contact pages as useful trust/support routes. No new pages to fill architecture quotas.

## 5. Verification and manual gates

- Run complete generated-site tests, metadata/schema/image/link checks and all-route mobile audit after changes.
- Confirm clean HTTPS/non-www/path aliases on the real published host; check source headers and sitemap there.
- Verify schema with official tools without assuming rich-result eligibility.
- Connect owner-authorised Search Console to check impressions, queries, indexed/excluded pages and backlink/history signals; no rankings are invented.
- Remeasure representative image-heavy templates; get field CWV once real traffic exists.
- Owner checks exact offered-species scope, prices, identity/care practices, and viewing/handover/aftercare commitments.
- Legal/veterinary expert review remains distinct from editorial source retrieval.

## Exact current implementation status

Created private audit inventories, classifications, keyword map, similarity/image/technical evidence, indexation matrix and this implementation plan. Added repeatable read-only audit helpers. **No public HTML, visual design, URL, meta-indexation, sitemap or serving policy has changed during the audit.** Proposed C changes are not represented as completed; owner approval and a verified published-host redirect method are required.
"""
    (OUT / "crownwing-implementation-plan.md").write_text(plan)
    (OUT / "crownwing-implementation-summary.md").write_text(
        "# Current implementation summary\n\nAudit/report phase completed. No public-site content or URL-policy changes applied.\n\n"
        "Changed: added complete 69-page inventory (original 66 + later 3), per-page classifications, intent-based keyword map, "
        "all-pairs similarity metrics, thin/overlap/linking reports, source/image/HTTP/mobile evidence, proposed indexation matrix and implementation plan.\n\n"
        "Manual/approval gates: 13 recommended city/directory merges and production-supported 301s; exact 16-species offered-range confirmation; "
        "business identity/practices and price facts; production/GSC/backlink and field-CWV access; professional legal/veterinary review.\n")
    research = json.loads((OUT / "crownwing-keyword-research-evidence.json").read_text())
    research_md = ["# UK keyword research evidence and limits\n",
                   "Current public web searches with UK-worded queries, not UK-geolocated Google rank tracking. Numeric volume, difficulty/competition and Crownwing rankings are unavailable and labelled unmeasured/unknown in the map.\n",
                   "Marketplace results support commercial enquiry intent; UK retailer/welfare guides support choosing/cost/care questions; GOV.UK/DAERA support jurisdiction-sensitive documentation topics. Some returned pages are irrelevant or questionable: they are not evidence of Crownwing stock, prices or services, and no competitor price is copied.\n"]
    for i, result in enumerate(research["results"], 1):
        research_md.append(f"## Search evidence set {i}\n")
        for page in result.get("resultPages", []):
            research_md.append(f"- {page['title']}: {page['url']}\n")
    research_md.append("## Mapping gaps\n\nCockatiel offer not confirmed: logical group enquiry only, no new page. Training/behaviour/socialisation have partial coverage, so deepen relevant existing resources before a dedicated page. Broad search wording can have mixed intents; mappings are editorial recommendations, not ranking predictions.\n")
    (OUT / "crownwing-keyword-research.md").write_text("\n".join(research_md))
    report_sections = [classification, plan, (OUT/"thin-content-report.md").read_text(),
                       (OUT/"duplicate-content-report.md").read_text(), linking, technical,
                       matrix, (OUT/"crownwing-keyword-research.md").read_text()]
    report_html = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Crownwing complete SEO classification audit</title><style>
body{margin:0;background:#f6f5f0;color:#213b2b;font:16px/1.6 system-ui,sans-serif}main{max-width:1080px;margin:auto;padding:32px}
h1,h2,h3{line-height:1.25}h1{font-size:30px}h2{margin-top:42px;border-top:1px solid #b9c6b6;padding-top:24px}
p{margin:12px 0}code{overflow-wrap:anywhere;color:#284e32;background:#e9eee4;padding:2px 4px}
.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}td{padding:10px;border:1px solid #c6cec2;vertical-align:top;overflow-wrap:anywhere}
tr:first-child{background:#e4ebdd;font-weight:bold}hr{border:0;border-top:1px solid #c6cec2;margin:24px 0}
@media print{body{background:white}main{padding:0}h2{break-after:avoid}table{font-size:10px}}
</style><main>"""
    report_html += "\n".join(markdown_to_html(section) for section in report_sections) + "</main></html>"
    (OUT / "crownwing-complete-audit.html").write_text(report_html)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    audit()