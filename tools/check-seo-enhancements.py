"""Regression checks for the nonvisual SEO improvements on all existing pages."""

import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from site_config import PUBLIC_ORIGIN
from seo_metadata import catalogue

DIST = Path(__file__).resolve().parents[1] / "dist"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.images = []
        self.connections = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            key = attrs.get("name", attrs.get("property"))
            if key:
                assert key not in self.meta, ("Duplicate meta tag", key)
                self.meta[key] = attrs["content"]
        if tag == "img":
            self.images.append(attrs)
        if tag == "link" and attrs.get("rel") == "preconnect":
            self.connections.append(attrs)


pages = images = responsive = 0
dimensions_cache = {}
for file in sorted(DIST.rglob("index.html")):
    pages += 1
    text = file.read_text()
    parser = Page()
    parser.feed(text)
    meta = parser.meta
    for key in ["og:image", "og:image:width", "og:image:height", "og:image:alt",
                "twitter:card", "twitter:title", "twitter:description", "twitter:image"]:
        assert meta.get(key), (file, key)
    assert meta["twitter:title"] == meta["og:title"]
    assert meta["twitter:description"] == meta["description"]
    assert meta["twitter:image"] == meta["og:image"]
    assert meta["twitter:card"] == "summary_large_image"
    image_url = urlsplit(meta["og:image"])
    assert image_url.netloc == urlsplit(PUBLIC_ORIGIN).netloc, file
    assert "-thumb" not in image_url.path, file
    asset = DIST / image_url.path.lstrip("/")
    assert asset.is_file(), (file, asset)
    if asset not in dimensions_cache:
        dimensions_cache[asset] = subprocess.check_output(
            ["magick", "identify", "-format", "%w %h", str(asset)], text=True).split()
    assert dimensions_cache[asset] == [meta["og:image:width"], meta["og:image:height"]], file
    for image in parser.images:
        images += 1
        assert image.get("width") and image.get("height"), (file, image)
        assert image.get("decoding") == "async", (file, image)
        if "availability-thumbnail" in image.get("class", "").split():
            assert image["width"] == image["height"] == "44", (file, image)
        if image.get("srcset"):
            responsive += 1
            assert image.get("sizes"), (file, image)
            for candidate in image["srcset"].split(","):
                src, width = candidate.strip().rsplit(" ", 1)
                assert (DIST / src.lstrip("/")).is_file(), (file, src)
                photo = catalogue()[src]
                actual = photo["thumbnailWidth"] if src == photo["thumbnail"] else photo["width"]
                assert width == f"{actual}w", (file, candidate)
        assert not (image.get("fetchpriority") == "high" and image.get("loading") == "lazy"), file
    assert sorted(a["href"] for a in parser.connections) == [
        "https://fonts.googleapis.com", "https://fonts.gstatic.com"], file
    assert "crossorigin" in next(a for a in parser.connections if "gstatic" in a["href"])
    schemas = [json.loads(s) for s in re.findall(
        r'<script type="application/ld\+json"[^>]*>(.*?)</script>', text, re.S)]
    webpage = next(s for s in schemas if s.get("@type") == "WebPage")
    assert webpage["@id"] == webpage["url"] + "#webpage", file
    assert webpage["isPartOf"]["@id"] == PUBLIC_ORIGIN + "/#website", file
    assert webpage["publisher"]["@id"] == PUBLIC_ORIGIN + "/#organization", file
    assert webpage["primaryImageOfPage"]["url"] == meta["og:image"], file
    assert webpage["inLanguage"] == "en-GB", file
    if file == DIST / "index.html":
        graph = next(s["@graph"] for s in schemas if "@graph" in s)
        assert {s["@type"] for s in graph} == {"Organization", "WebSite"}
        assert all(s["url"] == PUBLIC_ORIGIN + "/" for s in graph)
        assert next(s for s in graph if s["@type"] == "Organization")["name"] == "Crownwing Parrots"
    else:
        assert not any("@graph" in s for s in schemas), file

print(json.dumps({"pages": pages, "complete_social_metadata": "passed",
                  "official_site_identity": "passed", "images_with_dimensions_and_decoding": images,
                  "responsive_images": responsive, "original_circle_thumbnails": "preserved"}, indent=2))