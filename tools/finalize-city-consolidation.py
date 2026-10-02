"""Refresh current implementation evidence while preserving the 69-page audit."""
import csv
import hashlib
import html
import importlib.util
import json
import re
from datetime import datetime, timezone
from collections import Counter, deque
from urllib.parse import urlsplit

from classification_decisions import DECISIONS
from content_registry import ContentParser, ROOT, discover_pages
from route_rules import REDIRECTS
from city_consolidation import RECORDS

OUT = ROOT / "seo"
before = json.loads((OUT / "crownwing-classification-before.json").read_text())
pages = discover_pages(ROOT / "dist")
assert set(REDIRECTS) == {r for r, d in DECISIONS.items() if d["classification"] == "C"}
assert set(pages) == set(before["pages"]) - set(REDIRECTS)
assert len(pages) == 56
mobile = json.loads((OUT / "crownwing-mobile-rendering.json").read_text())
assert {p["route"] for p in mobile["pages"]} == set(pages)
assert not any(p.get("error") or p.get("overflow") or p.get("status") != 200 or
               len(p.get("h1", [])) != 1 or not p.get("menuOpens") or p.get("pageErrors") for p in mobile["pages"])
facts, outbound, contextual_outbound = {}, {}, {}
for route, file in sorted(pages.items()):
    source = file.read_text()
    parser = ContentParser()
    parser.feed(source)
    facts[route] = {
        "status": 200, "classification": DECISIONS[route]["classification"],
        "words": len(re.findall(r"\b[\w'-]+\b", " ".join(parser.body_fragments))),
        "html_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "canonical": re.search(r'<link rel="canonical" href="([^"]+)"', source)[1],
        "title": html.unescape(re.search(r"<title>(.*?)</title>", source, re.S)[1]),
        "h1": parser.headings[0], "image_count": len(parser.images),
        "body_fingerprint": hashlib.sha256(" ".join(parser.body_fragments).encode()).hexdigest(),
    }
    targets, contextual = [], set()
    for link in parser.links:
        parts = urlsplit(link["href"])
        if parts.netloc and parts.hostname != "crownwingparrots.co.uk":
            continue
        if parts.scheme not in ("", "http", "https"):
            continue
        target = parts.path or route
        if target in pages:
            targets.append(target)
            if link["main"]:
                contextual.add(target)
    outbound[route] = targets
    contextual_outbound[route] = contextual
    if route in RECORDS:
        assert source.count('id="approved-city-consolidation"') == 1
for source, target in REDIRECTS.items():
    assert facts[target]["status"] == 200
    archive = OUT / "retired-city-pages" / (source.strip("/").replace("/", "-") + ".html")
    assert archive.exists()
    facts[source] = {"status": 301, "target": target, "words": 0, "classification": "C", "canonical": None, "title": ""}
inbound = Counter(target for targets in outbound.values() for target in targets)
depth, queue = {"/": 0}, deque(["/"])
while queue:
    route = queue.popleft()
    for target in outbound[route]:
        if target not in depth:
            depth[target] = depth[route] + 1
            queue.append(target)
assert set(depth) == set(pages), "Orphan/unreachable surviving page"

with (OUT / "crownwing-66-page-inventory.csv").open(newline="") as file:
    inventory = list(csv.DictReader(file))
for row in inventory:
    route = row["URL"].removeprefix("https://crownwingparrots.co.uk")
    row["Audited status before implementation"] = before["pages"][route].get("status", 200)
    row["Audited canonical before implementation"] = before["pages"][route].get("canonical", row["URL"])
    row["Audited title before changes"] = before["pages"][route]["title"]
    row["Audited word count before changes"] = before["pages"][route]["words"]
    row["Status code"] = facts[route]["status"]
    row["Page title"] = facts[route]["title"]
    row["Word count"] = row["Current word count after safe changes"] = facts[route]["words"]
    row["Indexable?"] = "No; HTTP 301" if route in REDIRECTS else "Yes; canonical HTML (Google state unverified)"
    row["Canonical URL"] = facts[route]["canonical"] or ""
    row["Current destination"] = REDIRECTS.get(route, route)
    row.setdefault("Audited H1 before implementation", row["H1"])
    row["H1"] = facts[route].get("h1", "")
    row["Image count"] = facts[route].get("image_count", 0)
    row["Internal links in"] = inbound[route]
    row["Internal links out"] = len(outbound.get(route, []))
    row["Contextual inbound sources"] = "; ".join(sorted(r for r, targets in contextual_outbound.items() if route in targets))
    row["Contextual outbound targets"] = "; ".join(sorted(contextual_outbound.get(route, [])))
    row["Minimum clicks from home"] = depth.get(route, "")
    row["Body fingerprint"] = facts[route].get("body_fingerprint", "")
    if route in REDIRECTS:
        row["Schema types"] = ""
    row["Implementation status"] = ("Approved merge complete; production-ready HTTP 301; not published yet" if route in REDIRECTS else
                                    "Merged topical guidance applied" if route in RECORDS else
                                    "Practical expansion applied; owner-fact limits remain" if route in ("/parrot-prices-uk/", "/locations/belfast/") else
                                    "Retained; direct links/shared footer updated; owner-fact review remains where flagged")
with (OUT / "crownwing-66-page-inventory.csv").open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=list(inventory[0]))
    writer.writeheader()
    writer.writerows(inventory)
with (OUT / "crownwing-indexation-matrix.csv").open(newline="") as file:
    matrix = list(csv.DictReader(file))
matrix_md = "# Current source indexation matrix\n\n56 canonical HTML pages; 13 approved legacy routes return HTTP 301 through the production app. Google indexation and published-host behaviour remain unverified until publishing.\n\n| URL | Current source state | Target | Implementation |\n|---|---|---|---|\n"
for row in matrix:
    route = row["URL"].removeprefix("https://crownwingparrots.co.uk")
    row["Current source state"] = "HTTP 301; no index document; absent from sitemap" if route in REDIRECTS else "HTTP 200 canonical HTML; in sitemap"
    row["Recommended state"] = "Redirect only; not standalone indexable content" if route in REDIRECTS else "Canonical indexable HTML"
    row["Implementation state"] = "Implemented; publish and verify real host" if route in REDIRECTS else "Retained; deployed Google state unverified"
    matrix_md += f"| {route} | {row['Current source state']} | {row['Target']} | {row['Implementation state']} |\n"
with (OUT / "crownwing-indexation-matrix.csv").open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=list(matrix[0]))
    writer.writeheader()
    writer.writerows(matrix)
