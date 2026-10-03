"""Keep static Netlify form detection and the actual submission action in sync."""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def wire_netlify_contact():
    target = DIST / "contact/index.html"
    text = target.read_text()
    match = re.search(r'<form\b[^>]*id="enquiry-form"[^>]*>.*?</form>', text, re.S)
    assert match, "Contact form missing"
    form = match[0]
    form = re.sub(r'<input\b[^>]*name="form-name"[^>]*>', "", form)
    form = re.sub(r'<p data-form-honeypot[^>]*>.*?</p>', "", form, flags=re.S)
    opening = (
        '<form id="enquiry-form" name="contact" method="POST" '
        'data-netlify="true" data-netlify-honeypot="bot-field">'
        '<input type="hidden" name="form-name" value="contact">'
        '<p data-form-honeypot hidden aria-hidden="true"><label>Leave this field empty'
        '<input name="bot-field" tabindex="-1" autocomplete="off"></label></p>'
    )
    form = re.sub(r'<form\b[^>]*>', lambda _: opening, form, count=1)
    form = re.sub(
        r'(<button\b[^>]*type="submit"[^>]*>).*?(</button>)',
        lambda m: m[1] + "Send enquiry" + m[2], form, flags=re.S,
    )
    text = text[:match.start()] + form + text[match.end():]
    # Keep policy and result text readable on the existing dark form panel.
    text = re.sub(r'<style id="contact-form-colours">.*?</style>', "", text, flags=re.S)
    text = text.replace("</head>", '<style id="contact-form-colours">'
                        '.contact-form-panel .privacy-form-note,'
                        '.contact-form-panel .privacy-form-note a,'
                        '.contact-form-panel #form-status{color:#f8f7f0}'
                        '</style></head>')
    text = re.sub(r'<script\b[^>]*src="/netlify-contact\.js[^"]*"[^>]*></script>', "", text)
    script = (ROOT / "tools/netlify-contact.js").read_text()
    (DIST / "netlify-contact.js").write_text(script)
    version = hashlib.sha256(script.encode()).hexdigest()[:12]
    text = text.replace("</body>", f'<script src="/netlify-contact.js?v={version}"></script></body>')
    target.write_text(text)

    # Existing scripts own navigation and species-prefill only, not submission.
    for name in ("common.js", "app.js"):
        script_path = DIST / name
        script = script_path.read_text()
        script = re.sub(
            r"^document\.getElementById\('enquiry-form'\)\.onsubmit=.*\n?",
            "", script, flags=re.M,
        )
        assert "crownwing-enquiry.txt" not in script, "Old download handler remains"
        script_path.write_text(script)
        version = hashlib.sha256(script.encode()).hexdigest()[:12]
        for page in DIST.rglob("*.html"):
            text = page.read_text()
            text = re.sub(
                r'(<script\b[^>]*src=")/' + re.escape(name) + r'(?:\?[^"]*)?(")',
                lambda m: m[1] + "/" + name + "?v=" + version + m[2], text,
            )
            page.write_text(text)