"""Audit customer-visible launch copy in built HTML and optionally the preview."""
import argparse
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "form development notice": r"about this form|currently prepares|does not send(?: or save)?|no email.delivery connection",
    "demo/development wording": r"\bdemo\b|\bprototype\b|\blorem ipsum\b|\bplaceholder\b|\bunder construction\b|\bcoming soon\b|\bsample data\b|\btest data\b|\breview draft\b",
    "repeated stock/photo disclaimer": r"not (?:an? )?(?:live |current |individual |current individual )?stock (?:listing|list|catalogue)|not a listing of individual birds|not individual bird listings|species.guide photograph",
}


class VisibleCopy(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ignored = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("head", "script", "style"):
            self.ignored += 1
        if tag == "meta":
            attributes = dict(attrs)
            if attributes.get("name") == "description":
                self.parts.append(attributes.get("content", ""))

    def handle_endtag(self, tag):
        if tag in ("head", "script", "style"):
            self.ignored -= 1

    def handle_data(self, data):
        if not self.ignored:
            self.parts.append(data)


def findings(markup):
    parser = VisibleCopy()
    parser.feed(markup)
    text = " ".join(" ".join(parser.parts).split())
    return [
        {"category": category, "matched_text": match.group()}
        for category, pattern in PATTERNS.items()
        for match in re.finditer(pattern, text, re.I)
    ]


def main():
    arguments = argparse.ArgumentParser()
    arguments.add_argument("--preview", help="Running development preview origin")
    arguments.add_argument("--report", default="reports/launch-copy-audit.json")
    options = arguments.parse_args()
    files = sorted((ROOT / "dist").rglob("*.html"))
    routes = [
        "/" + file.relative_to(ROOT / "dist").as_posix().removesuffix("index.html")
        for file in files
    ]
    static_findings = [
        {"page": route, **item}
        for file, route in zip(files, routes)
        for item in findings(file.read_text())
    ]
    live_findings = []
    checked = 0
    if options.preview:
        def check_route(route):
            with urlopen(options.preview.rstrip("/") + route, timeout=30) as response:
                return route, findings(response.read().decode("utf-8"))
        with ThreadPoolExecutor(max_workers=4) as pool:
            for route, matches in pool.map(check_route, routes):
                checked += 1
                live_findings.extend({"page": route, **item} for item in matches)
    report = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "generated_html_pages": len(files),
        "running_preview_pages_checked": checked,
        "generated_page_findings": static_findings,
        "running_preview_findings": live_findings,
        "published_netlify_site": "Not verified: its URL has not been provided. Redeploy the updated files.",
        "retained_customer_information": [
            "Availability by enquiry", "Bird names and care guidance",
            "Privacy and business policies", "Accurately labelled Download enquiry action",
        ],
        "contact_functionality": "The form downloads an enquiry file for the customer to email; direct email links remain available.",
        "result": "PASS" if not static_findings and not live_findings else "FAIL",
    }
    target = ROOT / options.report
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    assert report["result"] == "PASS", "Customer-visible demo/development copy remains"


if __name__ == "__main__":
    main()