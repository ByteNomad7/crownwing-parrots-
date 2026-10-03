"""Check confirmed business copy, guide separation and availability enquiry routes."""

import json
import re
from pathlib import Path

from breeder_content import DISPLAY_NAMES, HERO_INTRO

root = Path(__file__).resolve().parents[1]
dist = root / "dist"
home = (dist / "index.html").read_text()
available = (dist / "available-birds/index.html").read_text()
assert '<h1>A little wild.<br>A lot of <em>wonder.</em></h1>' in home
assert HERO_INTRO in home
assert available.count('class="link-card availability-card"') == 8
assert "Individual birds change regularly" in available
assert "Explore our available range below" in available
for slug, name in DISPLAY_NAMES.items():
    assert f'href="/contact/?species={slug}"' in available
    guide = (dist / "parrots" / slug / "index.html").read_text()
    assert "Explore species information and everyday care" in guide, slug
    assert "not a live stock list" not in available
    assert f'href="/parrots/{slug}/"' in available
    assert 'class="photo-collection"' in guide
    assert re.search(r"<details\b[^>]*\bopen", guide), slug
    assert name in (dist / "common.js").read_text()
    assert name in home.replace("&amp;", "&")
for path in dist.rglob("index.html"):
    text = path.read_text()
    header = re.search(r"<header>.*?</header>", text, re.S)[0]
    for href, label in [
        ("/available-birds/", "Available birds"),
        ("/parrots-for-sale/", "Buying a parrot"),
        ("/contact/", "Contact us"),
    ]:
        assert f'href="{href}"' in header and label in header, (path, href)
    assert "African parrots" not in text and "African Parrots" not in text, path
    assert "Parrot breeder &amp; retailer" in text, path
contact = (dist / "contact/index.html").read_text()
assert "Download enquiry" in contact and "Send enquiry" not in contact
assert "Download your enquiry and email it" in contact
for path in dist.rglob("index.html"):
    text = path.read_text()
    for warning in (
        "not an individual stock listing", "not a current individual stock listing",
        "not individual stock listings", "not a live stock list",
        "not a listing of individual birds", "NOT A STOCK LISTING",
        "NOT INDIVIDUAL BIRD LISTINGS", "currently prepares a downloadable",
        "does not send or save your details",
    ):
        assert warning not in text, (path, warning)
approach = (dist / "our-approach/index.html").read_text()
assert 'class="editorial-photo"' in approach
assert "how it was reared and socialised" in approach
assert "Confirm the individual price" in approach
assert "collection arrangements" in approach
assert "Ask what aftercare is offered" in approach
print(json.dumps({
    "breeder_and_retailer_identity": "passed",
    "original_hero_headline": "preserved",
    "available_groups": 8,
    "group_specific_enquiry_routes": "passed",
    "species_guides_separated_from_live_stock": "passed",
    "gallery_collections_default_expanded": "passed",
    "enquiry_download_not_misrepresented_as_delivery": "passed",
}, indent=2))