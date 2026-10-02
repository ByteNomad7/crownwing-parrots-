"""Check editorial differentiation, species hierarchy and preservation contracts."""

import argparse
import html
import json
import re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

from breeder_content import DISPLAY_NAMES, SALE_SLUGS

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
INSTRUCTION_CLASSES = {
    "detail-cta", "related", "location-note", "guide-sources", "group-note", "gallery-note",
    "gallery-caption", "photo-dialog-caption", "city-enquiry", "contact-form-panel", "enquiry-status-note",
}


class Parse(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.paragraphs, self.links, self.images, self.forms = [], [], [], [], []
        self.ids, self.headings, self.meta, self.capture = [], [], {}, None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set(attrs.get("class", "").split())
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        elif tag == "img":
            self.images.append(attrs.get("src", ""))
        elif tag == "form":
            self.forms.append(attrs)
        elif tag == "meta":
            self.meta[attrs.get("property", attrs.get("name", ""))] = attrs.get("content", "")
        if tag in {"h1", "h2", "h3"}:
            self.headings.append(int(tag[1]))
        if tag == "p" and any(t == "main" for t, _ in self.stack):
            inherited = classes | set().union(*(c for _, c in self.stack))
            self.capture = [] if not inherited & INSTRUCTION_CLASSES else None
        if tag not in VOID:
            self.stack.append((tag, classes))

    def handle_data(self, value):
        if self.capture is not None:
            self.capture.append(value)

    def handle_endtag(self, tag):
        if tag == "p" and self.capture is not None:
            paragraph = " ".join(" ".join(self.capture).split())
            if len(paragraph.split()) >= 20 and not paragraph.startswith("This is a species and care guide"):
                self.paragraphs.append(paragraph)
            self.capture = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                self.stack = self.stack[:i]
                break


def collect():
    pages = {}
    for target in DIST.rglob("index.html"):
        path = "/" if target.parent == DIST else "/" + target.parent.relative_to(DIST).as_posix() + "/"
        text = target.read_text()
        parser = Parse()
        parser.feed(text)
        pages[path] = (text, parser)
    occurrences = defaultdict(set)
    for path, (_, parser) in pages.items():
        for paragraph in parser.paragraphs:
            occurrences[paragraph].add(path)
    duplicates = {p: sorted(paths) for p, paths in occurrences.items() if len(paths) > 1}
    return pages, duplicates


def check():
    pages, duplicates = collect()
    assert not duplicates, ("Repeated substantive body paragraphs", duplicates)
    profiles = json.loads((ROOT / "tools/individual-species-content.json").read_text())
    categories = json.loads((ROOT / "tools/category-content.json").read_text())
    for group in DISPLAY_NAMES:
        for prefix, slug in [("/parrots/", group), ("/parrots-for-sale/", SALE_SLUGS[group])]:
            path = prefix + slug + "/"
            text, parser = pages[path]
            assert len(" ".join(parser.paragraphs).split()) >= 350, (path, "thin editorial content")
            for profile in profiles:
                if profile["parent"] == group:
                    assert "/parrots/" + group + "/" + profile["slug"] + "/" in parser.links, (path, profile["slug"])
        guide = pages["/parrots/" + group + "/"][1]
        for anchor in ["lifespan", "diet", "temperament", "housing", "noise", "suitability"]:
            assert anchor in guide.ids, (group, "legacy fragment", anchor)
        assert len(categories[group]["guide_sections"]) >= 6
    for profile in profiles:
        path = "/parrots/" + profile["parent"] + "/" + profile["slug"] + "/"
        text, parser = pages[path]
        assert "/parrots/" + profile["parent"] + "/" in parser.links, (path, "parent link")
        assert len(parser.images) <= 4, (path, "four-photo provision")
        for topic in ["adult-size", "lifespan", "vocalisation", "training", "diet", "housing"]:
            assert topic in parser.ids, (path, "missing ownership topic", topic)
        assert len(" ".join(parser.paragraphs).split()) >= 350, (path, "thin species profile")
        assert "NOT A STOCK LISTING" in text, (path, "inventory ambiguity")
    for path, (text, parser) in pages.items():
        assert len(parser.ids) == len(set(parser.ids)), (path, "duplicate ids")
        assert parser.headings.count(1) == 1, (path, "H1 count")
        for before, after in zip(parser.headings, parser.headings[1:]):
            assert after <= before + 1, (path, "skipped heading level", before, after)
        title = html.unescape(re.search(r"<title>(.*?)</title>", text)[1])
        assert parser.meta["og:title"] == title, (path, "OG title")
        assert parser.meta["og:description"] == parser.meta["description"], (path, "OG description")
        canonical = html.unescape(re.search(r'<link rel="canonical" href="([^"]+)"', text)[1])
        assert parser.meta["og:url"] == canonical, (path, "OG canonical mismatch")
        if path.startswith("/locations/") and path != "/locations/":
            assert parser.meta.get("robots") == "index,follow", (path, "city indexing policy")
            assert len(" ".join(parser.paragraphs).split()) >= 350, (path, "thin regional content")
            assert len(parser.forms) == 1 and "local-enquiry-form" in parser.forms[0]["class"], (path, "form lost")
    baseline = Path("/tmp/crownwing-content-before.json")
    if baseline.exists():
        for path, old in json.loads(baseline.read_text()).items():
            assert path in pages, ("Existing route lost", path)
            text, parser = pages[path]
            assert set(old["links"]) <= set(parser.links), (path, "internal links removed", set(old["links"]) - set(parser.links))
            assert set(old["images"]) <= set(parser.images), (path, "images removed")
            assert old["forms"] == parser.forms, (path, "form hooks changed")
            assert old["brand"] == re.findall(r'<a[^>]*class="brand".*?</a>', text, re.S), (path, "branding changed")
            if not (path.startswith("/locations/") and path != "/locations/"):
                assert old["noindex"] == ("noindex" in text), (path, "robots policy changed")
    print(json.dumps({
        "pages_checked": len(pages), "individual_species_profiles": len(profiles),
        "group_and_buying_links": "bidirectional, passed", "legacy_fragments": "preserved",
        "repeated_substantive_body_paragraphs": len(duplicates),
        "social_metadata_matches_page": True, "semantic_headings_and_unique_ids": "passed",
        "original_routes_images_forms_links_and_brand": "passed" if baseline.exists() else "baseline unavailable; structural checks passed",
        "city_guides": "index,follow; distinct regional bodies and forms checked",
    }, indent=2))


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--baseline", action="store_true")
    if args.parse_args().baseline:
        pages, duplicates = collect()
        print(json.dumps({"pages": len(pages), "repeated_substantive_body_paragraphs": len(duplicates),
                          "examples": [{"text": p, "pages": paths} for p, paths in list(duplicates.items())[:4]]}, indent=2))
    else:
        check()