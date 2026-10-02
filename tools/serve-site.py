#!/usr/bin/env python3
"""Serve the generated static site with canonical URL and error handling."""

from __future__ import annotations

import argparse
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

try:
    from site_config import PUBLIC_ORIGIN
except ImportError:  # Imported as tools.serve_site from a package-aware caller.
    from tools.site_config import PUBLIC_ORIGIN


CANONICAL_HOST = urlsplit(PUBLIC_ORIGIN).hostname
WWW_HOST = f"www.{CANONICAL_HOST}"
KNOWN_PUBLIC_HOSTS = frozenset({CANONICAL_HOST, WWW_HOST})
IMAGE_EXTENSIONS = frozenset({".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"})


def _brand_fragments(homepage: str) -> tuple[str, str]:
    header = re.search(r"<header\b[^>]*>.*?</header>", homepage, flags=re.I | re.S)
    footer = re.search(r"<footer\b[^>]*>.*?</footer>", homepage, flags=re.I | re.S)
    if not header or not footer:
        raise ValueError("dist/index.html must contain the site's branded header and footer")
    return header.group(0), footer.group(0)


def make_handler(directory: str | Path) -> type[SimpleHTTPRequestHandler]:
    """Build a handler bound to a validated site directory; safe to use in tests."""
    root = Path(directory).resolve()
    home_path = root / "index.html"
    if not root.is_dir() or not home_path.is_file():
        raise FileNotFoundError(f"Static site root must contain index.html: {root}")
    header, footer = _brand_fragments(home_path.read_text(encoding="utf-8"))

    class SiteRequestHandler(SimpleHTTPRequestHandler):
        site_root = root
        branded_header = header
        branded_footer = footer

        def __init__(self, *args, **kwargs):
            kwargs.setdefault("directory", str(self.site_root))
            super().__init__(*args, **kwargs)

        def log_message(self, format, *args):
            # Keep the default server output concise and avoid logging request data.
            super().log_message(format, *args)

        def end_headers(self):
            path = urlsplit(self.path).path.lower()
            suffix = Path(path).suffix
            if suffix in {".html", ".htm", ".css", ".js", ".mjs"} or self._status in {301, 302, 404}:
                self.send_header("Cache-Control", "no-cache")
            elif suffix in IMAGE_EXTENSIONS:
                self.send_header("Cache-Control", "public, max-age=3600")
            self.send_header("X-Content-Type-Options", "nosniff")
            super().end_headers()

        def send_response(self, code, message=None):
            self._status = code
            super().send_response(code, message)

        def _request_hostname(self) -> str | None:
            host = self.headers.get("Host", "").strip().lower()
            forwarded_host = self.headers.get("X-Forwarded-Host", "").split(",", 1)[0].strip().lower()

            def hostname(value: str) -> str | None:
                if not value or "@" in value or "/" in value or "\\" in value:
                    return None
                parsed = urlsplit("//" + value)
                if parsed.path or parsed.query or parsed.fragment:
                    return None
                return parsed.hostname

            direct = hostname(host)
            if direct in KNOWN_PUBLIC_HOSTS:
                return direct
            forwarded = hostname(forwarded_host)
            return forwarded if forwarded in KNOWN_PUBLIC_HOSTS else None

        def _target_for_request(self) -> tuple[str | None, bool]:
            """Return a redirect location, if needed, and whether it is absolute."""
            parts = urlsplit(self.path)
            request_path = parts.path or "/"
            target_path = request_path
            from route_rules import merged_target
            target_path = merged_target(request_path) or target_path

            # Only redirect a real index document inside this site, preventing
            # malformed or traversal-like requests from becoming aliases.
            if request_path.endswith("/index.html") or request_path == "/index.html":
                candidate_path = request_path[: -len("index.html")]
                if not candidate_path:
                    candidate_path = "/"
                disk_path = (self.site_root / candidate_path.lstrip("/")).resolve()
                try:
                    disk_path.relative_to(self.site_root)
                    safe = (disk_path / "index.html").is_file()
                except ValueError:
                    safe = False
                if safe:
                    target_path = candidate_path

            # Retain SimpleHTTPRequestHandler's useful directory slash fix,
            # while making its query-string behavior explicit.
            if not target_path.endswith("/"):
                disk_path = (self.site_root / target_path.lstrip("/")).resolve()
                try:
                    disk_path.relative_to(self.site_root)
                    is_directory = disk_path.is_dir()
                except ValueError:
                    is_directory = False
                if is_directory:
                    target_path += "/"

            known_host = self._request_hostname()
            if known_host == WWW_HOST:
                return urlunsplit((urlsplit(PUBLIC_ORIGIN).scheme, urlsplit(PUBLIC_ORIGIN).netloc, target_path, parts.query, "")), True

            forwarded_proto = self.headers.get("X-Forwarded-Proto", "").split(",", 1)[0].strip().lower()
            if known_host == CANONICAL_HOST and forwarded_proto == "http":
                origin = urlsplit(PUBLIC_ORIGIN)
                return urlunsplit((origin.scheme, origin.netloc, target_path, parts.query, "")), True

            if target_path != request_path:
                return urlunsplit(("", "", target_path, parts.query, "")), False
            return None, False

        def _maybe_redirect(self) -> bool:
            location, _absolute = self._target_for_request()
            if location is None:
                return False
            self.send_response(301)
            self.send_header("Location", location)
            self.end_headers()
            return True

        def do_GET(self):
            if not self._maybe_redirect():
                super().do_GET()

        def do_HEAD(self):
            if not self._maybe_redirect():
                super().do_HEAD()

        def list_directory(self, path):
            self.send_error(404)
            return None

        def send_error(self, code, message=None, explain=None):
            if code != 404:
                return super().send_error(code, message, explain)
            body = (
                "<!doctype html><html lang=\"en-GB\"><head><meta charset=\"utf-8\">"
                "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
                "<meta name=\"robots\" content=\"noindex,follow\">"
                "<title>Page not found | Crownwing Parrots</title>"
                "<link rel=\"stylesheet\" href=\"/style.css\"></head><body>"
                + self.branded_header
                + "<main><section class=\"not-found\"><p class=\"eyebrow\">404</p>"
                "<h1>Page not found</h1><p>We couldn’t find the page you were looking for.</p>"
                "<a class=\"button lime\" href=\"/\">Return to the homepage</a></section></main>"
                + self.branded_footer
                + "</body></html>"
            ).encode("utf-8")
            self.send_response(404, "Not Found")
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

    return SiteRequestHandler


def create_server(directory: str | Path = "dist", bind: str = "0.0.0.0", port: int = 5000) -> ThreadingHTTPServer:
    handler = make_handler(directory)
    server = ThreadingHTTPServer((bind, port), handler)
    server.daemon_threads = True
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--bind", default="0.0.0.0")
    parser.add_argument("--directory", default="dist")
    args = parser.parse_args()
    server = create_server(args.directory, args.bind, args.port)
    print(f"Serving {Path(args.directory).resolve()} at http://{args.bind}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()