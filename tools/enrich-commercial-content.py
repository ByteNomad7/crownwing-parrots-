"""Repeatable editorial enrichment after photos and confirmed business positioning.

Preserves existing URLs, gallery markup, scripts, forms and branding. Educational
species profiles are not inventory listings or promises about breeder services.
"""

import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape

from breeder_content import DISPLAY_NAMES, SALE_SLUGS
from commercial_intent_content import INTENTS

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MAX_SPECIES_PHOTOS = 4


def esc(value):
    return html.escape(str(value), quote=True)


def link(path, label, css=""):
    attr = f' class="{esc(css)}"' if css else ""
    return f'<a href="{esc(path)}"{attr}>{esc(label)}</a>'


def route_file(path):
    return DIST / path.strip("/") / "index.html"


def element_bounds(text, pattern):
    """Locate a balanced element; regex alone cannot replace nested divs safely."""
    start = re.search(pattern, text)
    if not start:
        raise ValueError(f"Required element missing: {pattern}")
    tag = re.match(r"<([a-z]+)\b", start[0])[1]
    depth = 0
    for token in re.finditer(rf"</?{tag}\b[^>]*>", text[start.start():]):
        depth += -1 if token[0].startswith("</") else 1
        if depth == 0:
            return start.start(), start.start() + token.end()
    raise ValueError(f"Unbalanced {tag}")


def element(text, pattern):
    start, end = element_bounds(text, pattern)
    return text[start:end]


def replace_element(text, pattern, replacement):
    start, end = element_bounds(text, pattern)
    return text[:start] + replacement + text[end:]


def sections(items, tag="section"):
    return "".join(
        f'<{tag} class="article-section" id="{esc(item["id"])}">'
        f'<h2>{esc(item["title"])}</h2>'
        + "".join(f"<p>{esc(p)}</p>" for p in item["paragraphs"])
        + f"</{tag}>"
        for item in items
    )


def support_links(group, guide="/guides/choosing-a-parrot/"):
    return (
        '<section class="related"><h2>Plan the next step</h2><div>'
        + link("/parrots/" + group + "/", DISPLAY_NAMES[group] + " category guide")
        + link("/parrots-for-sale/" + SALE_SLUGS[group] + "/", DISPLAY_NAMES[group] + " buying questions")
        + link(guide, "Practical ownership planning")
        + link("/guides/parrot-housing-enrichment/", "Housing, exercise and enrichment")
        + link("/guides/buying-a-parrot-checklist/", "Questions to resolve before buying")
        + link("/guides/parrot-ownership-costs/", "Budgeting for lifetime care")
        + link("/guides/parrot-diet-nutrition/", "Feeding and nutrition guidance")
        + link("/available-birds/", "Available groups and current-bird enquiries")
        + "</div></section>"
    )


def profile_path(item):
    return "/parrots/" + item["parent"] + "/" + item["slug"] + "/"


def individual_sections(profile):
    """Expose separately the topics authored together in each species record."""
    result = []
    for index, section in enumerate(profile["sections"]):
        paragraphs = section["paragraphs"]
        if index == 2:
            topics = [("adult-size", "Typical adult size"), ("lifespan", "Expected lifespan and long-term care")]
        elif index == 3:
            topics = [("vocalisation", "Talking and vocalisation"), ("training", "Intelligence and reward-based training")]
        elif index == 4:
            topics = [("diet", "Diet and nutrition"), ("housing", "Housing, exercise and enrichment")]
        else:
            result.append(section)
            continue
        if len(paragraphs) < 2:
            raise ValueError(f'{profile["slug"]}: combined topic needs separate paragraphs')
        result += [
            {"id": topics[0][0], "title": topics[0][1], "paragraphs": paragraphs[:1]},
            {"id": topics[1][0], "title": topics[1][1], "paragraphs": paragraphs[1:]},
        ]
    return result


