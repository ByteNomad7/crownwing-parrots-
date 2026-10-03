"""Validate the deploy payload/config, not a claim of testing Netlify's live CDN."""
import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
config = tomllib.loads((ROOT / "netlify.toml").read_text())
assert config["build"]["publish"] == "dist"
assert config["build"]["command"] == "npm run build"
assert config["build"]["environment"]["NPM_FLAGS"] == "--omit=dev"
assert config["build"]["environment"]["NPM_CONFIG_REGISTRY"] == "https://registry.npmjs.org"
lock_text = (ROOT / "package-lock.json").read_text()
assert "replit.internal" not in lock_text, "External hosts cannot resolve Replit-only package URLs"
lock = json.loads(lock_text)
assert not json.loads((ROOT / "package.json").read_text()).get("dependencies"), "Review omit=dev if runtime npm dependencies are added"
for package in lock["packages"].values():
    if "resolved" in package:
        assert package["resolved"].startswith("https://registry.npmjs.org/"), "Nonportable npm archive URL"
assert config["build"]["processing"]["html"]["pretty_urls"] is True
assert (DIST / "index.html").is_file()
assert (DIST / "assets").is_dir()
redirects = json.loads((ROOT / "site/redirects.json").read_text())
rules = [line.split() for line in (DIST / "_redirects").read_text().splitlines()
         if line.strip() and not line.startswith("#")]
assert all(len(rule) == 3 and rule[2] == "301!" for rule in rules)
assert not any("*" in source for source, _, _ in rules), "Do not mask nonexistent URLs"
sources = {source: target for source, target, _ in rules}
assert len(sources) == len(rules), "Duplicate route rule"
for source, target in redirects.items():
    assert sources[source] == sources[source + "index.html"] == target
    assert not (DIST / source.strip("/") / "index.html").exists()
for source, target, _ in rules:
    assert (DIST / target.strip("/") / "index.html").is_file(), (source, target)
    assert target not in sources, (source, "redirect chain")
for file in DIST.rglob("index.html"):
    relative = file.parent.relative_to(DIST).as_posix()
    route = "/" if relative == "." else "/" + relative + "/"
    assert sources[route + "index.html"] == route
error = (DIST / "404.html").read_text()
assert "<h1>Page not found</h1>" in error
assert 'name="robots" content="noindex,follow"' in error
assert 'rel="canonical"' not in error
assert len(re.findall(r"<h1\b", error)) == 1
assert 'href="/style.css"' in error, "Error-page stylesheet must work at nested missing URLs"
assert "/404.html</loc>" not in (DIST / "sitemap.xml").read_text()
print(f"Netlify payload passed: 56 canonical pages, {len(rules)} permanent redirect rules, branded 404, no SPA fallback.")

contact = (DIST / "contact/index.html").read_text()
form = re.search(r'<form\b[^>]*id="enquiry-form"[^>]*>.*?</form>', contact, re.S)[0]
for attribute in ('name="contact"', 'method="POST"', 'data-netlify="true"',
                  'data-netlify-honeypot="bot-field"'):
    assert attribute in form, attribute
assert form.count('name="form-name" value="contact"') == 1
assert form.count('name="bot-field"') == 1
for field in ("name", "email", "species", "message"):
    assert f'name="{field}"' in form, field
assert "Send enquiry" in form and "Download enquiry" not in contact
assert 'role="status"' in form
assert re.search(r'src="/netlify-contact\.js\?v=[a-f0-9]{12}"', contact)
for name in ("common.js", "app.js"):
    assert "crownwing-enquiry.txt" not in (DIST / name).read_text()
    assert ".onsubmit=" not in (DIST / name).read_text()
for page in DIST.rglob("*.html"):
    text = page.read_text()
    for old_claim in ("shared enquiry download", "download-only", "download your enquiry",
                      "creates a local download", "downloaded enquiry",
                      "Your form entries are processed locally"):
        assert old_claim.lower() not in text.lower(), (page, old_claim)
privacy = (DIST / "privacy-policy/index.html").read_text()
assert "Netlify Forms" in privacy and "processes and stores submissions" in privacy
print("Netlify contact form: static detection, fields, honeypot, submission script and matching privacy copy passed.")