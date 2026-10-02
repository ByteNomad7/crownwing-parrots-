"""Add a small, linked buyer library without replacing established URLs."""
import html
import json
import re
import shutil
from pathlib import Path

from buyer_resource_content import (
    BUYING_SECTIONS, CHOOSING_SECTIONS, COST_SECTIONS,
    HUB_SECTIONS, LEGAL_SECTIONS,
)
from buyer_tools_markup import render_budget, render_comparison
from content_registry import sync_content_registry, write_sitemap

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

NEW_PAGES = {
    "/guides/": (
        "UK Parrot Guides | Buying, Care & Documentation",
        "Parrot guides for a considered beginning",
        "A practical UK parrot resource library: choose a bird, check documentation, plan costs and prepare a safe home before making a buying enquiry.",
        "Start with the decision you need to make. These resources bring buying preparation, everyday care and UK documentation checks together without treating a photograph as a current bird listing.",
        HUB_SECTIONS,
    ),
    "/guides/buying-a-parrot/": (
        "How to Buy a Parrot in the UK | Complete Buyer's Guide",
        "How to buy a parrot in the UK",
        "Follow a UK parrot buying journey: household suitability, fully weaned birds, seller questions, documentation, budgets, transport and the first week at home.",
        "Buying a parrot begins well before a price enquiry. Work through the household, individual-bird and practical checks below, then decide whether you are ready to offer a suitable long-term home.",
        BUYING_SECTIONS,
    ),
    "/guides/cites-parrots-uk/": (
        "Parrot Documentation UK | CITES & Bird Registration",
        "Parrot documentation, CITES and UK registration",
        "Check what UK parrot buyers should ask about CITES, identification, lawful origin, bird registration and GB/NI movements, with dated official sources.",
        "There is no single paperwork rule for every parrot. The scientific name, lawful origin, proposed transaction, housing arrangements and journey all matter. Use this guide to prepare questions, not to certify an individual bird.",
        LEGAL_SECTIONS,
    ),
}


def route_file(path):
    return DIST / path.strip("/") / "index.html"


def sections(records):
    return "".join(
        '<section class="article-section" id="foundation-' + html.escape(ident, quote=True)
        + '"><h2>' + html.escape(heading) + "</h2>" + body + "</section>"
        for ident, heading, body in records
    )


def insert_once(text, content, marker):
    if f'id="{marker}"' in text:
        return text
    position = re.search(r'<section\b[^>]*\bclass="related"[^>]*>', text)
    if position:
        return text[:position.start()] + content + text[position.start():]
    return text.replace("</main>", content + "</main>", 1)


def refresh_extension(text, content, marker):
    """Replace our complete nested div, rather than retaining stale tool markup."""
    start = re.search(r'<div\b[^>]*\bid="' + re.escape(marker) + r'"[^>]*>', text)
    if not start:
        return insert_once(text, content, marker)
    depth = 1
    for tag in re.finditer(r"</?div\b[^>]*>", text[start.end():], re.I):
        depth += -1 if tag[0].lower().startswith("</") else 1
        if depth == 0:
            end = start.end() + tag.end()
            return text[:start.start()] + content + text[end:]
    raise ValueError(f"Unbalanced managed resource block: {marker}")


