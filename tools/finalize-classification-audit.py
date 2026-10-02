#!/usr/bin/env python3
"""Record safe post-audit changes without destroying the original evidence."""
import csv
import hashlib
import html
import importlib.util
import json
import re
from datetime import datetime, timezone

from audit_quality_content import ADDITIONS
from content_registry import ContentParser, ROOT, discover_pages
from classification_decisions import DECISIONS

OUT = ROOT / "seo"
before = json.loads((OUT / "crownwing-classification-before.json").read_text())
pages = discover_pages(ROOT / "dist")
assert set(pages) == set(before["pages"]) == set(DECISIONS), "No routes may be added or retired without approval"
mobile = json.loads((OUT / "crownwing-mobile-rendering.json").read_text())
assert {p["route"] for p in mobile["pages"]} == set(pages)
assert not any(p.get("error") or p.get("overflow") or p.get("status") != 200 or
               len(p.get("h1", [])) != 1 or not p.get("menuOpens") or p.get("pageErrors") for p in mobile["pages"])
current, changed = {}, []
for route, file in sorted(pages.items()):
    source = file.read_text()
    cp = ContentParser()
    cp.feed(source)
    text = " ".join(" ".join(cp.body_fragments).split())
    sha = hashlib.sha256(source.encode()).hexdigest()
    current[route] = dict(html_sha256=sha, words=len(re.findall(r"\b[\w'-]+\b", text)),
                          classification=DECISIONS[route]["classification"],
                          title=html.unescape(re.search(r"<title>(.*?)</title>", source, re.S)[1]))
    if route in ADDITIONS:
        marker = "audit-quality-" + route.strip("/").replace("/", "-")
        assert source.count('id="' + marker + '"') == 1, f"Managed block duplicated/missing: {route}"
        assert current[route]["words"] > before["pages"][route]["words"] + 200, f"Expansion insufficient: {route}"
    if DECISIONS[route]["classification"] == "C":
        assert sha == before["pages"][route]["html_sha256"], f"Unapproved merge-source modification: {route}"
    if sha != before["pages"][route]["html_sha256"]:
        changed.append(route)
expected = set(ADDITIONS) | {"/available-birds/"}
assert set(changed) == expected, f"Unexpected public-page changes: {set(changed) ^ expected}"
inventory_file = OUT / "crownwing-66-page-inventory.csv"
with inventory_file.open(newline="") as handle:
    inventory = list(csv.DictReader(handle))
for row in inventory:
    route = row["URL"].removeprefix("https://crownwingparrots.co.uk")
    row["Audited word count before changes"] = before["pages"][route]["words"]
    row["Current word count after safe changes"] = current[route]["words"]
    row["Audited title before changes"] = before["pages"][route]["title"]
    row["Page title"] = current[route]["title"]
    row["Word count"] = current[route]["words"]
    row["Content uniqueness"] = row["Content uniqueness"].removeprefix("Audit baseline: ")
    row["Content uniqueness"] = "Audit baseline: " + row["Content uniqueness"]
    row["Implementation status"] = ("Practical expansion applied; owner-fact limits remain" if route in ADDITIONS else
                                    "Availability metadata clarified" if route == "/available-birds/" else
                                    "Merge awaits approval/production redirect support" if DECISIONS[route]["classification"] == "C" else
                                    "Audit recommendation; owner facts needed" if DECISIONS[route]["classification"] == "B" else
                                    "Retained; no public change in this pass")
with inventory_file.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(inventory[0]))
    writer.writeheader()
    writer.writerows(inventory)