def named_species(items):
    cards = "".join(
        f'<a class="link-card" href="{esc(profile_path(p))}"><h3>{esc(p["name"])}</h3>'
        f'<span>{esc(p["scientific_name"])}</span></a>' for p in items
    )
    return (
        '<section class="article-section named-species" id="named-species">'
        '<h2>Explore individual species</h2>'
        '<p>Compare these educational profiles before asking which individual birds are currently available.</p>'
        '<div class="link-card-grid">' + cards + "</div></section>"
    )


def cta(title, group, description, bird=None):
    destination = "/contact/?species=" + group + ("&bird=" + bird if bird else "")
    return (
        '<section class="detail-cta"><div><p class="eyebrow">CURRENT BIRDS · DETAILS BY ENQUIRY</p>'
        f'<h2>{esc(title)}</h2><p>{esc(description)}</p></div>'
        + link(destination, "Ask about current birds", "button lime")
        + "</section>"
    )


def set_intro(text, intro):
    return re.sub(
        r'(<p class="page-lead">).*?(</p>)',
        lambda m: m[1] + esc(intro) + m[2], text, count=1, flags=re.S,
    )


def retain_links(before, after):
    """Retain useful legacy navigation when replacing an editorial body."""
    present = set(re.findall(r'<a\b[^>]*href="([^"]+)"', after))
    missing = {}
    for href, label in re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', before, re.S):
        if href not in present:
            missing[href] = html.unescape(re.sub(r"<[^>]+>", "", label)).strip()
    if missing:
        block = '<section class="related"><h2>Further reading</h2><div>' + "".join(
            link(html.unescape(href), label) for href, label in missing.items()
        ) + "</div></section>"
        after = after.replace("</main>", block + "</main>", 1)
    return after


def main_after_intro(text, body):
    main = element(text, r'<main\b[^>]*>')
    _, end = element_bounds(main, r'<section class="page-intro"[^>]*>')
    return replace_element(text, r'<main\b[^>]*>', main[:end] + body + "</main>")


def append_before_related(text, block, marker):
    if marker in text:
        text = replace_element(text, rf'<section class="article-section" id="{marker}">', "")
    main = element(text, r'<main\b[^>]*>')
    position = main.find('<section class="related">')
    if position < 0:
        position = main.rfind("</main>")
    return replace_element(text, r'<main\b[^>]*>', main[:position] + block + main[position:])


def metadata(text, path, origin, title=None, description=None, parent=None):
    if title:
        if not title.endswith("Crownwing Parrots"):
            title += " | Crownwing Parrots"
        text = re.sub(r"<title>.*?</title>", lambda _: f"<title>{esc(title)}</title>", text)
    if description:
        text = re.sub(r'<meta name="description" content="[^"]*">',
                      lambda _: f'<meta name="description" content="{esc(description)}">', text)
    title = html.unescape(re.search(r"<title>(.*?)</title>", text)[1])
    description = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', text)[1])
    text = re.sub(r'<meta (?:property|name)="(?:og:[^"]*|twitter:[^"]*)"[^>]*>', "", text)
    og = {
        "og:type": "website", "og:site_name": "Crownwing Parrots", "og:locale": "en_GB",
        "og:title": title, "og:description": description, "og:url": origin + path,
    }
    images = re.findall(r'<img\b[^>]*src="([^"]+)"', text)
    if images:
        og["og:image"] = origin + images[0] if images[0].startswith("/") else images[0]
    additions = "".join(f'<meta property="{key}" content="{esc(value)}">' for key, value in og.items())
    additions += '<meta name="twitter:card" content="summary">'
    text = text.replace("</head>", additions + "</head>")
    text = re.sub(r'<link rel="canonical"[^>]*>', "", text)
    text = text.replace("</head>", f'<link rel="canonical" href="{esc(origin + path)}"></head>')

    def update_schema(match):
        schema = json.loads(match[1])
        if isinstance(schema, dict) and schema.get("@type") == "WebPage":
            schema.update(name=title, description=description, url=origin + path)
            trail = [("/", "Home")]
            if parent:
                trail += [("/parrots/", "Species guides"), ("/parrots/" + parent + "/", DISPLAY_NAMES[parent])]
            if path != "/":
                trail += [(path, title.split("|")[0].strip())]
                schema["breadcrumb"] = {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": i + 1, "name": name, "item": origin + url}
                        for i, (url, name) in enumerate(trail)
                    ],
                }
        return '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace("</", "<\\/") + "</script>"

    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', update_schema, text, flags=re.S)