def apply_buyer_resources(metadata):
    template = route_file("/our-approach/").read_text()
    for path, (title, h1, description, intro, records) in NEW_PAGES.items():
        main = (
            '<main class="content-page"><div class="detail-top"><a href="/">Home</a>'
            + ('' if path == "/guides/" else ' / <a href="/guides/">Parrot guides</a>')
            + '</div><section class="page-intro"><div><p class="eyebrow">'
            + ("BUYER RESOURCE LIBRARY" if path == "/guides/" else "UK BUYER EDUCATION")
            + "</p><h1>" + html.escape(h1) + '</h1><p class="page-lead">'
            + html.escape(intro) + "</p></div></section>" + sections(records)
            + '<section class="related"><h2>Your next step</h2><div>'
            + '<a href="/guides/">Browse the guide library</a>'
            + '<a href="/available-birds/">Ask about current availability</a>'
            + '<a href="/contact/">Prepare a Crownwing enquiry</a>'
            + "</div></section></main>"
        )
        text, count = re.subn(r"<main\b[^>]*>.*?</main>", lambda _: main, template, count=1, flags=re.S)
        if count != 1:
            raise ValueError("Buyer resource template must have exactly one main")
        text = metadata(text, path, origin(), title, description)
        target = route_file(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    extensions = [
        ("/guides/parrot-ownership-costs/", COST_SECTIONS, render_budget(),
         "foundation-budget-planning",
         "Cost of Keeping a Parrot UK | Budget Planner",
         "Plan the cost of keeping a parrot in the UK with a quote-based budget calculator covering setup, food, toys, veterinary saving, insurance and an emergency reserve."),
        ("/guides/choosing-a-parrot/", CHOOSING_SECTIONS, render_comparison(),
         "foundation-household-fit",
         "Which Parrot Is Right for Me? | UK Comparison Guide",
         "Compare eight parrot groups by size, noise, talking, social needs, lifespan and household demands. Build a thoughtful shortlist, not a best-bird ranking."),
    ]
    for path, records, tool, marker, title, description in extensions:
        target = route_file(path)
        block = '<div id="' + marker + '">' + sections(records) + tool + "</div>"
        text = refresh_extension(target.read_text(), block, marker)
        text = text.replace('<link rel="stylesheet" href="/buyer-resources.css">', "")
        text = text.replace('<script defer src="/buyer-tools.js"></script>', "")
        text = text.replace("</head>", '<link rel="stylesheet" href="/buyer-resources.css">'
                            '<script defer src="/buyer-tools.js"></script></head>')
        target.write_text(metadata(text, path, origin(), title, description))
    for name in ("buyer-resources.css", "buyer-tools.js"):
        shutil.copyfile(ROOT / "site" / name, DIST / name)

    # Contextual paths connect education with existing commercial/species pages.
    for target in sorted(DIST.rglob("index.html")):
        rel = target.parent.relative_to(DIST).as_posix()
        path = "/" if rel == "." else "/" + rel + "/"
        if path == "/guides/":
            continue
        if (path.startswith(("/parrots/", "/parrots-for-sale/", "/guides/"))
                or path in ("/", "/parrots-for-sale/", "/parrot-care/", "/available-birds/")):
            block = (
                '<section class="related" id="buyer-resource-pathways"><h2>Prepare before you enquire</h2><div>'
                '<a href="/guides/buying-a-parrot/">Work through the UK buying journey</a>'
                '<a href="/guides/cites-parrots-uk/">Check documentation and registration</a>'
                '<a href="/guides/parrot-ownership-costs/">Build your ownership budget</a>'
                '<a href="/guides/preparing-for-a-parrot/">Prepare for the first days at home</a>'
                '</div></section>'
            )
            target.write_text(insert_once(target.read_text(), block, "buyer-resource-pathways"))


def origin():
    from site_config import PUBLIC_ORIGIN
    return PUBLIC_ORIGIN


def finish_buyer_resources(public_paths):
    """Run after metadata/image updates so content dates survive pure rebuilds."""
    records = sync_content_registry(DIST)
    for target in sorted((DIST / "guides").glob("*/index.html")):
        path = "/" + target.parent.relative_to(DIST).as_posix() + "/"
        text = target.read_text()
        text = re.sub(r'<script type="application/ld\+json" id="buyer-article-schema">.*?</script>',
                      "", text, flags=re.S)
        headline = html.unescape(re.sub(r"<[^>]+>", "", re.search(r"<h1\b[^>]*>(.*?)</h1>", text, re.S)[1]))
        description = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', text)[1])
        article = {
            "@context": "https://schema.org",
            "@type": "Article", "@id": origin() + path + "#article",
            "headline": headline, "description": description, "url": origin() + path,
            "mainEntityOfPage": {"@id": origin() + path + "#webpage"},
            "publisher": {"@id": origin() + "/#organization"},
            "inLanguage": "en-GB",
        }
        dates = records[path]
        if dates.get("published"):
            article["datePublished"] = dates["published"]
        if dates.get("last_modified"):
            article["dateModified"] = dates["last_modified"]
        # No invented author, professional reviewer, qualifications or dates.
        data = json.dumps(article, ensure_ascii=False).replace("</", "<\\/")
        text = text.replace('</head>', '<script type="application/ld+json" id="buyer-article-schema">'
                            + data + "</script></head>")
        text = text.replace('property="og:type" content="website"',
                            'property="og:type" content="article"')
        target.write_text(text)
    write_sitemap(DIST, origin(), public_paths)