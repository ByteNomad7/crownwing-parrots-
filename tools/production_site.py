"""Production WSGI static-file service; run through Gunicorn, never Flask debug."""
from pathlib import Path
from urllib.parse import urlsplit

from flask import Flask, Response, request, send_file
from .route_rules import REDIRECTS, merged_target
from .site_config import PUBLIC_ORIGIN
from .static_hosting import not_found_page

DIST = Path(__file__).resolve().parents[1] / "dist"
ORIGIN = urlsplit(PUBLIC_ORIGIN)
PUBLIC_HOSTS = {ORIGIN.hostname, "www." + ORIGIN.hostname}
app = Flask(__name__, static_folder=None)
app.url_map.merge_slashes = False
NOT_FOUND_PAGE = not_found_page((DIST / "index.html").read_text())


def request_public_host():
    def hostname(value):
        return urlsplit("//" + value.split(",", 1)[0].strip()).hostname
    direct = hostname(request.host)
    if direct in PUBLIC_HOSTS:
        return direct
    forwarded = hostname(request.headers.get("X-Forwarded-Host", ""))
    return forwarded if forwarded in PUBLIC_HOSTS else None


def file_path(path):
    candidate = (DIST / path.lstrip("/")).resolve()
    try:
        candidate.relative_to(DIST)
    except ValueError:
        return None
    return candidate


def redirect_location(path):
    target = merged_target(path)
    if target is None:
        target = path
        if path.endswith("/index.html"):
            folder = file_path(path[:-len("index.html")])
            if folder is not None and (folder / "index.html").is_file():
                target = path[:-len("index.html")]
        candidate = file_path(target)
        if candidate is not None and candidate.is_dir() and not target.endswith("/"):
            target += "/"
    host = request_public_host()
    proto = request.headers.get("X-Forwarded-Proto", "").split(",", 1)[0].strip().lower()
    absolute = host == "www." + ORIGIN.hostname or (host == ORIGIN.hostname and proto == "http")
    if target == path and not absolute:
        return None
    query = request.query_string.decode("latin1")
    return (PUBLIC_ORIGIN if absolute else "") + target + ("?" + query if query else "")


@app.route("/", defaults={"path": ""}, methods=["GET", "HEAD"])
@app.route("/<path:path>", methods=["GET", "HEAD"])
def serve(path):
    location = redirect_location(request.path)
    if location is not None:
        return Response(status=301, headers={"Location": location, "Cache-Control": "public, max-age=300"})
    candidate = file_path(path)
    if candidate is not None and candidate.is_dir():
        candidate = candidate / "index.html"
    if candidate is None or not candidate.is_file() or any(part.startswith(".") for part in Path(path).parts):
        return not_found(None)
    response = send_file(candidate, conditional=True, max_age=3600 if candidate.suffix != ".html" else 0)
    if candidate.suffix == ".html":
        response.headers["Cache-Control"] = "no-cache"
    return response


@app.errorhandler(404)
def not_found(_error):
    response = Response(NOT_FOUND_PAGE, status=404, content_type="text/html; charset=utf-8")
    response.headers["Cache-Control"] = "no-store"
    return response


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


# Invalid deployments fail on startup rather than accepting broken merge rules.
for target in set(REDIRECTS.values()):
    assert (DIST / target.strip("/") / "index.html").is_file(), f"Missing redirect target: {target}"