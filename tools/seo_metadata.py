"""Nonvisual SEO helpers using approved images and confirmed site identity."""

import hashlib
import html
import json
import re
import subprocess
import tempfile
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from site_config import PUBLIC_ORIGIN

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


class ImageTags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.images.append(dict(attrs))


@lru_cache(maxsize=1)
def catalogue():
    data = json.loads((ROOT / "tools/photo-metadata.json").read_text())
    return {photo[key]: photo for photo in data["photos"]
            for key in ("src", "thumbnail")}


@lru_cache(maxsize=1)
def brand_image():
    """Reuse the unchanged favicon for photo-free pages, not a wrong species."""
    home = (DIST / "index.html").read_text()
    icon = html.unescape(re.search(r'<link rel="icon" href="([^"]+)"', home)[1])
    if not icon.startswith("data:image/svg+xml,"):
        raise ValueError("Expected the original embedded SVG favicon")
    svg = unquote(icon.split(",", 1)[1])
    digest = hashlib.sha256(svg.encode()).hexdigest()[:12]
    path = f"/assets/social/crownwing-{digest}.png"
    target = DIST / path.lstrip("/")
    if not target.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as work:
            source = Path(work) / "favicon.svg"
            source.write_text(svg)
            subprocess.run([
                "magick", "-size", "1200x630", "xc:#f4f0e7",
                "(", "-background", "none", str(source), "-resize", "360x360", ")",
                "-gravity", "center", "-compose", "over", "-composite",
                "-strip", str(target),
            ], check=True)
    return {"src": path, "width": 1200, "height": 630,
            "label": "Crownwing Parrots brand mark"}


def social_image(text):
    parser = ImageTags()
    parser.feed(text)
    for image in parser.images:
        if "availability-thumbnail" in image.get("class", "").split():
            continue
        photo = catalogue().get(urlsplit(image.get("src", "")).path)
        if photo and photo.get("publish", True) and photo["identificationConfidence"] == "high":
            if not (DIST / photo["src"].lstrip("/")).is_file():
                raise ValueError(f'Missing social image: {photo["src"]}')
            return photo
    return brand_image()


def optimize_images(text):
    def update(match):
        parser = ImageTags()
        parser.feed(match[0])
        attrs = parser.images[0]
        source = urlsplit(attrs.get("src", "")).path
        photo = catalogue().get(source)
        if not photo:
            return match[0]
        thumbnail = source == photo["thumbnail"]
        width = photo["thumbnailWidth"] if thumbnail else photo["width"]
        height = photo["thumbnailHeight"] if thumbnail else photo["height"]
        # Explicit 44px avatar dimensions must remain unchanged.
        attrs.setdefault("width", str(width))
        attrs.setdefault("height", str(height))
        attrs.setdefault("decoding", "async")
        if (not thumbnail and not attrs.get("srcset")
                and int(attrs["width"]) > 100
                and photo["thumbnailWidth"] < photo["width"]):
            attrs["srcset"] = f'{photo["thumbnail"]} {photo["thumbnailWidth"]}w, {photo["src"]} {photo["width"]}w'
            attrs["sizes"] = "(max-width: 700px) calc(100vw - 40px), 700px"
        return "<img " + " ".join(
            key if value is None else f'{key}="{html.escape(value, quote=True)}"'
            for key, value in attrs.items()
        ) + ">"
    return re.sub(r"<img\b[^>]*>", update, text)


def identity_schema():
    brand = brand_image()
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization", "@id": PUBLIC_ORIGIN + "/#organization",
                "name": "Crownwing Parrots", "url": PUBLIC_ORIGIN + "/",
                "email": "info@crownwingparrots.co.uk",
                "description": "Crownwing Parrots is a UK parrot breeder and retailer. Current individual birds and prices are confirmed by enquiry.",
                "contactPoint": {"@type": "ContactPoint", "contactType": "Customer enquiries",
                                 "email": "info@crownwingparrots.co.uk",
                                 "url": PUBLIC_ORIGIN + "/contact/"},
                "subjectOf": {"@type": "WebPage", "url": PUBLIC_ORIGIN + "/our-approach/"},
                "logo": {"@type": "ImageObject", "url": PUBLIC_ORIGIN + brand["src"],
                         "width": brand["width"], "height": brand["height"]},
            },
            {
                "@type": "WebSite", "@id": PUBLIC_ORIGIN + "/#website",
                "url": PUBLIC_ORIGIN + "/", "name": "Crownwing Parrots",
                "inLanguage": "en-GB",
                "publisher": {"@id": PUBLIC_ORIGIN + "/#organization"},
            },
        ],
    }


def enrich_page_schema(schema, path, image):
    schema["@id"] = PUBLIC_ORIGIN + path + "#webpage"
    schema["inLanguage"] = "en-GB"
    schema["isPartOf"]["@id"] = PUBLIC_ORIGIN + "/#website"
    schema["publisher"] = {"@id": PUBLIC_ORIGIN + "/#organization"}
    schema["primaryImageOfPage"] = {
        "@type": "ImageObject", "url": PUBLIC_ORIGIN + image["src"],
        "width": image["width"], "height": image["height"],
    }
    if "breadcrumb" in schema:
        schema["breadcrumb"]["@id"] = PUBLIC_ORIGIN + path + "#breadcrumbs"
    return schema


def add_connection_hints(text):
    for host, extra in [
        ("https://fonts.googleapis.com", ""),
        ("https://fonts.gstatic.com", " crossorigin"),
    ]:
        if f'rel="preconnect" href="{host}"' not in text:
            text = text.replace("</head>", f'<link rel="preconnect" href="{host}"{extra}></head>')
    return text