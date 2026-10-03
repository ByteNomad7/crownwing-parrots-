"""Place approved bird photographs throughout the Crownwing homepage.

The images introduce bird groups; they are not current individual stock listings.
This pass runs after editorial enrichment so its content and placements persist on
every regular site build.
"""

import hashlib
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PHOTO_DATA = ROOT / "tools" / "photo-metadata.json"
SOURCE_CSS = ROOT / "site" / "homepage-photography.css"
DEST_CSS = DIST / "homepage-photography.css"

GROUPS = [
    ("african-parrots", "African Grey Parrots"),
    ("macaws", "Macaw Parrots"),
    ("cockatoos", "Cockatoo Parrots"),
    ("amazons", "Amazon Parrots"),
    ("conures", "Conure Parrots"),
    ("caiques", "Caique Parrots"),
    ("eclectus", "Eclectus Parrots"),
    ("parakeets-small-psittacines", "Parakeets & Budgerigars"),
]


def esc(value):
    return html.escape(str(value), quote=True)


def approved_photos():
    data = json.loads(PHOTO_DATA.read_text())
    photos_by_id = {photo["id"]: photo for photo in data["photos"]}
    result = {}
    for slug, _ in GROUPS:
        photo_id = data["primaryByGroup"].get(slug)
        photo = photos_by_id.get(photo_id)
        if (
            not photo
            or photo.get("group") != slug
            or not photo.get("publish")
            or photo.get("identificationConfidence") != "high"
        ):
            raise ValueError(f"Approved, high-confidence group photo required: {slug}")
        for key in ("src", "thumbnail", "focus", "width", "height", "thumbnailWidth"):
            if key not in photo:
                raise ValueError(f"Photo metadata missing {key}: {slug}")
        for path in (photo["src"], photo["thumbnail"]):
            if not (DIST / path.lstrip("/")).is_file():
                raise FileNotFoundError(f"Approved homepage photo is missing: {path}")
        result[slug] = photo
    return result


def image_link(slug, name, photo, extra_class=""):
    css_class = "hp-photo-link" + (f" {extra_class}" if extra_class else "")
    return (
        f'<a class="{css_class}" href="/parrots/{esc(slug)}/" '
        f'aria-label="Explore the {esc(name)} species guide">'
        f'<img src="{esc(photo["src"])}" '
        f'srcset="{esc(photo["thumbnail"])} {int(photo["thumbnailWidth"])}w, '
        f'{esc(photo["src"])} {int(photo["width"])}w" '
        f'sizes="(max-width: 700px) 92vw, (max-width: 1100px) 45vw, 42vw" '
        f'alt="{esc(photo["label"])}" width="{int(photo["width"])}" '
        f'height="{int(photo["height"])}" loading="lazy" decoding="async" '
        f'style="object-position:{esc(photo["focus"])}">'
        '<span class="hp-photo-arrow" aria-hidden="true">↗</span></a>'
    )


def caption(name):
    return (
        f'<p class="hp-caption"><span>{esc(name)}</span>'
        '<span>Species-guide photograph · not an individual stock listing</span></p>'
    )


def story_single(photo_map, slug, name, index, heading, copy, link_label):
    photo = photo_map[slug]
    return (
        f'<section class="hp-story hp-story-single hp-story-{index}" '
        f'aria-labelledby="hp-heading-{index}">'
        '<div class="hp-story-image">'
        + image_link(slug, name, photo)
        + caption(name)
        + '</div><div class="hp-story-copy">'
        f'<p class="hp-kicker">A CLOSER LOOK · {esc(name.upper())}</p>'
        f'<h2 id="hp-heading-{index}">{heading}</h2>'
        f'<p>{copy}</p>'
        f'<a class="hp-text-link" href="/parrots/{esc(slug)}/">{esc(link_label)} <span aria-hidden="true">↗</span></a>'
        '</div></section>'
    )


