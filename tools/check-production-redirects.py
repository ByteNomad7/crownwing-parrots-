"""Exercise the exact production WSGI app, not an HTML/meta-refresh substitute."""
import json
import sys
import unittest
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.production_site import app, DIST
from tools.route_rules import REDIRECTS
from tools.site_config import PUBLIC_ORIGIN
from flask.testing import FlaskClient


class BufferedClient(FlaskClient):
    def open(self, *args, **kwargs):
        kwargs.setdefault("buffered", True)
        return super().open(*args, **kwargs)


class ProductionRedirectTests(unittest.TestCase):
    def setUp(self):
        app.test_client_class = BufferedClient
        self.client = app.test_client()

    def test_all_13_routes_and_aliases_preserve_query_without_chains(self):
        for source, target in REDIRECTS.items():
            for alias in (source, source.rstrip("/"), source + "index.html"):
                for method in ("GET", "HEAD"):
                    with self.subTest(alias=alias, method=method):
                        response = self.client.open(alias + "?from=saved&keep=a%2Fb", method=method)
                        self.assertEqual(response.status_code, 301)
                        self.assertEqual(response.headers["Location"], target + "?from=saved&keep=a%2Fb")
                        destination = self.client.get(response.headers["Location"])
                        self.assertEqual(destination.status_code, 200)
                        self.assertNotIn("Location", destination.headers)
                self.assertFalse((DIST / source.strip("/") / "index.html").exists())

    def test_host_protocol_and_merge_are_one_hop(self):
        for source, target in REDIRECTS.items():
            for alias in (source, source.rstrip("/"), source + "index.html"):
                response = self.client.get(alias + "?keep=1", headers={
                    "Host": "www." + urlsplit(PUBLIC_ORIGIN).hostname,
                    "X-Forwarded-Proto": "http",
                })
                self.assertEqual(response.status_code, 301)
                self.assertEqual(response.headers["Location"], PUBLIC_ORIGIN + target + "?keep=1")
        forwarded = self.client.get("/locations/london/", headers={
            "Host": "preview.replit.dev", "X-Forwarded-Host": urlsplit(PUBLIC_ORIGIN).hostname,
            "X-Forwarded-Proto": "http",
        })
        self.assertEqual(forwarded.headers["Location"], PUBLIC_ORIGIN + REDIRECTS["/locations/london/"])

    def test_index_and_slash_aliases_for_every_surviving_page(self):
        for file in DIST.rglob("index.html"):
            relative = file.parent.relative_to(DIST).as_posix()
            route = "/" if relative == "." else "/" + relative + "/"
            response = self.client.get(route + "index.html?x=1")
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response.headers["Location"], route + "?x=1")
            if route != "/":
                self.assertEqual(self.client.get(route.rstrip("/")).headers["Location"], route)
            self.assertEqual(self.client.get(route).status_code, 200)

    def test_real_robots_xml_sitemap_and_belfast(self):
        robots = self.client.get("/robots.txt")
        self.assertEqual(robots.status_code, 200)
        self.assertTrue(robots.data.startswith(b"User-agent:"))
        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertTrue(sitemap.data.startswith(b"<?xml"))
        self.assertEqual(sitemap.data.count(b"<loc>"), 56)
        for source in REDIRECTS:
            self.assertNotIn((PUBLIC_ORIGIN + source + "</loc>").encode(), sitemap.data)
        self.assertEqual(self.client.get("/locations/belfast/").status_code, 200)

    def test_private_files_traversal_and_unknown_paths_not_served(self):
        for path in ("/seo/crownwing-classification-before.json", "/../.replit", "/%2e%2e/.replit",
                     "/site/redirects.json", "/assets/", "/not-real/", "/.replit"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 404)
                self.assertIn(b"<!doctype html", response.data.lower())
        self.assertEqual(self.client.post("/contact/", data={"name": "not stored"}).status_code, 405)
        self.assertEqual(self.client.get("/", headers={"Host": "untrusted.invalid",
            "X-Forwarded-Host": "evil.invalid", "X-Forwarded-Proto": "http"}).status_code, 200)

    def test_no_internal_retired_url_links_and_managed_content_present(self):
        from tools.content_registry import ContentParser
        for file in DIST.rglob("index.html"):
            parser = ContentParser()
            parser.feed(file.read_text())
            for link in parser.links:
                self.assertNotIn(urlsplit(link["href"]).path, REDIRECTS)
        for target in set(REDIRECTS.values()):
            self.assertIn('id="approved-city-consolidation"', (DIST / target.strip("/") / "index.html").read_text())
        self.assertEqual(len(list(DIST.rglob("index.html"))), 56)


if __name__ == "__main__":
    unittest.main(verbosity=2)