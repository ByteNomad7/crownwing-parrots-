#!/usr/bin/env python3
"""Exercise static HTTP behavior locally, with an optional live-origin check."""

from __future__ import annotations

import argparse
import http.client
import importlib.util
import re
import threading
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SPEC = importlib.util.spec_from_file_location("serve_site", ROOT / "tools" / "serve-site.py")
serve_site = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(serve_site)


class StaticHttpFoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = serve_site.create_server(DIST, "127.0.0.1", 0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self, path, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        connection.request("GET", path, headers=headers or {})
        response = connection.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return result

    def test_every_real_index_document_has_a_single_hop_alias(self):
        index_files = sorted(DIST.rglob("index.html"))
        self.assertTrue(index_files, "No generated pages found")
        for index_file in index_files:
            relative = index_file.parent.relative_to(DIST).as_posix()
            route = "/" if relative == "." else f"/{relative}/"
            alias = f"{route}index.html" if route != "/" else "/index.html"
            with self.subTest(alias=alias):
                status, headers, _ = self.request(alias + "?from=foundation&keep=1")
                self.assertEqual(status, 301)
                self.assertEqual(headers.get("Location"), route + "?from=foundation&keep=1")

    def test_directory_slash_correction_preserves_query(self):
        status, headers, _ = self.request("/guides/choosing-a-parrot?source=test")
        self.assertEqual(status, 301)
        self.assertEqual(headers.get("Location"), "/guides/choosing-a-parrot/?source=test")

    def test_known_www_host_redirects_to_public_origin(self):
        status, headers, _ = self.request(
            "/guides/choosing-a-parrot/?q=hello",
            {"Host": "www.crownwingparrots.co.uk"},
        )
        self.assertEqual(status, 301)
        self.assertEqual(
            headers.get("Location"),
            "https://crownwingparrots.co.uk/guides/choosing-a-parrot/?q=hello",
        )

    def test_allowlisted_forwarded_host_is_recognized(self):
        status, headers, _ = self.request(
            "/?via=proxy",
            {
                "Host": "preview.internal",
                "X-Forwarded-Host": "www.crownwingparrots.co.uk",
            },
        )
        self.assertEqual(status, 301)
        self.assertEqual(headers.get("Location"), "https://crownwingparrots.co.uk/?via=proxy")

    def test_canonical_http_forwarded_proto_redirects_to_https(self):
        status, headers, _ = self.request(
            "/?campaign=spring",
            {"Host": "crownwingparrots.co.uk", "X-Forwarded-Proto": "http"},
        )
        self.assertEqual(status, 301)
        self.assertEqual(headers.get("Location"), "https://crownwingparrots.co.uk/?campaign=spring")

    def test_preview_hosts_are_not_redirected_or_trusted_as_targets(self):
        status, headers, body = self.request(
            "/",
            {
                "Host": "workspace.example.replit.dev",
                "X-Forwarded-Proto": "http",
                "X-Forwarded-Host": "attacker.invalid",
            },
        )
        self.assertEqual(status, 200)
        self.assertNotIn("Location", headers)
        self.assertIn(b"<h1>", body)

    def test_missing_page_and_directory_listing_return_branded_404(self):
        for path in ("/not-a-real-page-for-http-test/", "/assets/"):
            with self.subTest(path=path):
                status, headers, body = self.request(path)
                self.assertEqual(status, 404)
                self.assertIn("noindex,follow", body.decode("utf-8"))
                self.assertIn(b"CROWN WING", body)
                self.assertIn(b"Page not found", body)
                self.assertNotIn(path.encode(), body)
                self.assertEqual(headers.get("Content-Type"), "text/html; charset=utf-8")

    def test_real_robots_sitemap_and_page_heading_are_served(self):
        for path in ("/robots.txt", "/sitemap.xml"):
            with self.subTest(path=path):
                status, _, body = self.request(path, {"Host": "crownwingparrots.co.uk"})
                self.assertEqual(status, 200)
                self.assertTrue(body)

        status, headers, body = self.request(
            "/guides/choosing-a-parrot/",
            {"Host": "crownwingparrots.co.uk"},
        )
        self.assertEqual(status, 200)
        content_type = next(value for name, value in headers.items() if name.lower() == "content-type")
        self.assertIn("text/html", content_type)
        self.assertRegex(body.decode("utf-8"), r"<h1\b[^>]*>.+?</h1>")

    def test_server_rejects_a_site_root_without_homepage(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                serve_site.make_handler(directory)


def run_live_check(base_url: str) -> None:
    base_url = base_url.rstrip("/") + "/"
    for path in ("", "robots.txt", "sitemap.xml", "guides/choosing-a-parrot/"):
        url = urljoin(base_url, path)
        request = Request(url, headers={"User-Agent": "CrownwingHttpFoundationCheck/1.0"})
        try:
            with urlopen(request, timeout=15) as response:
                body = response.read().decode("utf-8", errors="replace")
                if response.status != 200:
                    raise AssertionError(f"{url}: expected HTTP 200, got {response.status}")
                if path.startswith("guides/") and not re.search(r"<h1\b[^>]*>.+?</h1>", body, re.S):
                    raise AssertionError(f"{url}: expected a rendered page heading")
                print(f"PASS {response.status} {response.geturl()}")
        except (HTTPError, URLError) as error:
            raise SystemExit(f"Live HTTP check failed for {url}: {error}") from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live-url",
        help="also check the running public/proxy URL, e.g. https://$REPLIT_DEV_DOMAIN",
    )
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(StaticHttpFoundationTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    if args.live_url:
        run_live_check(args.live_url)


if __name__ == "__main__":
    main()