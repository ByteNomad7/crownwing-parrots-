"""Check crawler access, readable public exports and visible/schema consistency."""
import json
import re
import sys
from pathlib import Path
from urllib import robotparser
from xml.etree import ElementTree

from ai_discovery import BUYER_ANSWERS, SEARCH_AGENTS, MainText, export_name
from site_config import PUBLIC_ORIGIN

DIST = Path(__file__).resolve().parents[1] / "dist"
urls = [n.text for n in ElementTree.parse(DIST / "sitemap.xml").findall(".//{*}loc")]
robots = robotparser.RobotFileParser()
robots.parse((DIST / "robots.txt").read_text().splitlines())
assert robots.site_maps() == [PUBLIC_ORIGIN + "/sitemap.xml"]
for agent in SEARCH_AGENTS + ("UnlistedSearchCrawler", "GPTBot", "ClaudeBot"):
    for url in urls + [PUBLIC_ORIGIN + "/llms.txt"]:
        assert robots.can_fetch(agent, url), (agent, url)
index = (DIST / "llms.txt").read_text()
assert len(list((DIST / "ai-pages").glob("*.md"))) == len(urls)
for url in urls:
    path = url.removeprefix(PUBLIC_ORIGIN)
    source = (DIST / path.strip("/") / "index.html").read_text()
    filename = export_name(path)
    exported = (DIST / "ai-pages" / filename).read_text()
    assert f"Canonical URL: {url}" in exported
    assert url in index and f"/ai-pages/{filename}" in index
    assert source.count(f'href="/ai-pages/{filename}"') == 1
    assert len(exported) > 300, filename
    assert "<script" not in exported and "form-name" not in exported
    assert not re.search(r"/locations/(?:london|manchester)/", exported)
faq_source = (DIST / "available-birds/index.html").read_text()
faq = json.loads(re.search(r'id="buyer-answer-schema">(.*?)</script>', faq_source, re.S)[1])
parser = MainText()
parser.feed(faq_source)
visible = parser.markdown()
for item, (question, answer) in zip(faq["mainEntity"], BUYER_ANSWERS, strict=True):
    assert item["name"] == question and question in visible
    assert item["acceptedAnswer"]["text"] == answer and answer in visible
assert faq_source.count('id="buyer-answers"') == 1
probe = MainText()
probe.feed('<main><h1>Answer</h1><form><div><input><p>Private</p></div></form><p>Public</p><script>bad</script><a href="/guides/">Guides</a></main>')
assert "Public" in probe.markdown() and "Private" not in probe.markdown()
assert "bad" not in probe.markdown() and PUBLIC_ORIGIN + "/guides/" in probe.links
sys.path.insert(0, str(DIST.parent))
from tools.production_site import app
with app.test_client() as client:
    for path, content_type in [("/llms.txt", "text/plain"),
                               ("/ai-pages/home.md", "text/markdown")]:
        response = client.get(path)
        assert response.status_code == 200
        assert response.headers["Content-Type"].startswith(content_type)
        assert response.headers["X-Robots-Tag"] == "noindex"
        assert client.head(path).status_code == 200
    assert client.get("/ai-pages/not-a-real-page.md").status_code == 404
    assert "X-Robots-Tag" not in client.get("/").headers
headers = (DIST / "_headers").read_text()
assert "/ai-pages/*" in headers and "/llms.txt" in headers
assert headers.count("X-Robots-Tag: noindex") == 2
print(json.dumps({"public_text_exports": len(urls), "crawler_permissions": "passed",
                  "visible_faq_matches_schema": "passed", "optional_directory": "passed"}))