def story_pair(photo_map, index, heading, copy, groups):
    figures = []
    for slug, name in groups:
        figures.append(
            '<figure class="hp-pair-figure">'
            + image_link(slug, name, photo_map[slug])
            + caption(name)
            + '</figure>'
        )
    return (
        f'<section class="hp-story hp-story-pair hp-story-{index}" '
        f'aria-labelledby="hp-heading-{index}">'
        '<div class="hp-story-copy">'
        '<p class="hp-kicker">A RANGE OF CHARACTERS</p>'
        f'<h2 id="hp-heading-{index}">{heading}</h2><p>{copy}</p>'
        '<p class="hp-stock-note">These images illustrate bird groups. For current individual birds, '
        'photographs and details, please enquire.</p>'
        '</div><div class="hp-pair-photos">'
        + "".join(figures)
        + '</div></section>'
    )


def block(key, content):
    return f'<!-- crownwing-home-photo:{key}:start -->{content}<!-- crownwing-home-photo:{key}:end -->'


def place(text, key, content, anchor_pattern, count=1):
    marker_pattern = re.compile(
        rf'<!-- crownwing-home-photo:{re.escape(key)}:start -->.*?'
        rf'<!-- crownwing-home-photo:{re.escape(key)}:end -->',
        flags=re.S,
    )
    replacement = block(key, content)
    if marker_pattern.search(text):
        return marker_pattern.sub(lambda _: replacement, text, count=1)
    updated, changed = re.subn(anchor_pattern, lambda m: replacement + m.group(0), text, count=count, flags=re.S)
    if not changed:
        raise ValueError(f"Could not find homepage placement anchor for {key}")
    return updated


def apply():
    photo_map = approved_photos()
    home_path = DIST / "index.html"
    home = home_path.read_text()

    # Keep the existing all-eight-guide links intact; these photographs add
    # editorial waypoints between those groups rather than making a second gallery.
    home = place(
        home,
        "african-grey-story",
        story_single(
            photo_map,
            "african-parrots",
            "African Grey Parrots",
            "grey",
            "Begin with the bird, not the picture.",
            "A species guide is a useful first step: learn about a group’s needs, then ask about the "
            "individual bird and the details that matter to your home.",
            "Read the African Grey guide",
        ),
        r'<section id="parrots" class="section species">',
    )
    home = place(
        home,
        "cockatoo-eclectus-story",
        story_pair(
            photo_map,
            "colour",
            "Distinctive looks.<br>Individual needs.",
            "From a white cockatoo to the vivid plumage of an Eclectus, every photograph here is an "
            "introduction to a group—not a promise about a bird currently available.",
            [
                ("cockatoos", "Cockatoo Parrots"),
                ("eclectus", "Eclectus Parrots"),
            ],
        ),
        r'<section class="home-feature section">',
    )
    home = place(
        home,
        "amazon-caique-story",
        story_pair(
            photo_map,
            "companions",
            "Small details. A big part of the choice.",
            "Explore different groups at your own pace. The species guides cover the birds’ care; "
            "current individual availability is always confirmed by enquiry.",
            [
                ("amazons", "Amazon Parrots"),
                ("caiques", "Caique Parrots"),
            ],
        ),
        r'<section class="enquiry section">',
    )

    # Add the dedicated stylesheet with a content hash, without changing global CSS.
    DIST.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE_CSS, DEST_CSS)
    version = hashlib.sha256(DEST_CSS.read_bytes()).hexdigest()[:12]
    stylesheet = f'<link rel="stylesheet" href="/homepage-photography.css?v={version}">'
    home = re.sub(
        r'<link rel="stylesheet" href="/homepage-photography\.css(?:\?[^"]*)?">',
        stylesheet,
        home,
    )
    if stylesheet not in home:
        home = home.replace("</head>", stylesheet + "</head>", 1)

    home_path.write_text(home)
    print("Added three distributed, approved bird-photo stories to the Crownwing homepage.")


if __name__ == "__main__":
    apply()