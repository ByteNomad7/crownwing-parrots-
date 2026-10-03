"""Apply confirmed breeder/retailer copy without changing the site's visual identity.

Run after page generation. Availability describes the confirmed species range,
never individual stock, prices, services or breeding practices not supplied.
"""

import html
import hashlib
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

from breeder_content import AFRICAN_GREY_GUIDE, DISPLAY_NAMES, HERO_INTRO, SALE_SLUGS
from site_config import PUBLIC_ORIGIN

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
            ("/guides/", "Parrot guides"),
        ]
    ) + link("/contact/", "Contact us", "mobile-contact") + "</nav>"
    text = re.sub(r'<nav aria-label="Main navigation">.*?</nav>', lambda _: nav, text, flags=re.S)
    text = re.sub(
        r'(<a\b[^>]*class="button nav-cta"[^>]*>).*?(</a>)',
        r"\1Contact us\2", text, flags=re.S,
    )
    footer_match = re.search(r"<footer\b[^>]*>.*?</footer>", text, re.S)
    if footer_match:
        brand = re.search(r'<a\b[^>]*class="brand"[^>]*>.*?</a>', footer_match[0], re.S)
        if not brand:
            raise ValueError("Footer brand missing")
        footer = (
            '<footer class="site-footer" id="site-footer"><div class="footer-identity">'
            + brand[0] + "<p>Parrot breeder &amp; retailer. Thoughtful beginnings.</p></div>"
            + '<nav class="footer-nav" aria-label="Footer navigation">'
            + '<section class="footer-link-group"><h2>Explore</h2>'
            + "".join(link(path, label) for path, label in [
                ("/available-birds/", "Available birds"),
                ("/parrots/", "Species guides"),
                ("/parrots-for-sale/", "Buying a parrot"),
                ("/our-approach/", "Our approach"),
            ]) + '</section><section class="footer-link-group"><h2>Ownership &amp; enquiries</h2>'
            + "".join(link(path, label) for path, label in [
                ("/parrot-care/", "Care guides"),
                ("/locations/", "UK city guides"),
                ("/parrot-prices-uk/", "Parrot prices & costs"),
                ("/contact/", "Contact us"),
            ]) + '</section></nav><div class="footer-bottom"><span>© 2026 Crownwing Parrots</span>'
            + '<nav class="footer-policies" aria-label="Policies">'
            + "".join(link(path, label) for path, label in [
                ("/privacy-policy/", "Privacy policy"),
                ("/cookie-policy/", "Cookie policy"),
                ("/business-policies/", "Payments, delivery & refunds"),
            ]) + "</nav></div></footer>"
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
    origin = PUBLIC_ORIGIN
    source_data = json.loads((ROOT / "tools/species-data.json").read_text())
    for item in source_data:
        item["name"] = DISPLAY_NAMES[item["slug"]]
        if item["slug"] == "african-parrots":
            item.update(AFRICAN_GREY_GUIDE)
    (ROOT / "tools/species-data.json").write_text(json.dumps(source_data, indent=2) + "\n")

    available_cards = ""
    buying_cards = ""
    photo_metadata = json.loads((ROOT / "tools/photo-metadata.json").read_text())
    photos_by_id = {photo["id"]: photo for photo in photo_metadata["photos"]}
    for item in source_data:
        slug, name = item["slug"], item["name"]
        photo = photos_by_id[photo_metadata["primaryByGroup"][slug]]
        if photo["group"] != slug or not photo["publish"] or photo["identificationConfidence"] != "high":
            raise ValueError(f"Approved representative photograph required for {slug}")
        if not (DIST / photo["thumbnail"].lstrip("/")).is_file():
            raise ValueError(f"Missing thumbnail for {slug}")
        available_cards += (
            '<article class="link-card availability-card"><p class="availability-status">Available by enquiry</p>'
            '<h3 class="availability-title">'
            f'<img class="availability-thumbnail" src="{esc(photo["thumbnail"])}" alt="" aria-hidden="true" '
            f'width="44" height="44" loading="lazy" decoding="async" style="object-position:{esc(photo["focus"])}">'
            f'<span>{esc(name)}</span></h3><p>{esc(item["tag"])}</p><div class="availability-actions">'
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
        "start with the bird’s needs and your home. Explore our available range below.</p>"
        "<p>Contact us for current photographs and details of the bird you are considering.</p>",
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
        + '</figure>'
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
        "BUYING A PARROT FROM CROWNWING", "Parrots for sale in the UK.<br>A considered beginning.",
        "Looking for parrots for sale in the UK? Crownwing is a parrot breeder and retailer with eight "
        "parrot groups available by enquiry. Compare African Grey Parrots, Macaws and smaller companions, "
        "then contact us for current photographs, ages, prices and details of the individual birds.",
    ) + article(
        "1. Explore the range. Understand the species.",
        "<p>All eight parrot groups are available through Crownwing. Start with "
        + link("/available-birds/", "Available birds") + " to choose a group, then read our "
        + link("/parrots/", "species guides") + " for lifespan, diet, housing and everyday care.</p>",
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
    ) + '<section class="article-section" id="parrot-buyer-questions"><h2>Questions when buying a parrot in the UK</h2><div class="page-faq">' + (
        '<details><summary>How do I get a current parrot price?</summary><p>'
        'Choose a group above and ask for a quote for the particular bird being discussed. Request its '
        'exact species, current photographs, known age and an itemised account of what the price includes. '
        'An advert on another website is not a Crownwing quote. Allow separately for food, housing, '
        'enrichment and avian veterinary care; our '
        + link("/guides/parrot-ownership-costs/", "parrot ownership costs guide")
        + ' helps you plan beyond the purchase price.</p></details>'
        '<details><summary>Can I enquire about baby or hand-reared parrots?</summary><p>'
        'Include your preferences in the enquiry, then confirm what individual birds are available. '
        'Ask about known age, rearing and socialisation history, established food, independent feeding '
        'and current handling preferences. Baby, hand-reared and tame are not interchangeable descriptions '
        'or guarantees of future behaviour. See the '
        + link("/guides/buying-a-parrot-checklist/", "parrot buying checklist")
        + ' for questions to resolve before committing.</p></details>'
        '<details><summary>What should I check when searching for parrots for sale near me?</summary><p>'
        'Crownwing’s published contact address is in Bristol. Contact us to confirm the bird, viewing '
        'and handover arrangements before travelling or making a commitment. Our city guides help buyers '
        'plan from their area; they do not identify Crownwing branches or local stock. '
        + link("/contact/", "Check our contact details and ask about arrangements")
        + ' for your enquiry.</p></details>'
    ) + '</div></section>' + cta("Ask about your next companion.") + related()

    form = re.search(r'<form id="enquiry-form"[^>]*>.*?</form>', (DIST / "contact/index.html").read_text(), re.S)[0]
    form = re.sub(r'<p class="form-note">.*?</p>', "", form, flags=re.S)
    contact_body = intro(
        "CONTACT CROWNWING", "Your next companion.<br>Start with a conversation.",
        "Ask about available parrots, current bird details and the practical steps before buying. "
        "Tell us which species interests you and a little about the home you can offer.",
    ) + '<section class="contact-layout"><div><h2>Contact details</h2><address>White’s Paddock<br>Bristol BS9 1RQ<br>United Kingdom</address><p><strong>Email</strong><br>' + link("mailto:crownwingparrots@gmail.com", "crownwingparrots@gmail.com") + '<br>' + link("mailto:info@crownwingparrots.co.uk", "info@crownwingparrots.co.uk") + '</p><h2>Make your enquiry count.</h2><p>Request current photographs, ages, prices and details of the birds available. Include questions about background, diet, records, what is included, collection and aftercare.</p><p>Our range covers all eight parrot groups. Contact us for current availability.</p><p>Read ' + link(
        "/our-approach/", "our breeder & buyer information"
    ) + " and the " + link("/guides/buying-a-parrot-checklist/", "buying checklist") + ' before deciding.</p></div><div class="contact-form-panel">' + form + "</div></section>" + related()

    pages = {
        "/available-birds/": ("Available Parrots UK: Photos, Ages & Prices | Crownwing Parrots", "Check Crownwing’s available parrot groups and enquire about current photographs, ages and prices. Individual birds change regularly; contact us for details.", available_body),
        "/our-approach/": ("Parrot Breeder & Retailer | Our Approach | Crownwing", "Meet Crownwing’s breeder-and-retailer approach. Understand the bird’s background and confirm inclusions, collection and aftercare before buying.", approach_body),
        "/parrots-for-sale/": ("Parrots for Sale UK | Crownwing Parrots", "Parrots for sale in the UK from Crownwing, a breeder and retailer. Compare eight parrot groups and enquire about current birds, photos, ages and prices.", buying_body),
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
        r'(<section class="hero"><div class="hero-copy"><p class="eyebrow">).*?(</p>)',
        r"\1UK PARROTS FOR SALE · BREEDER &amp; RETAILER\2",
        home, count=1, flags=re.S,
    )
    home = re.sub(
        r'<div class="hero-actions">.*?</div>',
        '<div class="hero-actions">' + link("/available-birds/", "See available birds", "button lime")
        + link("/parrots/", "Explore species guides", "text-link") + "</div>", home, count=1, flags=re.S,
    )
    home = re.sub(
        r'(<section id="parrots" class="section species"><div class="section-heading"><div>).*?(</div><p>).*?(</p></div>)',
        r'\1<p class="eyebrow">EXPLORE OUR PARROTS</p><h2>Different feathers.<br>Distinct personalities.</h2>\2'
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
                    lambda m: m[1] + "<p>Explore species information and everyday care. "
                    + link("/available-birds/", "See the available range") + " or "
                    + link("/contact/?species=" + slug, "ask about current " + name) + ".</p>",
                    text, count=1, flags=re.S,
                )
                text = text.replace("Enquire about " + esc(name), "Ask about available birds")
                text = metadata(text, path, origin, name + ": Lifespan, Diet & Care | Crownwing Parrots", "Explore " + name + " with guidance on lifespan, diet, housing and care. Contact Crownwing for available birds and current details.")
            if path == "/parrots-for-sale/" + SALE_SLUGS[slug] + "/":
                text = re.sub(r'<section class="location-note availability-note">.*?</section>', "", text, flags=re.S)
                note = '<section class="location-note availability-note"><h2>Available by enquiry</h2><p>' + esc(name) + ' are available through Crownwing. Individual birds change regularly. ' + link("/contact/?species=" + slug, "Contact us for current birds, photographs and prices") + '.</p></section>'
                text = re.sub(r'(<section class="page-intro">.*?</section>)', lambda m: m[1] + note, text, count=1, flags=re.S)
        text = text.replace("Discover this group", "Read the species guide")
        text = text.replace("Current birds and prices require direct confirmation.", "All eight parrot groups are available through Crownwing; current individual birds and prices require direct confirmation.")
        text = navigation(text)
        if path == "/parrots/":
            text = text.replace("Explore the character and care of eight parrot groups. Start with the species; make the final choice around the individual.", "Explore eight parrot groups and understand their needs. Visit Available birds for our range and contact us for current details.")
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
    # Static JS is cacheable in production; a content version prevents existing
    # visitors from keeping an old photo viewer after a fix is published.
    detail_version = hashlib.sha256((DIST / "detail.js").read_bytes()).hexdigest()[:12]
    for target in DIST.rglob("index.html"):
        text = target.read_text()
        updated = re.sub(r'(<script\b[^>]*src=")/detail\.js(?:\?[^"]*)?(")',
                         lambda m: m[1] + "/detail.js?v=" + detail_version + m[2], text)
        if updated != text:
            target.write_text(updated)
    print("Applied breeder/retailer positioning, enquiry-based availability and species-guide separation.")
    # Editorial content is the final authority after stock disclosures and photographs.
    import runpy
    runpy.run_path(str(ROOT / "tools/enrich-commercial-content.py"), run_name="__main__")
    # Homepage photography runs after editorial changes so its distributed,
    # group-linked stories persist in the generated homepage.
    runpy.run_path(str(ROOT / "tools/homepage-photography.py"), run_name="__main__")
    from netlify_forms import wire_netlify_contact
    wire_netlify_contact()
    from static_hosting import generate_static_hosting
    generate_static_hosting()


if __name__ == "__main__":
    apply()