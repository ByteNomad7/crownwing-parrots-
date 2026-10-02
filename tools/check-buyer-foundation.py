"""Verify the whole buyer-library request and preserve existing SEO boundaries."""
import json
import re
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

from buyer_resources import NEW_PAGES
from content_registry import extract_content, sync_content_registry
from site_config import PUBLIC_ORIGIN

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
baseline = json.loads((ROOT / "seo/content-baseline.json").read_text())
registry = json.loads((ROOT / "seo/content-register.json").read_text())
registry = {record["path"]: record for record in registry["pages"]}
pages = {}
for target in DIST.rglob("index.html"):
    route = "/" + target.parent.relative_to(DIST).as_posix().strip(".") + "/"
    route = "/" if route == "//" else route
    pages[route] = target.read_text()
assert set(baseline["routes"]) <= set(pages), "An established URL was removed"
assert set(NEW_PAGES) <= set(pages)
for route in NEW_PAGES:
    text = pages[route]
    assert 'href="/guides/"' in text
    assert len(re.findall(r"<h1\b", text)) == 1
    assert f'href="{PUBLIC_ORIGIN}{route}"' in text
    minimum = 250 if route == "/guides/" else 900
    main = re.search(r"<main\b[^>]*>(.*?)</main>", text, re.S)[1]
    assert len(re.sub(r"<[^>]+>", " ", main).split()) >= minimum, f"Insufficient resource depth: {route}"
    assert 'noindex' not in text
    assert 'site-identity-schema' not in text, "Organization graph belongs on home"

guide_count = 0
for route, text in pages.items():
    if route.startswith("/guides/") and route != "/guides/":
        match = re.search(r'<script type="application/ld\+json" id="buyer-article-schema">(.*?)</script>', text, re.S)
        assert match, f"Missing article markup: {route}"
        article = json.loads(match[1])
        assert article["@type"] == "Article"
        assert article["url"] == PUBLIC_ORIGIN + route
        assert article["mainEntityOfPage"]["@id"] == PUBLIC_ORIGIN + route + "#webpage"
        assert "author" not in article and "reviewedBy" not in article
        guide_count += 1
        assert 'href="/guides/buying-a-parrot/"' in text
    for match in re.finditer(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', text, re.S):
        data = json.loads(match[1])
        if isinstance(data, dict) and data.get("@type") == "WebPage" and route != "/":
            trail = data["breadcrumb"]
            assert trail["itemListElement"][-1]["item"] == PUBLIC_ORIGIN + route
            if route.startswith("/guides/") and route != "/guides/":
                assert trail["itemListElement"][1]["item"] == PUBLIC_ORIGIN + "/guides/"
        assert '"AggregateRating"' not in match[1] and '"Review"' not in match[1]

legal = pages["/guides/cites-parrots-uk/"]
for term in ("England", "Wales", "Scotland", "Northern Ireland", "Article 10", "Article 60",
             "Sources checked: 2026-10-02", "speciesplus.net", "gov.scot", "daera-ni.gov.uk"):
    assert term in legal, f"Missing documentation scope/source: {term}"
assert "/guidance/register-as-a-bird-keeper" not in legal, "Dead government URL"
budget = pages["/guides/parrot-ownership-costs/"]
choice = pages["/guides/choosing-a-parrot/"]
for text in (budget, choice):
    assert 'href="/buyer-resources.css"' in text and 'src="/buyer-tools.js"' in text
assert 'id="ownership-budget"' in budget and 'id="group-comparison"' in choice
assert 'This form prepares a download' not in budget
assert "emergency reserve" in budget.lower()
assert re.search(r'<button\b[^>]*type="submit"[^>]*disabled', budget), "No-JS calculator must not submit private estimates"
assert "best" in choice.lower() and "rank" in choice.lower()
assert len(re.findall(r"<table\b", choice)) == 1, "Comparison must exist in crawlable HTML"

# Optional dates stay truthful, and pure template/schema rebuilds never update them.
ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
sitemap = ET.parse(DIST / "sitemap.xml")
urls = sitemap.findall("s:url", ns)
assert {u.findtext("s:loc", namespaces=ns) for u in urls} == {PUBLIC_ORIGIN + r for r in pages}
assert all(not r.startswith("/search") for r in pages)
for entry in urls:
    route = entry.findtext("s:loc", namespaces=ns).removeprefix(PUBLIC_ORIGIN)
    modified = entry.findtext("s:lastmod", namespaces=ns)
    assert modified == registry[route].get("last_modified")

with tempfile.TemporaryDirectory() as temp:
    # Isolate registry side effects from the real project's date history.
    import content_registry as cr
    original_registry, original_baseline = cr.REGISTRY, cr.BASELINE
    testroot = Path(temp)
    cr.REGISTRY = testroot / "registry.json"
    cr.BASELINE = testroot / "baseline.json"
    mockdist = testroot / "dist"
    mockdist.mkdir()
    (mockdist / "index.html").write_text('<html><nav>Old menu</nav><main><h1>Bird care</h1><p>Original content.</p></main></html>')
    try:
        first = sync_content_registry(mockdist)["/"]
        (mockdist / "index.html").write_text('<html><nav>New menu</nav><main><h1>Bird care</h1><p>Original content.</p></main><script>changed()</script></html>')
        second = sync_content_registry(mockdist)["/"]
        assert first["content_digest"] == second["content_digest"]
        assert first["last_modified"] == second["last_modified"]
        (mockdist / "index.html").write_text('<html><main><h1>Bird care</h1><p>Revised meaningful information.</p></main></html>')
        third = sync_content_registry(mockdist)["/"]
        assert third["content_digest"] != second["content_digest"]
        (mockdist / "index.html").write_text('<html><main><h1>Bird care</h1><p>Revised meaningful information.</p><ul><li>Daily exercise</li></ul><table><tr><td>Individual needs vary</td></tr></table></main></html>')
        fourth = sync_content_registry(mockdist)["/"]
        assert fourth["content_digest"] != third["content_digest"], "Lists and comparison cells must affect dates"
        # A fingerprint format change alone is not a content edit.
        stored = json.loads(cr.REGISTRY.read_text())
        stored["pages"][0]["content_digest"] = extract_content((mockdist / "index.html").read_text())["legacy_digest"]
        stored["pages"][0].pop("digest_version")
        stored["pages"][0]["last_modified"] = None
        cr.REGISTRY.write_text(json.dumps(stored))
        migrated = sync_content_registry(mockdist)["/"]
        assert migrated["last_modified"] is None, "Fingerprint migration invented a modification date"
    finally:
        cr.REGISTRY, cr.BASELINE = original_registry, original_baseline

print(f"Buyer foundation passed: {len(pages)} preserved/indexable routes; {guide_count} real articles; sourced UK distinctions; readable tools; truthful sitemap dates.")