"""Validate the uploaded-photo assignments and removal of sample photography."""

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
catalogue = json.loads((ROOT / "tools/photo-metadata.json").read_text())
by_source = {p["src"]: p for p in catalogue["photos"]}
all_html = "\n".join(p.read_text() for p in DIST.rglob("index.html"))


class PhotoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.photos = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "data-photo-src" in attrs:
            self.photos.append(attrs["data-photo-src"])
        if tag == "img":
            self.images.append(attrs)


assert 'class="credits"' not in all_html, "Sample footer credits remain"
assert 'class="photo-credit"' not in all_html, "Sample photo credits remain"
assert "commons.wikimedia.org" not in all_html, "Sample photography attribution remains"
assert "More photos coming soon" not in all_html, "Empty photo tiles remain"
for name in ["grey", "macaw", "cockatoo", "amazon", "conure", "caique", "eclectus", "parakeet"]:
    assert not (DIST / "assets" / f"{name}.jpg").exists(), f"Sample photo remains: {name}"

matched = []
for page in DIST.rglob("index.html"):
    parser = PhotoParser()
    parser.feed(page.read_text())
    for image in parser.images:
        assert image.get("src"), f"Empty image source: {page}"
        decorative = (
            "availability-thumbnail" in image.get("class", "").split()
            and image.get("aria-hidden") == "true"
            and image.get("alt") == ""
        )
        assert image.get("alt") or decorative, f"Missing photo description: {page}"
    parts = page.relative_to(DIST).parts
    if len(parts) == 3 and parts[0] == "parrots":
        for source in parser.photos:
            assert source in by_source, f"Unknown gallery photo: {source}"
            photo = by_source[source]
            assert photo["group"] == parts[1], f"Wrong group: {source} on {page}"
            assert photo.get("publish", True), f"Unconfirmed photo published: {source}"
            matched.append(source)

for photo in catalogue["photos"]:
    for key in ["src", "thumbnail"]:
        assert (DIST / photo[key].lstrip("/")).exists(), f"Missing asset: {photo[key]}"
    assert photo["width"] > 0 and photo["height"] > 0
    if photo.get("publish", True):
        assert photo["src"] in matched, f"Matched photo absent from gallery: {photo['src']}"
        if photo["identificationConfidence"] == "provisional":
            assert photo.get("identificationDisplayNote") in all_html, "Provisional identification is not disclosed"
    else:
        assert photo["src"] not in all_html, f"Unconfirmed photo is displayed: {photo['src']}"

print(json.dumps({
    "matched_photos_in_correct_galleries": len(set(matched)),
    "provisional_group_matches_disclosed": sum(p["identificationConfidence"] == "provisional" for p in catalogue["photos"]),
    "unclassified_photos_withheld": sum(not p.get("publish", True) for p in catalogue["photos"]),
    "sample_photos_and_credits_removed": True,
    "gallery_descriptions_and_assets": "passed",
}, indent=2))