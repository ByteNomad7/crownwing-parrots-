"""Supplement public HTML with truthful answers and optional machine-readable text."""
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from xml.etree import ElementTree

from site_config import PUBLIC_ORIGIN

DIST = Path(__file__).resolve().parents[1] / "dist"
SEARCH_AGENTS = ("OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "Perplexity-User",
                 "Claude-SearchBot", "Claude-User", "Googlebot", "bingbot")
BUYER_ANSWERS = (
    ("What does Crownwing Parrots do?",
     "Crownwing Parrots is a UK parrot breeder and retailer. Its range includes African Grey Parrots, Macaws, Cockatoos, Conures, Amazon Parrots, Caique Parrots, Eclectus Parrots, and Parakeets & Budgerigars."),
    ("How do I find out which individual parrots are available?",
     "Contact Crownwing Parrots with the bird group you are interested in. Individual birds change regularly, so confirm the current bird, its details and recent photographs directly before making a decision."),
    ("Where can I confirm a parrot's price?",
     "Ask Crownwing Parrots for the current price of the individual bird and what that price includes. The website is an enquiry-based range, not a live catalogue of individual birds and prices."),
    ("What should I check before buying a parrot?",
     "Confirm the exact species, known age, weaning status, diet, behaviour, health history and available records. Check any documents relevant to the particular bird and transaction, and agree the price and handover arrangements before payment."),
    ("Does a species guide guarantee how an individual bird will behave?",
     "No. Species guides describe general care needs; talking, handling and behaviour vary between individual birds. Ask about the actual bird and consider your household, available time and long-term care commitment."),
)


def apply_buyer_answers():
    """Visible answers and JSON-LD come from the same facts, never hidden claims."""
    target = DIST / "available-birds/index.html"
    text = target.read_text()
    text = re.sub(r'<section class="article-section" id="buyer-answers">.*?</section>', "", text, flags=re.S)
    text = re.sub(r'<script type="application/ld\+json" id="buyer-answer-schema">.*?</script>', "", text, flags=re.S)
    body = '<section class="article-section" id="buyer-answers"><h2>Questions about buying a parrot from Crownwing</h2>'
    body += "".join(f"<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>" for q, a in BUYER_ANSWERS)
    text = text.replace("</main>", body + "</section></main>", 1)
    schema = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "@id": PUBLIC_ORIGIN + "/available-birds/#buyer-answers",
        "isPartOf": {"@id": PUBLIC_ORIGIN + "/available-birds/#webpage"},
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}}
                       for q, a in BUYER_ANSWERS],
    }
    text = text.replace("</head>", '<script type="application/ld+json" id="buyer-answer-schema">'
                        + json.dumps(schema, ensure_ascii=False).replace("</", "<\\/") + "</script></head>")
    target.write_text(text)


