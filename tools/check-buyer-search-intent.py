"""Verify buying keywords are backed by visible content, not stock promises."""

import html
import json
import re
from pathlib import Path

from breeder_content import DISPLAY_NAMES, SALE_SLUGS

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
categories = json.loads((ROOT / "tools/category-content.json").read_text())


def visible(text):
    return html.unescape(re.sub(r"<[^>]+>", " ", text))


def heading(text):
    return visible(re.search(r"<h1>(.*?)</h1>", text, re.S)[1]).strip()


targets = {
    "african-parrots": "African Grey Parrots for Sale UK",
    "macaws": "Macaw Parrots for Sale UK",
    "cockatoos": "Cockatoo Parrots for Sale UK",
    "amazons": "Amazon Parrots for Sale UK",
    "conures": "Conure Parrots for Sale UK",
    "caiques": "Caique Parrots for Sale UK",
    "eclectus": "Eclectus Parrots for Sale UK",
    "parakeets-small-psittacines": "Parakeets & Budgies for Sale UK",
}
for group, keyword in targets.items():
    path = DIST / "parrots-for-sale" / SALE_SLUGS[group] / "index.html"
    text = path.read_text()
    title = visible(re.search(r"<title>(.*?)</title>", text)[1])
    assert title == keyword + " | Crownwing Parrots", (path, title)
    assert len(title) <= 65, (path, "Title too long")
    description = html.unescape(re.search(r'<meta name="description" content="([^"]+)"', text)[1])
    assert 100 <= len(description) <= 170, (path, description)
    assert "by enquiry" in description, path
    assert heading(text) == categories[group]["buying_heading"], path
    assert categories[group]["buying_intro"] in html.unescape(text), path
    assert f'href="/contact/?species={group}"' in text, path
    assert "Species photographs are not individual stock listings." in text, path
    body = visible(re.search(r"<main\b[^>]*>(.*?)</main>", text, re.S)[1])
    assert "price" in body.lower() and "available" in body.lower(), path
    # Informational guides keep their own purpose rather than becoming sale adverts.
    guide = (DIST / "parrots" / group / "index.html").read_text()
    assert "for sale" not in re.search(r"<title>(.*?)</title>", guide)[1].lower(), group
    assert "species and care guide, not a listing" in guide, group
    assert DISPLAY_NAMES[group] in guide, group
    assert 'itemtype="https://schema.org/Product"' not in text, path
    schemas = [json.loads(s) for s in re.findall(
        r'<script type="application/ld\+json"[^>]*>(.*?)</script>', text, re.S)]
    assert not any(s.get("@type") in ("Product", "Offer", "AggregateRating") for s in schemas), path

hub = (DIST / "parrots-for-sale/index.html").read_text()
assert "<title>Parrots for Sale UK | Crownwing Parrots</title>" in hub
assert heading(hub).startswith("Parrots for sale in the UK.")
for question in [
    "How do I get a current parrot price?",
    "Can I enquire about baby or hand-reared parrots?",
    "What should I check when searching for parrots for sale near me?",
]:
    assert f"<summary>{question}</summary>" in hub, question
assert "they do not identify Crownwing branches or local stock" in hub
macaw = (DIST / "parrots-for-sale/macaws/index.html").read_text()
assert "Are hand-reared macaws always tame?" in macaw
assert "do not establish that a Hyacinth Macaw is currently for sale" in macaw
assert "Macaw parrot prices and total ownership costs" in macaw
home = (DIST / "index.html").read_text()
assert '<h1>A little wild.<br>A lot of <em>wonder.</em></h1>' in home
print(json.dumps({"buying_keyword_targets": len(targets) + 1,
                  "aligned_titles_headings_and_visible_intros": "passed",
                  "price_rearing_and_local_buyer_questions": "passed",
                  "care_guides_separate_from_sales_intent": "passed",
                  "no_unverified_product_stock_or_ratings_schema": "passed"}, indent=2))