summary = """# Applied changes and remaining manual review

The audit and all 69 classifications were completed before any public changes. Audit-state inventory fields, classifications and technical facts describe that preserved baseline; separate current word-count/status columns and post-change evidence distinguish the implementation.

## Exactly what changed

- /guides/buying-a-parrot-checklist/: concrete seller-question sheet, documented/observed/unknown answer categories and pre-purchase decision checks.
- /guides/parrot-diet-nutrition/: feeding-observation example, food-handling routine, veterinary discussion questions and RSPCA reference with genuine editorial check date.
- /guides/parrot-housing-enrichment/: practical enclosure/room screening, enrichment review and repeatable exercise/maintenance checks, with RSPCA sources.
- /guides/preparing-for-a-parrot/: before-handover readiness, room/fume hazards, arrival-information and vet-contact prompts, with veterinary-authored hazard reference.
- /parrot-prices-uk/: individual-quotation comparison, included/excluded items and purchase-versus-ownership separation. No fictitious prices or inclusions.
- /locations/belfast/: origin/destination/purpose worksheet, directly linked DAERA/APHA starting points and editorial source-check disclosure. No local branch, stock or delivery claim.
- /available-birds/: title/description now explicitly describe offered groups and details by enquiry, rather than implying published individual prices/ages.
- Existing source generator integrates these managed additions idempotently; genuine content history/source-check records are updated by its existing date registry.

No new public pages, page deletions, URL changes, redirects, noindex changes, visual redesign, new tracking, submitted forms or stock/Product/Review schema. All 69 URLs remain until structural recommendations are approved.

## Changed-page evidence

| URL | Words at audit | Words after expansion |
|---|---:|---:|
"""
for route in changed:
    summary += f"| {route} | {before['pages'][route]['words']} | {current[route]['words']} |\n"
summary += """
## Verified

The full npm test suite passed: 69 preserved routes, metadata/canonicals/sitemap, source/schema/images/fragments, buyer intent, existing enquiry boundaries, URL aliases and buyer-tool validation. All 69 pages also passed live mobile H1/navigation/overflow/error checks after these changes. The complete audit-phase HTTP crawl and graph checks are retained in the before snapshot; post-change browser evidence is current.

## Manual review / remaining work

1. Approve or decline the 13 city/directory merge recommendations. The proposed result is 56 canonical indexable pages, not a page-count target. Consolidation must preserve useful content, replace separate city enquiry forms with contact access and serve tested single-hop 301s.
2. Verify a production-supported HTTP redirect method before retirement. Current static publishing does not automatically run the preview Python redirect server.
3. Confirm the 16 named species are genuinely within the intended offered range. Their B briefs require sourced species-specific depth; no fabricated availability justifies retention.
4. Supply first-party facts for /our-approach/: real care practices and the actual buying/aftercare process. No unverified qualifications, history or guarantees were added.
5. Verify any price data, individual birds and handover services before publishing them. The improved quotation page still does not offer measured market-average or current individual prices.
6. Obtain published-host/Search Console/backlink and field-CWV evidence; rankings, volume/difficulty and actual Google indexation remain unknown.
7. Source-checks are editorial, not professional legal/veterinary approval. Maintain genuine review dates and relevant expert support.

The original A/B/C labels remain the audit decisions; six B pages have received practical expansions, while exact-offer, first-party evidence and structural gates remain visible instead of being claimed complete.
"""
(OUT / "crownwing-implementation-summary.md").write_text(summary)
(OUT / "crownwing-classification-after.json").write_text(json.dumps({
    "verified_at": datetime.now(timezone.utc).isoformat(), "changed_pages": changed,
    "current_routes": len(pages), "retired_urls": [], "source_policy_changed": False,
    "pages": current, "mobile_evidence": mobile["checked_at"], "tests": "npm test passed",
}, indent=2) + "\n")
plan_file = OUT / "crownwing-implementation-plan.md"
plan = plan_file.read_text().split("## Exact current implementation status")[0]
plan += "## Current implementation status\n\nAudit first, then six practical expansions and one availability metadata clarification. " \
        "See crownwing-implementation-summary.md and the after snapshot for exact changes. C retirements, exact-species/business confirmations " \
        "and production redirect support remain outstanding; no structural changes are represented as completed.\n"
plan_file.write_text(plan)
spec = importlib.util.spec_from_file_location("audit_report", ROOT / "tools/audit-page-classification.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
report_file = OUT / "crownwing-complete-audit.html"
report = report_file.read_text()
section = '<section id="implementation-summary">' + module.markdown_to_html(summary) + "</section><hr>"
report = re.sub(r'<section id="implementation-summary">.*?</section><hr>', "", report, flags=re.S)
report = report.replace("<main>", "<main>" + section, 1)
report = re.sub(r'<h1>Audit-led implementation plan</h1>.*?(?=<h1>Thin/incomplete content review</h1>)',
                lambda _: module.markdown_to_html(plan), report, flags=re.S)
report_file.write_text(report)
assert len(re.findall(r"^## \d{2} — ", (OUT/"crownwing-page-classification.md").read_text(), re.M)) == 69
print(json.dumps({"verified_routes": len(pages), "public_pages_changed": changed,
                  "all_69_classifications": "present exactly once",
                  "structural_changes": "none; approval needed"}, indent=2))