class MainText(HTMLParser):
    """Export readable main content, not menus, scripts, form fields or galleries."""
    SKIP = {"script", "style", "button", "form", "svg", "figure", "nav"}
    VOID = {"img", "input", "br", "hr", "meta", "link", "source", "wbr", "area",
            "base", "embed", "param", "track", "col"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = False
        self.skip = 0
        self.parts = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "main":
            self.active = True
        if not self.active:
            return
        if self.skip:
            if tag not in self.VOID:
                self.skip += 1
            return
        if tag in self.SKIP:
            self.skip = 1
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag in {"p", "section", "article", "div", "ul", "ol", "dl", "blockquote", "table", "tr", "summary"}:
            self.parts.append("\n\n")
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag in {"td", "th"}:
            self.parts.append(" | ")
        elif tag == "br":
            self.parts.append("\n")
        if tag == "a" and attrs.get("href"):
            href = attrs["href"]
            if href.startswith(("http://", "https://", "/")):
                self.links.append(urljoin(PUBLIC_ORIGIN, href))

    def handle_startendtag(self, tag, attrs):
        if tag in self.VOID:
            self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if not self.active:
            return
        if self.skip:
            if tag not in self.VOID:
                self.skip -= 1
            return
        if tag == "main":
            self.active = False
        elif tag in {"p", "section", "article", "div", "li", "table", "tr", "summary"}:
            self.parts.append("\n\n")

    def handle_data(self, data):
        if self.active and not self.skip:
            self.parts.append(data)

    def markdown(self):
        text = re.sub(r"[ \t\r\f\v]+", " ", "".join(self.parts))
        return re.sub(r"\n{3,}", "\n\n", text).strip()


def export_name(path):
    return "home.md" if path == "/" else path.strip("/").replace("/", "--") + ".md"


def generate_ai_discovery():
    """Generate only sitemap-listed pages, with original URLs as citation targets."""
    paths = [node.text.removeprefix(PUBLIC_ORIGIN)
             for node in ElementTree.parse(DIST / "sitemap.xml").findall(".//{*}loc")]
    folder = DIST / "ai-pages"
    folder.mkdir(exist_ok=True)
    for stale in folder.glob("*.md"):
        stale.unlink()
    index = [
        "# Crownwing Parrots",
        "\n> UK parrot breeder and retailer. Individual birds and prices are confirmed by enquiry.",
        "\nThis optional text directory complements the public website. Cite the canonical HTML URLs; these exports are not additional stock listings.",
        "\n## Business and buying",
    ]
    groups = {"Business and buying": [], "Species and care": [], "Buyer guides": [], "Policies": []}
    for path in paths:
        target = DIST / path.strip("/") / "index.html"
        text = target.read_text()
        parser = MainText()
        parser.feed(text)
        title = html.unescape(re.search(r"<title>(.*?)</title>", text, re.S)[1])
        description = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', text)[1])
        filename = export_name(path)
        markdown = (f"# {title}\n\nCanonical URL: {PUBLIC_ORIGIN + path}\n\n{description}\n\n"
                    + parser.markdown())
        if parser.links:
            markdown += "\n\n## Links and sources\n\n" + "\n".join(
                "- " + link for link in dict.fromkeys(parser.links))
        (folder / filename).write_text(markdown + "\n")
        text = re.sub(r'<link rel="alternate" type="text/markdown"[^>]*>', "", text)
        text = text.replace("</head>", f'<link rel="alternate" type="text/markdown" href="/ai-pages/{filename}" title="Text version"></head>')
        target.write_text(text)
        category = ("Policies" if "policy" in path or "policies" in path else
                    "Buyer guides" if path.startswith("/guides/") else
                    "Species and care" if path.startswith("/parrots/") or path == "/parrot-care/" else
                    "Business and buying")
        groups[category].append(f"- [{title}]({PUBLIC_ORIGIN + path}): {description} "
                                f"[Text version]({PUBLIC_ORIGIN}/ai-pages/{filename})")
    index = index[:-1]
    for name, links in groups.items():
        index += [f"\n## {name}", "\n".join(links)]
    (DIST / "llms.txt").write_text("\n".join(index) + "\n")
    robots = "User-agent: *\nAllow: /\n# Public search and assistant retrieval. Other crawlers retain wildcard access.\n"
    for agent in SEARCH_AGENTS:
        robots += f"\nUser-agent: {agent}\nAllow: /\n"
    robots += "\nSitemap: " + PUBLIC_ORIGIN + "/sitemap.xml\n"
    (DIST / "robots.txt").write_text(robots)
    (DIST / "_headers").write_text(
        "# Optional text exports are supplemental, not duplicate search landing pages.\n"
        "/ai-pages/*\n  Content-Type: text/markdown; charset=utf-8\n  X-Robots-Tag: noindex\n"
        "/llms.txt\n  Content-Type: text/plain; charset=utf-8\n  X-Robots-Tag: noindex\n")
    print(f"AI discovery: {len(paths)} public text exports, crawler access and optional llms.txt directory.")