(OUT / "crownwing-indexation-matrix.md").write_text(matrix_md)

summary = """# Applied changes and remaining manual review

The audit classified all 69 actual pages before changes: original 66 plus three later buyer-library additions. Those classifications remain the audit baseline, not an invented final page-count target.

## Approved consolidation completed

- 12 Great Britain city guides and /locations/ have been merged into the strongest existing guides. There are now 56 canonical HTML pages; Belfast remains as a scoped Northern Ireland aid.
- Useful city topics were consolidated into practical shared-home, weekly-care, first-time expectation, backup-care, safe-room/exercise, feeding-record, enclosure/activity and identity/terms sections. The guide library links directly to these resources, Belfast and shared contact access.
- 13 source URLs no longer have public index documents, are absent from the sitemap and are not used as internal links. Their city-labelled download forms are replaced by /contact/; no buyer records existed to delete.
- A shared redirect manifest supplies real HTTP 301s, including slashless and /index.html aliases. Query strings survive; host/protocol corrections and merges resolve in one hop.
- Autoscale configuration and the production Gunicorn/Flask workflow replace static-only hosting, with the user's approval of usage-based compute billing. No publication was performed.
- Private copies of retired city HTML are in seo/retired-city-pages/. The original audit snapshot and all 69 classifications are preserved.
- The existing brand, logo/favicon, nature-led styling, photo galleries and remaining enquiry/tool behaviour are preserved. Shared footer and breadcrumb/navigation links now go directly to surviving resources.

## Earlier safe improvements retained

- Seller checklist: specific questions and documented/observed/unknown evidence categories.
- Nutrition: feeding observations, hygiene, vet discussion and dated welfare references.
- Housing: enclosure/room screening, enrichment review and repeatable supervision.
- Home preparation: readiness, household/fume hazards and quiet arrival checks.
- Purchase prices: individual quotation/inclusion comparison, without fictitious prices.
- Belfast: DAERA/APHA source links and origin/destination/purpose checks, without local-service claims.
- Availability metadata: offered groups and details by enquiry, not implied published individual prices/ages.

## Exact permanent redirect destinations

| Retired URL | Direct destination |
|---|---|
"""
for source, target in REDIRECTS.items():
    summary += f"| {source} | {target} |\n"
