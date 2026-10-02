"""Apply confirmed breeder/retailer copy without changing the site's visual identity.

Run after page generation. Availability describes the confirmed species range,
never individual stock, prices, services or breeding practices not supplied.
"""

import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape

from breeder_content import AFRICAN_GREY_GUIDE, DISPLAY_NAMES, HERO_INTRO, SALE_SLUGS

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
esc = lambda value: html.escape(str(value), quote=True)


def link(path, label, css=""):
    attr = f' class="{css}"' if css else ""
    return f'<a href="{esc(path)}"{attr}>{esc(label)}</a>'


def article(title, content):
    return f'<section class="article-section"><h2>{title}</h2>{content}</section>'


def intro(kicker, title, description, side=""):
    return (
        '<section class="page-intro"><div>'
        f'<p class="eyebrow">{kicker}</p><h1>{title}</h1>'
        f'<p class="page-lead">{description}</p></div>{side}</section>'
    )


def cta(title):
    return (
        '<section class="detail-cta"><div><p class="eyebrow">YOUR NEXT STEP</p>'
        f'<h2>{title}</h2><p>Tell us which parrots interest you and a little about your home.</p>'
        '</div>' + link("/contact/", "Contact us", "button lime") + "</section>"
    )


def related():
    items = [
        ("/available-birds/", "Available birds"),
        ("/parrots/", "Species guides"),
        ("/parrots-for-sale/", "Buying a parrot"),
        ("/our-approach/", "Breeder & buyer information"),
        ("/parrot-care/", "Care guides"),
    ]
    return '<section class="related"><h2>Explore your next step</h2><div>' + "".join(
        link(path, label) for path, label in items
    ) + "</div></section>"


def shell(body):
    return '<main class="content-page"><div class="detail-top">' + link(
        "/", "Home"
    ) + "</div>" + body + "</main>"


def navigation(text):
    nav = '<nav aria-label="Main navigation">' + "".join(
        link(path, label) for path, label in [
            ("/available-birds/", "Available birds"),
            ("/parrots/", "Species guides"),
            ("/parrots-for-sale/", "Buying a parrot"),
            ("/parrot-care/", "Care guides"),
        ]
    ) + link("/contact/", "Contact us", "mobile-contact") + "</nav>"
    text = re.sub(r'<nav aria-label="Main navigation">.*?</nav>', lambda _: nav, text, flags=re.S)
    text = re.sub(
        r'(<a\b[^>]*class="button nav-cta"[^>]*>).*?(</a>)',
        r"\1Contact us\2", text, flags=re.S,
    )
    footer_match = re.search(r"<footer>.*?</footer>", text, re.S)
    if footer_match:
        brand = re.search(r'<a\b[^>]*class="brand"[^>]*>.*?</a>', footer_match[0], re.S)
        if not brand:
            raise ValueError("Footer brand missing")
        footer = (
            "<footer>" + brand[0] + "<p>Parrot breeder &amp; retailer. Thoughtful beginnings.</p><div>"
            + "".join(link(path, label) for path, label in [
                ("/available-birds/", "Available birds"),
                ("/parrots/", "Species guides"),
                ("/parrots-for-sale/", "Buying a parrot"),
                ("/our-approach/", "Our approach"),
                ("/parrot-care/", "Care guides"),
                ("/locations/", "UK city guides"),
                ("/parrot-prices-uk/", "Parrot prices & costs"),
                ("/contact/", "Contact us"),
            ]) + "<span>© 2026 Crownwing Parrots</span></div></footer>"
        )
        text = text[:footer_match.start()] + footer + text[footer_match.end():]
    return text


def metadata(text, path, origin, title=None, description=None):
    if title:
        text = re.sub(r"<title>.*?</title>", lambda _: f"<title>{esc(title)}</title>", text)
    if description:
        text = re.sub(
            r'<meta name="description" content="[^"]*">',
            lambda _: f'<meta name="description" content="{esc(description)}">', text,
        )
    title = html.unescape(re.search(r"<title>(.*?)</title>", text)[1])
    text = re.sub(r'<link rel="canonical"[^>]*>', "", text)
    text = re.sub(r'<script type="application/ld\+json">.*?</script>', "", text, flags=re.S)
    schema = {
        "@context": "https://schema.org", "@type": "WebPage", "name": title,
        "url": origin + path,
        "isPartOf": {"@type": "WebSite", "name": "Crownwing Parrots", "url": origin + "/"},
    }
    if path != "/":
        schema["breadcrumb"] = {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": origin + "/"},
                {"@type": "ListItem", "position": 2, "name": title.split("|")[0].strip(), "item": origin + path},
            ],
        }
    return text.replace(
        "</head>", f'<link rel="canonical" href="{origin + path}">'
        f'<script type="application/ld+json">{json.dumps(schema)}</script></head>',
    )


