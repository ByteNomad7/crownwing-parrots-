"""Generate static-host routing files from the same approved production rules."""
import re
from pathlib import Path
from urllib.parse import urlsplit, urljoin

if __package__:
    from .route_rules import REDIRECTS
else:
    from route_rules import REDIRECTS

DIST = Path(__file__).resolve().parents[1] / "dist"


def not_found_page(home):
    page = re.sub(r"<main\b[^>]*>.*?</main>", """<main class="content-page">
<section class="page-intro"><p class="eyebrow">CROWNWING PARROTS</p><h1>Page not found</h1>
<p>We couldn’t find the page you were looking for.</p><a class="button lime" href="/">Return to the homepage</a>
</section></main>""", home, count=1, flags=re.S)
    page = re.sub(r"<title>.*?</title>", "<title>Page not found | Crownwing Parrots</title>", page, flags=re.S)
    page = re.sub(r'<script type="application/ld\+json"[^>]*>.*?</script>', "", page, flags=re.S)
    page = re.sub(r'<link rel="canonical"[^>]*>|<meta (?:property="og:[^"]*"|name="(?:robots|description|twitter:[^"]*)")[^>]*>', "", page)
    # A 404 is rendered at the requested URL, often several directories deep.
    # Homepage-relative assets must resolve from the site root, not that URL.
    def root_reference(match):
        value = match[2]
        if not value.startswith(("/", "#")) and not urlsplit(value).scheme:
            value = urljoin("/", value)
        return match[1] + value + match[3]
    page = re.sub(r'(\b(?:src|href)=")([^"]+)(")', root_reference, page)
    return page.replace("</head>", '<meta name="robots" content="noindex,follow"></head>')


def generate_static_hosting():
    rules = ["# Generated from site/redirects.json. Netlify preserves query strings.",
             "# Netlify matches trailing-slash and slashless paths equivalently.",
             "# Do not add a /* /index.html 200 SPA fallback: this is a multi-page site."]
    for source, target in REDIRECTS.items():
        rules += [f"{source} {target} 301!", f"{source}index.html {target} 301!"]
    for file in sorted(DIST.rglob("index.html")):
        relative = file.parent.relative_to(DIST).as_posix()
        route = "/" if relative == "." else "/" + relative + "/"
        rules.append(f"{route}index.html {route} 301!")
    (DIST / "_redirects").write_text("\n".join(rules) + "\n")
    (DIST / "404.html").write_text(not_found_page((DIST / "index.html").read_text()))