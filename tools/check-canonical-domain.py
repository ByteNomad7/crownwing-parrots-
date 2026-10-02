"""Validate the official SEO origin and reference footer on every route."""

import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree

from site_config import PUBLIC_ORIGIN

DIST = Path(__file__).resolve().parents[1] / "dist"
expected = set()
for page in DIST.rglob("index.html"):
    relative = page.parent.relative_to(DIST).as_posix()
    route = "/" if relative == "." else "/" + relative + "/"
    url = PUBLIC_ORIGIN + route
    text = page.read_text()
    assert "ihermes.chatgpt.site" not in text, page
    canonicals = re.findall(r'<link rel="canonical" href="([^"]+)"', text)
    assert canonicals == [url], (page, canonicals)
    assert f'<meta property="og:url" content="{url}">' in text, page
    for image in re.findall(r'<meta property="og:image" content="([^"]+)"', text):
        assert urlsplit(image).netloc == urlsplit(PUBLIC_ORIGIN).netloc, (page, image)
    schemas = [json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)]
    for schema in schemas:
        if schema.get("@type") == "WebPage":
            assert schema["url"] == url, page
            assert schema["isPartOf"]["url"] == PUBLIC_ORIGIN + "/", page
            for crumb in schema.get("breadcrumb", {}).get("itemListElement", []):
                assert crumb["item"].startswith(PUBLIC_ORIGIN + "/"), page
    footer = re.search(r'<footer class="site-footer">.*?</footer>', text, re.S)
    assert footer and len(re.findall(r'<footer\b', text)) == 1, page
    for policy in ["/privacy-policy/", "/cookie-policy/", "/business-policies/"]:
        assert f'href="{policy}"' in footer[0], (page, policy)
    assert "/footer.css" in (DIST / "style.css").read_text()
    if "noindex" not in text:
        expected.add(url)

actual = [e.text for e in ElementTree.parse(DIST / "sitemap.xml").findall(".//{*}loc")]
assert len(actual) == len(set(actual)) and set(actual) == expected
assert (DIST / "robots.txt").read_text() == "User-agent: *\nAllow: /\nSitemap: " + PUBLIC_ORIGIN + "/sitemap.xml\n"
print(json.dumps({"canonical_origin": PUBLIC_ORIGIN, "pages": len(expected),
                  "canonical_social_schema_sitemap_robots": "passed",
                  "shared_footer_and_policy_links": "passed"}, indent=2))