def apply():
    home = (DIST / "index.html").read_text()
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', home)
    if not canonical:
        raise ValueError("Existing canonical origin required; do not guess a production domain")
    parsed_origin = urlsplit(canonical[1])
    origin = parsed_origin.scheme + "://" + parsed_origin.netloc
    source_data = json.loads((ROOT / "tools/species-data.json").read_text())
    for item in source_data:
        item["name"] = DISPLAY_NAMES[item["slug"]]
        if item["slug"] == "african-parrots":
            item.update(AFRICAN_GREY_GUIDE)
    (ROOT / "tools/species-data.json").write_text(json.dumps(source_data, indent=2) + "\n")

    available_cards = ""
    buying_cards = ""
    for item in source_data:
        slug, name = item["slug"], item["name"]
        available_cards += (
            '<article class="link-card availability-card"><p class="availability-status">Available by enquiry</p>'
            f'<h3>{esc(name)}</h3><p>{esc(item["tag"])}</p><div class="availability-actions">'
            + link("/contact/?species=" + slug, "Ask about current birds", "button")
            + link("/parrots/" + slug + "/", "Read the species guide", "availability-guide")
            + "</div></article>"
        )
        buying_cards += (
            f'<a class="link-card" href="/parrots-for-sale/{SALE_SLUGS[slug]}/">'
            f"<h3>{esc(name)}</h3><span>Explore buying questions &amp; preparation</span></a>"
        )

    available_body = intro(
        "CROWNWING · PARROT BREEDER &amp; RETAILER",
        "Available parrots.<br>Details by enquiry.",
        "All eight parrot groups below are available through Crownwing. Individual birds change regularly, "
        "so contact us for the latest photographs, ages, prices and details.",
    ) + article(
        "Find your species. Ask about the individual.",
        "<p>Whether you are drawn to African Grey Parrots, the colour of Macaws or a smaller companion, "
        "start with the bird’s needs and your home. Our available range is shown below; "
        "it is not a live stock list.</p><p>Species-gallery photographs introduce bird types. "
        "They are not listings of individual birds for sale. Request current photographs and details "
        "of the actual bird you are considering.</p>",
    ) + '<section><h2>Our available parrot range</h2><div class="link-card-grid">' + available_cards + "</div></section>" + article(
        "A good enquiry helps you choose with confidence.",
        "<p>Tell us your preferred species, your experience with birds and the space and daily routine you can offer. "
        "Ask about the individual bird’s age, background, current diet, handling, available records and price. "
        "Confirm what is included and any viewing, collection or aftercare arrangements before committing.</p>",
    ) + cta("Ask about the birds available now.") + related()

    cover = re.search(
        r'<a class="species-card visual-card" href="/parrots/african-parrots/">.*?(<img[^>]+>)',
        home, re.S,
    )
    if not cover:
        raise ValueError("Existing African Grey guide photograph required")
    approach_photo = (
        '<figure class="editorial-photo">' + cover[1]
        + '<figcaption>Species-guide photograph, not an individual stock listing.</figcaption></figure>'
    )
    approach_body = intro(
        "THE CROWNWING APPROACH", "Breeder &amp; retailer.<br>Care at the heart of the choice.",
        "A remarkable bird deserves a well-prepared home. Crownwing brings breeding and retail together "
        "with species information and a considered approach to choosing a parrot.",
        approach_photo,
    ) + article(
        "Know the bird behind the photograph.",
        "<p>Our range includes all eight parrot groups, from African Grey Parrots and Macaws to Conures, Caiques "
        "and smaller companions. The individual birds change, so current details must be confirmed by enquiry.</p>"
        "<p>Ask about the bird’s origin, how it was reared and socialised, its established diet and handling preferences, "
        "and its known health history. Confirm which details are documented and which records are available. "
        "Do not assume every bird has the same background or routine.</p>",
    ) + article(
        "Be clear about what comes with your bird.",
        "<p>Confirm the individual price, any care information or records provided, and whether any supplies are included. "
        "Agree these details before deciding, rather than assuming a standard package or a particular guarantee.</p>",
    ) + article(
        "Agree viewing and collection before making plans.",
        "<p>Ask about viewing opportunities and collection arrangements for the bird you are considering. "
        "Confirm the location, appointment, timing and a suitable transport plan before travelling. "
        "Do not assume delivery or any other transport service is included.</p>",
    ) + article(
        "Prepare for life beyond collection.",
        "<p>Ask what aftercare is offered and how to raise a question after collection. Keep any agreed arrangements "
        "alongside the bird’s care information. For health concerns, seek advice from a qualified avian vet.</p>"
        "<p>Prepare suitable accommodation, a consistent diet, enrichment and safe exercise before the bird comes home. "
        + link("/parrot-care/", "Our care guides") + " help you plan for the everyday commitment.</p>",
    ) + article(
        "A suitable home matters more than a quick decision.",
        "<p>Consider space, noise, daily interaction, other animals and the whole household. "
        "No species is automatically easy, quiet or guaranteed to talk. Choose around the individual bird’s needs "
        "and the care you can sustain—not appearance alone.</p>",
    ) + cta("Start with the right questions.") + related()

    buying_body = intro(
        "BUYING A PARROT FROM CROWNWING", "A remarkable companion.<br>A considered beginning.",
        "Explore the available range, understand the care commitment and contact Crownwing for current bird details. "
        "We are a parrot breeder and retailer; choosing well starts with the individual, not just the species.",
    ) + article(
        "1. Explore the range. Understand the species.",
        "<p>All eight parrot groups are available through Crownwing. Start with "
        + link("/available-birds/", "Available birds") + " to choose a group, then read our "
        + link("/parrots/", "species guides") + " for lifespan, diet, housing and everyday care. "
        "Guide photographs illustrate species; they are not a live stock catalogue.</p>",
    ) + '<div class="link-card-grid">' + buying_cards + "</div>" + article(
        "2. Request current details of the actual bird.",
        "<p>Individual birds change regularly. Contact us for current photographs, age, background, diet, handling "
        "and price. Share your experience, available space and daily routine so your enquiry covers more than availability.</p>",
    ) + article(
        "3. Confirm the details before you commit.",
        "<p>Ask about any records, care information and supplies included with the bird. "
        "Agree payment terms, viewing and collection arrangements directly. Ask what aftercare is offered; "
        "do not assume a service or guarantee that has not been confirmed.</p>",
    ) + article(
        "4. Have the home ready for the first day.",
        "<p>Plan appropriate accommodation, familiar food, safe exercise and enrichment, and identify an avian vet. "
        "Read the " + link("/guides/buying-a-parrot-checklist/", "parrot buying checklist") + " and "
        + link("/guides/preparing-for-a-parrot/", "home preparation guide") + " before making arrangements.</p>",
    ) + cta("Ask about your next companion.") + related()

    form = re.search(r'<form id="enquiry-form">.*?</form>', (DIST / "contact/index.html").read_text(), re.S)[0]
    form = re.sub(r'<p class="form-note">.*?</p>', "", form, flags=re.S)
    contact_body = intro(
        "CONTACT CROWNWING", "Your next companion.<br>Start with a conversation.",
        "Ask about available parrots, current bird details and the practical steps before buying. "
        "Tell us which species interests you and a little about the home you can offer.",
    ) + '<section class="contact-layout"><div><h2>Make your enquiry count.</h2><p>Request current photographs, ages, prices and details of the actual birds available. Include questions about background, diet, records, what is included, collection and aftercare.</p><p>Our range covers all eight parrot groups, but individual birds change regularly. Species-guide photos are not stock listings.</p><p class="enquiry-status-note"><strong>About this form:</strong> it currently prepares a downloadable enquiry file. It does not send a message to Crownwing or store your form details.</p><p>Read ' + link(
        "/our-approach/", "our breeder & buyer information"
    ) + " and the " + link("/guides/buying-a-parrot-checklist/", "buying checklist") + ' before deciding.</p></div><div class="contact-form-panel">' + form + "</div></section>" + related()

    pages = {
        "/available-birds/": ("Available Parrots UK | Crownwing Breeder & Retailer", "All eight parrot groups are available through Crownwing. Contact us for current birds, photographs, ages and prices; individual availability changes regularly.", available_body),
        "/our-approach/": ("Parrot Breeder & Retailer | Our Approach | Crownwing", "Meet Crownwing’s breeder-and-retailer approach. Understand the bird’s background and confirm inclusions, collection and aftercare before buying.", approach_body),
        "/parrots-for-sale/": ("Buying a Parrot UK | Crownwing Parrots", "Buying a parrot in the UK? Explore Crownwing’s available range, compare species and confirm current bird details, prices and arrangements by enquiry.", buying_body),
        "/contact/": ("Contact Crownwing | Available Parrot Enquiries UK", "Enquire about available African Grey Parrots, Macaws and more. Prepare questions about current birds, prices, care and collection with Crownwing.", contact_body),
    }
    for path, (title, description, body) in pages.items():
        target = DIST / path.strip("/") / "index.html"
        text = target.read_text() if target.exists() else home
        text = re.sub(r"<main\b[^>]*>.*?</main>", lambda _: shell(body), text, count=1, flags=re.S)
        text = text.replace('href="style.css"', 'href="/style.css"')
        text = metadata(text, path, origin, title, description)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    home = re.sub(r'<p class="intro">.*?</p>', lambda _: f'<p class="intro">{HERO_INTRO}</p>', home, count=1, flags=re.S)
    home = re.sub(
        r'<div class="hero-actions">.*?</div>',
        '<div class="hero-actions">' + link("/available-birds/", "See available birds", "button lime")
        + link("/parrots/", "Explore species guides", "text-link") + "</div>", home, count=1, flags=re.S,
    )
    home = re.sub(
        r'(<section id="parrots" class="section species"><div class="section-heading"><div>).*?(</div><p>).*?(</p></div>)',
        r'\1<p class="eyebrow">SPECIES GUIDES · NOT INDIVIDUAL BIRD LISTINGS</p><h2>Different feathers.<br>Distinct personalities.</h2>\2'
        'Explore African Grey Parrots, Macaws and more. Learn about the species, then visit '
        + link("/available-birds/", "Available birds") + r' for the range and current-bird enquiries.\3',
        home, count=1, flags=re.S,
    )
    home = re.sub(
        r'<section class="home-feature section">.*?</section>',
        '<section class="home-feature section"><div><p class="eyebrow">BREEDER &amp; RETAILER · CROWNWING PARROTS</p>'
        '<h2>A companion.<br>A commitment.<br>A considered choice.</h2></div><div>'
        '<p>A bird’s needs and your home should shape the decision. Get to know the individual, '
        'confirm what is included and agree the details before your next chapter begins.</p>'
        + link("/our-approach/", "Our breeder & buyer information", "button") + "</div></section>",
        home, count=1, flags=re.S,
    )
    home = re.sub(
        r'<section class="enquiry section">.*?</section>',
        '<section class="enquiry section"><div><p class="eyebrow">AVAILABLE PARROTS · DETAILS BY ENQUIRY</p>'
        '<h2>Your next chapter<br>could have <em>wings.</em></h2><p>All eight parrot groups are available through Crownwing. '
        'The individual birds change regularly—contact us for current photographs, ages, prices and details.</p></div><div>'
        + link("/available-birds/", "Explore available birds", "button lime")
        + "<p>" + link("/contact/", "Contact us", "text-link") + "</p></div></section>",
        home, count=1, flags=re.S,
    )
    home = metadata(home, "/", origin, "Parrot Breeder & Retailer UK | Crownwing Parrots", "Crownwing is a parrot breeder and retailer for UK homes. Explore African Grey Parrots, Macaws and more, and enquire about current birds and prices.")
    (DIST / "index.html").write_text(home)

    public_paths = []
    for target in sorted(DIST.rglob("index.html")):
        rel = target.parent.relative_to(DIST).as_posix()
        path = "/" if rel == "." else "/" + rel + "/"
        text = target.read_text()
        if path == "/parrots/african-parrots/":
            for section_id, key in [("lifespan", "lifetext"), ("temperament", "temperament")]:
                text = re.sub(
                    rf'(<article id="{section_id}"><p class="eyebrow">.*?</p><h2>.*?</h2>)<p>.*?</p>(</article>)',
                    lambda m, key=key: m[1] + "<p>" + esc(AFRICAN_GREY_GUIDE[key]) + "</p>" + m[2],
                    text, count=1, flags=re.S,
                )
            text = re.sub(
                r'(Examples include: ).*?(</p>)',
                lambda m: m[1] + esc(AFRICAN_GREY_GUIDE["examples"]) + "." + m[2],
                text, count=1,
            )
        text = re.sub(r"\bAfrican parrots\b", "African Grey Parrots", text, flags=re.I)
        for slug, name in DISPLAY_NAMES.items():
            old_name = next(item["name"] for item in source_data if item["slug"] == slug)
            # The old headings may come from an earlier generator, not the current catalogue.
            aliases = [old_name, {"macaws": "Macaws", "cockatoos": "Cockatoos", "amazons": "Amazons", "conures": "Conures", "caiques": "Caiques", "eclectus": "Eclectus", "parakeets-small-psittacines": "Parakeets &amp; small psittacines"}.get(slug, name)]
            for old in aliases:
                text = re.sub(r'(<h[13][^>]*>)' + re.escape(old) + r'(</h[13]>)', lambda m: m[1] + esc(name) + m[2], text, flags=re.I)
            text = re.sub(r'(<option[^>]*>)' + re.escape(aliases[-1]) + r'(</option>)', lambda m: m[1] + esc(name) + m[2], text, flags=re.I)
            if path == "/parrots/" + slug + "/":
                text = re.sub(
                    r'(<section class="detail-intro"><div>.*?<p class="detail-tag">.*?</p>)<p>.*?</p>',
                    lambda m: m[1] + "<p>This is a species and care guide, not a listing of individual birds for sale. "
                    + link("/available-birds/", "See the available range") + " or "
                    + link("/contact/?species=" + slug, "ask about current " + name) + ".</p>",
                    text, count=1, flags=re.S,
                )
                text = text.replace("Enquire about " + esc(name), "Ask about available birds")
                text = metadata(text, path, origin, name + ": Lifespan, Diet & Care | Crownwing Parrots", "Explore " + name + " with guidance on lifespan, diet, housing and care. These are species photographs; contact Crownwing for current bird details.")
            if path == "/parrots-for-sale/" + SALE_SLUGS[slug] + "/":
                text = re.sub(r'<section class="location-note availability-note">.*?</section>', "", text, flags=re.S)
                note = '<section class="location-note availability-note"><h2>Available by enquiry</h2><p>' + esc(name) + ' are available through Crownwing. Individual birds change regularly. ' + link("/contact/?species=" + slug, "Contact us for current birds, photographs and prices") + '.</p><p>Species photographs are not individual stock listings.</p></section>'
                text = re.sub(r'(<section class="page-intro">.*?</section>)', lambda m: m[1] + note, text, count=1, flags=re.S)
        text = text.replace("Discover this group", "Read the species guide")
        text = text.replace("Current birds and prices require direct confirmation.", "All eight parrot groups are available through Crownwing; current individual birds and prices require direct confirmation.")
        text = navigation(text)
        if path == "/parrots/":
            text = text.replace("Explore the character and care of eight parrot groups. Start with the species; make the final choice around the individual.", "Explore eight parrot groups and understand their needs. These are species guides, not individual stock listings. Visit Available birds for our range and contact us for current details.")
        text = metadata(text, path, origin)
        target.write_text(text)
        if 'content="noindex,follow"' not in text:
            public_paths.append(path)
    for name in ["common.js", "app.js"]:
        target = DIST / name
        text = target.read_text()
        text = re.sub(r"speciesNames=\[.*?\]", lambda _: "speciesNames=" + json.dumps(list(DISPLAY_NAMES.values())), text)
        target.write_text(text)
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join("<url><loc>" + escape(origin + path) + "</loc></url>" for path in public_paths)
        + "</urlset>"
    )
    print("Applied breeder/retailer positioning, enquiry-based availability and species-guide separation.")


if __name__ == "__main__":
    apply()