def apply_content():
    categories = json.loads((ROOT / "tools/category-content.json").read_text())
    cities = json.loads((ROOT / "tools/location-content.json").read_text())
    profiles = json.loads((ROOT / "tools/individual-species-content.json").read_text())
    photos = json.loads((ROOT / "tools/photo-metadata.json").read_text())["photos"]
    home = route_file("/").read_text()
    origin_url = re.search(r'<link rel="canonical" href="([^"]+)"', home)[1]
    parsed = urlsplit(origin_url)
    origin = parsed.scheme + "://" + parsed.netloc
    by_parent = {group: [p for p in profiles if p["parent"] == group] for group in DISPLAY_NAMES}
    rewritten, expanded, created, photo_free = [], [], [], []

    for group, content in categories.items():
        path = "/parrots/" + group + "/"
        text = route_file(path).read_text()
        source_links = element(text, r'<div class="guide-sources"[^>]*>')
        old_content = element(text, r'<div class="detail-content"[^>]*>')
        note_match = re.search(r'<p class="group-note">.*?</p>', old_content, re.S)
        group_note = note_match[0] if note_match else ""
        articles = sections(content["guide_sections"], "article")
        # Keep legacy fragment destinations even if an editorial topic is combined.
        ids = {s["id"] for s in content["guide_sections"]}
        aliases = "".join(f'<span id="{anchor}"></span>' for anchor in
                          ["lifespan", "diet", "temperament", "housing", "noise", "suitability"] if anchor not in ids)
        text = replace_element(
            text, r'<div class="detail-content"[^>]*>',
            '<div class="detail-content">' + group_note + aliases + articles
            + named_species(by_parent[group]) + support_links(group) + source_links + "</div>",
        )
        text = replace_element(
            text, r'<aside\b[^>]*>',
            '<aside><p class="eyebrow">IN THIS GUIDE</p>'
            + "".join(link("#" + s["id"], s["title"]) for s in content["guide_sections"])
            + link("#named-species", "Individual species profiles") + "</aside>",
        )
        guide_intro = element(text, r'<section class="detail-intro"[^>]*>')
        classification = (
            "<p>This is a species and care guide, not a listing of individual birds for sale. "
            + link("/available-birds/", "See the available range") + " or "
            + link("/contact/?species=" + group, "ask about current " + DISPLAY_NAMES[group]) + ".</p>"
        )
        guide_intro = re.sub(
            r'(<p class="detail-tag">.*?</p>).*?(?=<a class="button")',
            lambda m: m[1] + f'<p>{esc(content["guide_intro"])}</p>' + classification,
            guide_intro, count=1, flags=re.S,
        )
        text = replace_element(text, r'<section class="detail-intro"[^>]*>', guide_intro)
        title = DISPLAY_NAMES[group] + ": Size, Personality & Care"
        desc = content.get("guide_description", content["guide_intro"])
        text = metadata(text, path, origin, title, desc)
        route_file(path).write_text(retain_links(route_file(path).read_text(), text))
        rewritten.append(path)

        sale_path = "/parrots-for-sale/" + SALE_SLUGS[group] + "/"
        sale = set_intro(route_file(sale_path).read_text(), content["buying_intro"])
        note = element(sale, r'<section class="location-note availability-note"[^>]*>')
        existing_related = element(sale, r'<section class="related"[^>]*>')
        faq = '<div class="page-faq">' + "".join(
            f'<details><summary>{esc(f["question"])}</summary><p>{esc(f["answer"])}</p></details>'
            for f in content.get("buying_faq", [])
        ) + "</div>"
        sale = main_after_intro(
            sale, note + sections(content["buying_sections"])
            + named_species(by_parent[group]) + support_links(group)
            + faq + cta("Discuss the individual " + DISPLAY_NAMES[group].lower(),
                        group, content["buying_questions"][0])
            + existing_related,
        )
        sale = metadata(sale, sale_path, origin, content["buying_title"], content["buying_description"])
        route_file(sale_path).write_text(retain_links(route_file(sale_path).read_text(), sale))
        rewritten.append(sale_path)

    for slug, city in cities.items():
        path = "/locations/" + slug + "/"
        text = set_intro(route_file(path).read_text(), city["intro"])
        # The upstream notice cleanup removes legacy location notes. Restore
        # this factual boundary independently rather than requiring old markup.
        note = (
            '<div class="location-note"><strong>Regional planning guide</strong>'
            '<p>This page helps owners prepare an enquiry. It is not evidence of local Crownwing premises, '
            'local stock or a confirmed collection or delivery service.</p></div>'
        )
        form = element(text, r'<section class="contact-layout city-enquiry"[^>]*>')
        old_related = element(text, r'<section class="related"[^>]*>')
        species_links = (
            '<section class="article-section"><h2>Compare the species on your shortlist</h2><div class="related"><div>'
            + "".join(link("/parrots/" + group + "/", DISPLAY_NAMES[group] + " care and temperament")
                      + link("/parrots-for-sale/" + SALE_SLUGS[group] + "/", DISPLAY_NAMES[group] + " buying questions")
                      for group in city["groups"])
            + link(city["guide"], "An ownership guide for this planning focus")
            + link("/guides/buying-a-parrot-checklist/", "The UK parrot buying checklist")
            + link("/parrot-prices-uk/", "Understanding price and long-term care costs")
            + "</div></div></section>"
        )
        text = main_after_intro(text, note + sections(city["sections"]) + species_links + form + old_related)
        text = metadata(text, path, origin, city["title"], city["description"])
        route_file(path).write_text(retain_links(route_file(path).read_text(), text))
        rewritten.append(path)

    for slug, content in INTENTS.items():
        path = "/parrots-for-sale/" + slug + "/"
        text = set_intro(route_file(path).read_text(), content["intro"])
        old_related = element(text, r'<section class="related"[^>]*>')
        item_sections = [{"id": ident, "title": title, "paragraphs": paragraphs}
                         for ident, title, paragraphs in content["sections"]]
        body = sections(item_sections)
        for group in content["groups"]:
            body += named_species(by_parent[group]).replace('id="named-species"', 'id="species-' + group + '"')
        body += '<section class="related"><h2>Compare care before enquiring</h2><div>' + "".join(
            link("/parrots/" + group + "/", DISPLAY_NAMES[group] + " needs")
            for group in content["groups"]
        ) + link("/available-birds/", "Which groups are available by enquiry")
        body += link("/guides/parrot-housing-enrichment/", "Plan the accommodation and exercise space") + "</div></section>"
        text = main_after_intro(text, body + old_related)
        text = metadata(text, path, origin, content["title"], content["description"])
        route_file(path).write_text(retain_links(route_file(path).read_text(), text))
        rewritten.append(path)

    # Individual species routes are educational and never imply individual stock.
    for profile in profiles:
        group, path = profile["parent"], profile_path(profile)
        source = route_file("/parrots-for-sale/" + SALE_SLUGS[group] + "/").read_text()
        selected = [p for p in photos if p.get("publish", True) and p["group"] == group
                    and p["identificationConfidence"] == "high" and p["label"] in profile["photo_labels"]][:MAX_SPECIES_PHOTOS]
        if not selected:
            photo_free.append(path)
        photo_html = '<div class="individual-photos">' + "".join(
            f'<figure><img src="{esc(p["src"])}" alt="{esc(p["label"])}" width="{p["width"]}" height="{p["height"]}" loading="lazy">'
            '<figcaption>Species photograph, not a current individual stock listing.</figcaption></figure>'
            for p in selected
        ) + "</div>" if selected else ""
        main = (
            '<main class="content-page"><div class="detail-top">' + link("/", "Home")
            + link("/parrots/", "Species guides") + link("/parrots/" + group + "/", DISPLAY_NAMES[group])
            + '</div><section class="page-intro"><div><p class="eyebrow">INDIVIDUAL SPECIES GUIDE · NOT A STOCK LISTING</p>'
            f'<h1>{esc(profile["name"])}</h1><p class="page-lead">{esc(profile["intro"])}</p></div></section>'
            '<div class="quick-facts"><div><span>Scientific name</span><strong>' + esc(profile["scientific_name"])
            + '</strong></div><div><span>Typical adult size</span><strong>' + esc(profile["size"])
            + '</strong></div><div><span>Lifetime planning</span><strong>' + esc(profile["lifespan"])
            + "</strong></div></div>" + photo_html + sections(individual_sections(profile))
            + ('<section class="article-section"><h2>Species references</h2><ul>'
               + "".join(f'<li>{link(s["url"], s["label"])}</li>' for s in profile.get("sources", []))
               + "</ul></section>" if profile.get("sources") else "")
            + support_links(group) + cta("Ask which " + profile["name"] + " birds are available",
                                       group, profile["enquiry_question"], profile["slug"])
            + '<section class="related"><h2>Compare related species</h2><div>'
            + "".join(link(profile_path(p), p["name"]) for p in by_parent[group] if p != profile)
            + "</div></section></main>"
        )
        text = replace_element(source, r'<main\b[^>]*>', main)
        text = metadata(text, path, origin, profile["title"], profile["description"], group)
        route_file(path).parent.mkdir(parents=True, exist_ok=True)
        route_file(path).write_text(text)
        created.append(path)

    enquiry_data = {
        p["slug"]: {"parent": p["parent"], "message": "I am interested in " + p["name"] + ". " + p["enquiry_question"]}
        for p in profiles
    }
    enquiry_script = (
        "/* Add a known species question without changing the download-only form. */\n"
        "(()=>{const profiles=" + json.dumps(enquiry_data, ensure_ascii=False) + ";"
        "const params=new URLSearchParams(location.search),picked=profiles[params.get('bird')];"
        "const field=document.querySelector('#enquiry-form [name=\"message\"]');"
        "if(field && !field.value && picked && picked.parent===params.get('species'))field.value=picked.message;})();\n"
    )
    (DIST / "species-enquiry.js").write_text(enquiry_script)
    contact = route_file("/contact/").read_text()
    if 'src="/species-enquiry.js"' not in contact:
        contact = contact.replace("</body>", '<script src="/species-enquiry.js"></script></body>')
        route_file("/contact/").write_text(contact)

    hub_blocks = {
        "/available-birds/": ("compare-before-enquiry", "Availability is a starting point, not the whole match",
                             "A group may be available while the exact species, age or handling background you want is not. Use the named-species profiles to make a care-based shortlist, then ask about photographs and details of the individual birds currently offered."),
        "/parrots-for-sale/": ("compare-buying-needs", "Different parrots call for different buying questions",
                              "For African Grey Parrots, discuss security and responses to change. With macaws, establish adult size and usable exercise space. Cockatoo enquiries should explore time alone and independent activity; Amazon enquiries benefit from attention to maturity and body language. Conures, caiques and smaller flock birds need a social and activity plan, while an Eclectus enquiry should include its established feeding routine."),
        "/parrots/": ("species-comparison", "Start with the group. Compare the exact species",
                     "A Blue-and-gold Macaw and a smaller macaw are not interchangeable accommodation choices. Green-cheeked and Sun Conures can differ markedly in vocalisation. Congo African Grey and Timneh profiles describe related but distinct birds, and the small-parrot category spans several social patterns and lifespans. Explore a category, then follow its individual-species links."),
        "/locations/": ("regional-planning", "Use a regional guide for the decisions you still need to make",
                        "The London guide examines usable space and shared living; Manchester focuses on a working-week routine. Leeds considers budgeting, Bristol safe exercise and Sheffield enrichment. Scotland and Northern Ireland pages also ask readers to establish the proposed origin and destination before making travel assumptions. These are planning guides, not evidence of local Crownwing premises."),
        "/parrot-prices-uk/": ("species-cost-drivers", "Species change the care budget as well as the purchase question",
                             "Large macaws need robust equipment and a replacement plan for chew materials. Cockatoo care includes sustained social and independent activity, not simply a cage purchase. Smaller flock birds may require planning for compatible companionship and usable flight space. Eclectus owners should establish the actual feeding routine before buying supplies. Price comparisons need the exact species, bird and inclusions—not a generic parrot price."),
        "/parrot-care/": ("care-by-species", "Apply general care guidance to the exact bird",
                        "The care needs of a bird are not determined by body size alone. Compare an African Grey’s routine and learning opportunities, a caique’s supervised physical activity and a budgerigar’s flock and flight needs. Read the relevant species profile alongside each care guide, then confirm the individual’s existing diet, social history and handling preferences."),
    }
    for path, (ident, title, paragraph) in hub_blocks.items():
        links = "".join(link("/parrots/" + group + "/", DISPLAY_NAMES[group] + " species profiles")
                        for group in DISPLAY_NAMES)
        block = f'<section class="article-section" id="{ident}"><h2>{esc(title)}</h2><p>{esc(paragraph)}</p><div class="related"><div>{links}</div></div></section>'
        text = route_file(path).read_text()
        if path == "/parrot-care/" and 'id="care-library"' not in text:
            text = text.replace('<div class="link-card-grid">',
                                '<h2 id="care-library">The practical ownership library</h2><div class="link-card-grid">', 1)
        if path == "/parrots/" and 'id="browse-groups"' not in text:
            text = re.sub(r'(<div class="species-grid"[^>]*>)',
                          '<h2 id="browse-groups">Explore eight parrot categories</h2>\\1', text, count=1)
        text = append_before_related(text, block, ident)
        route_file(path).write_text(text)
        expanded.append(path)

    guide_groups = {
        "choosing-a-parrot": ("Shortlist by needs, not appearance", ["african-parrots", "conures", "cockatoos"]),
        "buying-a-parrot-checklist": ("Ask questions that fit the species", ["macaws", "amazons", "eclectus"]),
        "parrot-diet-nutrition": ("Read the diet in its species context", ["eclectus", "amazons", "parakeets-small-psittacines"]),
        "parrot-housing-enrichment": ("Compare space, beak strength and activity", ["macaws", "caiques", "parakeets-small-psittacines"]),
        "parrot-ownership-costs": ("Match your budget to the lifetime commitment", ["cockatoos", "macaws", "african-parrots"]),
        "preparing-for-a-parrot": ("Plan the first days around a familiar routine", ["african-parrots", "eclectus", "conures"]),
    }
    for slug, (title, groups) in guide_groups.items():
        path = "/guides/" + slug + "/"
        ident = "species-context"
        block = f'<section class="article-section" id="{ident}"><h2>{esc(title)}</h2><div class="related"><div>'
        for group in groups:
            block += link("/parrots/" + group + "/", DISPLAY_NAMES[group] + " care requirements")
            block += link("/parrots-for-sale/" + SALE_SLUGS[group] + "/", "Buying questions for " + DISPLAY_NAMES[group])
        block += "</div></div></section>"
        route_file(path).write_text(append_before_related(route_file(path).read_text(), block, ident))
        expanded.append(path)

    # All pages receive matching social metadata without touching their robots policy.
    public_paths = []
    for target in sorted(DIST.rglob("index.html")):
        relative = target.parent.relative_to(DIST).as_posix()
        path = "/" if relative == "." else "/" + relative + "/"
        parent = next((p["parent"] for p in profiles if profile_path(p) == path), None)
        text = metadata(target.read_text(), path, origin, parent=parent)
        target.write_text(text)
        if 'content="noindex,follow"' not in text:
            public_paths.append(path)
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join("<url><loc>" + escape(origin + path) + "</loc></url>" for path in public_paths) + "</urlset>"
    )
    report = {"rewritten": rewritten, "expanded": expanded, "new_species_profiles": created,
              "species_profiles_awaiting_exact_photos": photo_free, "city_review_drafts_retained": 13,
              "metadata_reviewed": len(list(DIST.rglob("index.html")))}
    (ROOT / "tools/content-audit-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Editorial enrichment: {len(rewritten)} rewritten, {len(expanded)} expanded, {len(created)} named-species profiles.")


if __name__ == "__main__":
    apply_content()