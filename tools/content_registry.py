"""Substantive-content history for the static Crownwing site."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "seo" / "content-register.json"
BASELINE = ROOT / "seo" / "content-baseline.json"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
CHROME = {"header", "nav", "footer", "aside", "script", "style"}
EXCLUDED = {"related", "detail-cta", "location-note", "gallery-note", "gallery-caption", "photo-dialog-caption",
            "city-enquiry", "contact-form-panel", "privacy-form-note", "guide-sources", "availability-note"}


class ContentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.paragraphs = []
        self.headings = []
        self.images = []
        self.image_records = []
        self.links = []
        self.body_fragments = []
        self._capture = None
        self._main_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set(attrs.get("class", "").split())
        excluded = tag in CHROME or bool(classes & EXCLUDED)
        in_main = any(item[2] for item in self.stack)
        active = in_main and not excluded and not any(item[3] for item in self.stack)
        if tag == "main":
            active = True
        if tag == "img" and active:
            self.images.append(attrs.get("src", ""))
            self.image_records.append({"src": attrs.get("src", ""), "alt": attrs.get("alt")})
        if tag == "a":
            self.links.append({"href": attrs.get("href", ""), "main": active})
        if tag == "p" and active:
            self._capture = []
        if tag in {"h1", "h2", "h3", "h4"} and active:
            self._heading_capture = tag
            self._heading_text = []
        if tag not in VOID:
            self.stack.append((tag, classes, active, excluded))

    def handle_data(self, data):
        if self.stack and self.stack[-1][2] and not any(item[3] for item in self.stack):
            self.body_fragments.append(data)
        if self._capture is not None:
            self._capture.append(data)
        if getattr(self, "_heading_capture", None):
            self._heading_text.append(data)

    def handle_endtag(self, tag):
        if tag == "p" and self._capture is not None:
            value = " ".join(" ".join(self._capture).split())
            if value:
                self.paragraphs.append(value)
            self._capture = None
        if tag == getattr(self, "_heading_capture", None):
            value = " ".join(" ".join(self._heading_text).split())
            if value:
                self.headings.append(value)
            self._heading_capture = None
            self._heading_text = []
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def extract_content(html):
    parser = ContentParser()
    parser.feed(html)
    paragraphs = parser.paragraphs
    body = "\n".join(parser.headings + paragraphs)
    images = sorted(set(parser.images))
    legacy_digest = hashlib.sha256((body + "\nIMAGES\n" + "\n".join(images)).encode("utf-8")).hexdigest()
    # Tables, lists and form explanations are substantive content too.
    content_text = " ".join(" ".join(parser.body_fragments).split())
    evidence = json.dumps(parser.image_records, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256((content_text + "\nIMAGES\n" + evidence).encode("utf-8")).hexdigest()
    return {"paragraphs": paragraphs, "headings": parser.headings, "images": images,
            "image_evidence": parser.image_records,
            "links": parser.links, "digest": digest, "legacy_digest": legacy_digest}


def discover_pages(dist):
    pages = {}
    for file in Path(dist).rglob("index.html"):
        relative = file.parent.relative_to(dist).as_posix()
        path = "/" if relative == "." else "/" + relative.rstrip("/") + "/"
        pages[path] = file
    return pages


def _source_links(html):
    links = []
    main = re.search(r"<main\b[^>]*>(.*?)</main\s*>", html, re.I | re.S)
    source_html = main.group(1) if main else ""
    for match in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', source_html, re.I | re.S):
        href = match.group(1).strip()
        parsed = urlsplit(href)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            label = re.sub(r"<[^>]+>", " ", match.group(2))
            links.append({"url": href, "label": " ".join(label.split())})
    return links


def _article_dates(html):
    """Return genuine publication/modification dates only for Article JSON-LD."""
    result = {"published": None, "modified": None}
    for match in re.finditer(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script\s*>',
        html, re.I | re.S,
    ):
        try:
            value = json.loads(match.group(1))
        except (ValueError, TypeError):
            continue
        candidates = value if isinstance(value, list) else [value]
        for item in candidates:
            if not isinstance(item, dict):
                continue
            types = item.get("@type", [])
            types = types if isinstance(types, list) else [types]
            if not set(types) & {"Article", "BlogPosting", "NewsArticle", "TechArticle", "ScholarlyArticle"}:
                continue
            published = item.get("datePublished")
            if isinstance(published, str):
                try:
                    result["published"] = date.fromisoformat(published[:10]).isoformat()
                except ValueError:
                    pass
            modified = item.get("dateModified")
            if isinstance(modified, str):
                try:
                    result["modified"] = date.fromisoformat(modified[:10]).isoformat()
                except ValueError:
                    pass
    return result


def _new_record(path, info, html, observed):
    return {
        "path": path, "content_digest": info["digest"], "digest_version": 2, "publisher": "Crownwing",
        "published": _article_dates(html)["published"],
        "article_date_modified": _article_dates(html)["modified"],
        "owner": {"organisation": "Crownwing Parrots", "person": None, "role": "Publisher"},
        "sources": _source_links(html), "last_modified": observed,
        "last_reviewed": None, "reviewed_by": None, "review_scope": None,
        "review_status": None,
        "review_reminder_due": None, "history": (
            [{"date": observed, "event": "New route observed", "digest": info["digest"]}]
            if observed else []
        ),
    }


def sync_content_registry(dist):
    """Synchronise observed body content without treating template rebuilds as edits."""
    today = date.today().isoformat()
    pages = discover_pages(dist)
    existing = {}
    if REGISTRY.exists():
        try:
            existing = {entry["path"]: entry for entry in json.loads(REGISTRY.read_text()).get("pages", [])}
        except (ValueError, OSError, KeyError, TypeError):
            existing = {}
    baseline = {}
    if BASELINE.exists():
        try:
            baseline = json.loads(BASELINE.read_text()).get("pages", {})
        except (ValueError, OSError, TypeError):
            baseline = {}
    result = {}
    for path, file in sorted(pages.items()):
        html = file.read_text(encoding="utf-8")
        info = extract_content(html)
        record = existing.get(path)
        if not record:
            old = baseline.get(path)
            if old:
                changed = old["digest"] != info["legacy_digest"]
                record = _new_record(path, info, html, today if changed else None)
                record["history"] = ([{
                    "date": today, "event": "Substantive change compared with captured baseline",
                    "previous_digest": old["digest"], "digest": info["digest"],
                }] if changed else [])
            else:
                record = _new_record(path, info, html, today)
        else:
            expected = info["digest"] if record.get("digest_version") == 2 else info["legacy_digest"]
            # Rebase old fingerprints without inventing an editorial change date.
            if record.get("content_digest") != expected:
                record.setdefault("history", []).append({
                    "date": today, "event": "Substantive body text or image change observed",
                    "previous_digest": record.get("content_digest"), "digest": info["digest"],
                })
                record["last_modified"] = today
        record["content_digest"] = info["digest"]
        record["digest_version"] = 2
        # Sources describe the current authored content; this is not an editorial review.
        record["sources"] = _source_links(html)
        article_dates = _article_dates(html)
        record["published"] = article_dates["published"]
        record["article_date_modified"] = article_dates["modified"]
        checked = None
        body_text = " ".join(info["headings"] + info["paragraphs"])
        review_match = re.search(
            r"\bSources?\s+checked\s*:?\s*(\d{4}-\d{2}-\d{2})\b", body_text, re.I
        )
        if review_match:
            try:
                checked = date.fromisoformat(review_match.group(1)).isoformat()
            except ValueError:
                checked = None
        if checked and checked != record.get("last_reviewed"):
            record["last_reviewed"] = checked
            record["reviewed_by"] = None
            record["review_scope"] = "Source references checked; no expert review implied"
            record["review_status"] = "sources_checked"
            record.setdefault("history", []).append({
                "date": checked, "event": "Editorial source references checked",
                "review_scope": "sources_checked",
            })
        elif "review_status" not in record:
            record["review_status"] = None
        reviewed = record.get("last_reviewed")
        reminder = None
        if reviewed:
            reviewed_date = date.fromisoformat(reviewed)
            month_index = reviewed_date.year * 12 + reviewed_date.month - 1 + 6
            year, month = divmod(month_index, 12)
            month += 1
            import calendar
            reminder = date(year, month, min(reviewed_date.day, calendar.monthrange(year, month)[1])).isoformat()
        record["review_reminder_due"] = (
            reminder
        )
        result[path] = record
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps({"publisher": "Crownwing", "pages": list(result.values())},
                                   indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def write_sitemap(dist, origin, paths):
    """Write a sitemap into the supplied dist directory for generator integration."""
    records = {}
    try:
        records = {entry["path"]: entry for entry in json.loads(REGISTRY.read_text()).get("pages", [])}
    except (ValueError, OSError, KeyError, TypeError):
        pass
    nodes = []
    for path in sorted(set(paths)):
        entry = f"<loc>{escape(origin.rstrip('/') + path)}</loc>"
        modified = records.get(path, {}).get("last_modified")
        if modified:
            entry += f"<lastmod>{escape(modified)}</lastmod>"
        nodes.append("<url>" + entry + "</url>")
    Path(dist, "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(nodes) + "</urlset>", encoding="utf-8")