summary += """
## Verification and limits

The full npm test suite passes. Production-app tests cover all 13 redirect rules and three path variants with GET/HEAD, query retention, combined host/protocol correction, every surviving page's index/slash aliases, sitemap/robots content, no internal retired links, private-file protection, branded 404s and non-submitting contact behaviour.

All 56 surviving pages pass live mobile title/H1/navigation/error/overflow checks. The running preview uses the same Gunicorn/Flask service configured for publishing. These are development/production-app tests, not proof of a published deployment or actual Google indexing. Rebuild checks verify the 56/13 route split and managed additions remain stable.

## Remaining manual review

1. Publish the configured Autoscale app, connect/verify the owner-specified crownwingparrots.co.uk domain and check all 13 HTTP redirects on the real published host. Production has not been published or verified.
2. Confirm the 16 named species are genuinely within the intended offered range; complete the specific evidence/depth briefs without treating photos as stock proof.
3. Provide first-party business/care/buying/aftercare facts for /our-approach/. No credentials, years of experience or guarantees were invented.
4. Verify actual individual birds, prices and any handover arrangements before publishing them.
5. Obtain Search Console/backlink history and field-CWV evidence. Historical city traffic, rankings, keyword volumes/difficulty and Google indexation remain unverified.
6. Keep legal/veterinary professional review distinct from editorial source checks.
"""
(OUT / "crownwing-implementation-summary.md").write_text(summary)
plan_file = OUT / "crownwing-implementation-plan.md"
plan = plan_file.read_text()
plan = plan.replace("## 3. Proposed C consolidation — owner decision needed", "## 3. C consolidation — approved and implemented")
plan = re.sub(r"\*\*Hosting gate:\*\*.*?(?=\n\n)", "**Hosting gate resolved for the configured app:** The owner approved Autoscale with usage-based compute billing. Production Gunicorn/Flask tests verify actual HTTP 301 behaviour, including aliases and query strings. Publishing and real-host checks remain manual; static rewrites are not substituted for redirects.", plan, flags=re.S)
plan = plan.replace("## Current implementation status\n\n" + plan.split("## Current implementation status\n\n")[-1],
                    "## Current implementation status\n\nSix practical expansions, accurate availability metadata and all 13 owner-approved city/directory merges are implemented. Autoscale server hosting was approved and configured for real HTTP 301s. There are 56 surviving canonical pages. Publish-host checks and exact-species/business evidence remain outstanding; see crownwing-implementation-summary.md.\n")
plan_file.write_text(plan)
deployment = {"target": "autoscale", "server": "Gunicorn/Flask", "published": False,
              "redirect_support": "production app tested; real published host pending"}
(OUT / "crownwing-classification-after.json").write_text(json.dumps({
    "verified_at": datetime.now(timezone.utc).isoformat(), "audited_routes": 69,
    "current_canonical_routes": 56, "retired_routes": REDIRECTS, "pages": facts,
    "mobile_evidence": mobile["checked_at"], "tests": "npm test passed",
    "deployment": deployment, "source_noindex_added": 0,
}, indent=2) + "\n")
spec = importlib.util.spec_from_file_location("audit_report", ROOT / "tools/audit-page-classification.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
report_file = OUT / "crownwing-complete-audit.html"
report = report_file.read_text()
files = ["crownwing-implementation-summary.md", "crownwing-implementation-plan.md",
         "crownwing-page-classification.md", "thin-content-report.md", "duplicate-content-report.md",
         "internal-linking-plan.md", "crownwing-indexation-matrix.md"]
body = '<p><strong>Current implementation is summarised first. The per-page classification, thin-content and duplication reports below preserve the original audit findings before implementation.</strong></p>'
body += "<hr>".join(module.markdown_to_html((OUT / file).read_text()) for file in files)
report = re.sub(r"<main>.*?</main>", lambda _: "<main>" + body + "</main>", report, flags=re.S)
report_file.write_text(report)
assert len(re.findall(r"^## \d{2} — ", (OUT / "crownwing-page-classification.md").read_text(), re.M)) == 69
print(json.dumps({"canonical_pages": 56, "permanent_redirects": 13,
                  "original_classifications_preserved": 69, "published": False}, indent=2))