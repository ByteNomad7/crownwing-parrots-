"""Apply the curated uploaded-photo catalogue to the existing static site.

Run with --archive PATH on first import to create optimised WebP assets.
Subsequent runs are idempotent and do not require the original archive.
"""

import argparse
import hashlib
import html
import json
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MANIFEST = ROOT / "tools/photo-metadata.json"
OLD_IMAGES = {
    "grey.jpg": "african-parrots",
    "macaw.jpg": "macaws",
    "cockatoo.jpg": "cockatoos",
    "amazon.jpg": "amazons",
    "conure.jpg": "conures",
    "caique.jpg": "caiques",
    "eclectus.jpg": "eclectus",
    "parakeet.jpg": "parakeets-small-psittacines",
}


def esc(value):
    return html.escape(str(value), quote=True)


def import_assets(catalogue, archive):
    total_original = total_optimised = 0
    imported = 0
    with zipfile.ZipFile(archive) as bundle, tempfile.TemporaryDirectory() as work:
        for photo in catalogue["photos"]:
            if photo.get("sourceArchive") and photo["sourceArchive"] != archive.name:
                continue
            source = photo["sourceFile"]
            source_path = Path(source)
            if (source_path.is_absolute() or ".." in source_path.parts
                    or "\\" in source or source.startswith("__MACOSX/")
                    or source_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}):
                raise ValueError(f"Unsafe archive entry: {source}")
            data = bundle.read(source)
            if photo.get("sourceHash") and hashlib.sha256(data).hexdigest() != photo["sourceHash"]:
                raise ValueError(f"Source photo has changed: {source}")
            original = Path(work) / source_path.name
            original.write_bytes(data)
            imported += 1
            total_original += original.stat().st_size
            for key, size, quality in [("src", 2000, 84), ("thumbnail", 480, 80)]:
                target = DIST / photo[key].lstrip("/")
                target.parent.mkdir(parents=True, exist_ok=True)
                subprocess.run(
                    ["magick", str(original), "-auto-orient", "-resize",
                     f"{size}x{size}>", "-strip", "-quality", str(quality),
                     str(target)], check=True,
                )
                dimensions = subprocess.check_output(
                    ["magick", "identify", "-format", "%w %h", str(target)],
                    text=True,
                ).split()
                prefix = "" if key == "src" else "thumbnail"
                width_key = "width" if not prefix else "thumbnailWidth"
                height_key = "height" if not prefix else "thumbnailHeight"
                photo[width_key], photo[height_key] = map(int, dimensions)
                total_optimised += target.stat().st_size
    if not imported:
        raise ValueError(f"No catalogue photos match archive: {archive.name}")
    MANIFEST.write_text(json.dumps(catalogue, indent=2) + "\n")
    print(f"Imported {imported} photos: "
          f"{total_original:,} source bytes → {total_optimised:,} web bytes.")


def photo_image(photo, *, hero=False, thumbnail=False, responsive=True):
    source = photo["thumbnail"] if thumbnail else photo["src"]
    width = photo.get("thumbnailWidth", photo["width"]) if thumbnail else photo["width"]
    height = photo.get("thumbnailHeight", photo["height"]) if thumbnail else photo["height"]
    attributes = [
        f'src="{esc(source)}"', f'alt="{esc(photo["label"])}"',
        f'width="{width}"', f'height="{height}"', 'decoding="async"',
    ]
    if hero:
        attributes += ['fetchpriority="high"', 'loading="eager"']
    else:
        attributes.append('loading="lazy"')
    if responsive and not thumbnail and photo.get("thumbnailWidth", 0) < photo["width"]:
        attributes += [
            f'srcset="{esc(photo["thumbnail"])} {photo["thumbnailWidth"]}w, '
            f'{esc(photo["src"])} {photo["width"]}w"',
            'sizes="(max-width: 760px) 100vw, 50vw"' if hero else
            'sizes="(max-width: 430px) 90vw, (max-width: 1050px) 44vw, 25vw"',
        ]
    focus = photo.get("focus", "50% 35%")
    attributes.append(f'style="object-position:{esc(focus)}"')
    return "<img " + " ".join(attributes) + ">"


def photo_data(photo):
    return (f'data-photo-src="{esc(photo["src"])}" '
            f'data-photo-alt="{esc(photo["label"])}" '
            f'data-photo-width="{photo["width"]}" '
            f'data-photo-height="{photo["height"]}"')


def thumbnail_button(photo):
    return (
        f'<button type="button" class="photo-thumbnail" {photo_data(photo)} '
        f'aria-label="Enlarge {esc(photo["label"])}" aria-haspopup="dialog">'
        f'{photo_image(photo, thumbnail=True)}'
        '</button>'
    )


def gallery_markup(photos):
    primary = photos[0]
    identification_notes = sorted({
        p["identificationDisplayNote"] for p in photos if p.get("identificationDisplayNote")
    })
    identification_note = " ".join(identification_notes)
    if identification_note:
        identification_note = esc(identification_note) + " "
    featured = "".join(thumbnail_button(p) for p in photos[1:5])
    more = ""
    if len(photos) > 5:
        more = (
            '<details class="photo-collection" open>'
            f'<summary>{len(photos) - 5} additional photos</summary>'
            '<div class="photo-collection-grid">'
            + "".join(thumbnail_button(p) for p in photos[5:])
            + "</div></details>"
        )
    return (
        '<div class="detail-gallery">'
        f'<button type="button" class="gallery-main" {photo_data(primary)} '
        f'aria-label="Enlarge {esc(primary["label"])}" aria-haspopup="dialog">'
        f'{photo_image(primary, hero=True, responsive=False)}</button>'
        f'<p class="gallery-caption">{esc(primary["label"])}'
        f'<span>{len(photos)} photos in this collection</span></p>'
        f'<div class="gallery-slots photo-thumbnails" '
        f'style="--photo-columns:{max(1, min(4, len(photos) - 1))}">{featured}</div>{more}'
        f'<p class="gallery-note">{identification_note}Species-group photographs do not indicate '
        'individual availability.</p></div>'
    )


def dialog_markup(photo):
    return (
        '<dialog id="photo-dialog" aria-label="Enlarged parrot photographs">'
        '<button type="button" class="close" aria-label="Close enlarged photo">×</button>'
        '<button type="button" class="photo-prev" aria-label="Previous photo">‹</button>'
        f'<img src="{esc(photo["src"])}" alt="{esc(photo["label"])}">'
        '<button type="button" class="photo-next" aria-label="Next photo">›</button>'
        '<p class="photo-dialog-caption" aria-live="polite"></p></dialog>'
    )


def apply_catalogue(catalogue):
    photos = {p["id"]: p for p in catalogue["photos"]}
    covers = {group: photos[pid] for group, pid in catalogue["primaryByGroup"].items()}
    hero = photos[catalogue["heroPhotoId"]]
    by_source = {p["src"]: p for p in photos.values()}
    updated = 0

    for page in sorted(DIST.rglob("index.html")):
        original = page.read_text()
        text = original
        # Sample attribution is removed only together with the sample images.
        text = re.sub(r'<div class="credits">.*?</div>', "", text, flags=re.S)
        text = re.sub(r'<p class="photo-credit">.*?</p>', "", text, flags=re.S)

        if page == DIST / "index.html":
            def fill_hero_slot(match):
                slot = match[0]
                opening = slot[:slot.index(">") + 1]
                content = re.sub(r"<img\b[^>]*>", "", slot[len(opening):-6])
                return opening + photo_image(hero, hero=True) + content + "</div>"

            text = re.sub(
                r'<div\b[^>]*\bdata-hero-photo(?:="[^"]*")?[^>]*>.*?</div>',
                fill_hero_slot, text, count=1, flags=re.S,
            )
            text = re.sub(
                r'(<div class="hero-photo">)\s*<img\b[^>]*>',
                lambda m: m[1] + photo_image(hero, hero=True), text, count=1,
            )
            text = re.sub(
                r'<div class="hero-note">.*?</div>',
                '<div class="hero-note"><span>Hyacinth macaw<br>'
                '<small>Anodorhynchus hyacinthinus</small></span></div>',
                text, count=1, flags=re.S,
            )

        def fill_group_slot(match):
            slot, group = match[0], match[2]
            photo = covers.get(group)
            if not photo:
                return ""
            opening = slot[:slot.index(">") + 1]
            content = re.sub(r"<img\b[^>]*>", "", slot[len(opening):-6])
            return opening + photo_image(photo) + content + "</div>"

        text = re.sub(
            r'<div class="(card-photo|approach-photo)" data-photo-group="([^"]+)"[^>]*>.*?</div>',
            fill_group_slot, text, flags=re.S,
        )

        def fill_editorial_slot(match):
            photo = covers.get(match[1])
            if not photo:
                return ""
            return (
                f'<figure class="editorial-photo" data-photo-group="{esc(match[1])}">'
                f'{photo_image(photo)}<figcaption>{esc(photo["label"])}</figcaption></figure>'
            )

        text = re.sub(
            r'<figure\b[^>]*data-photo-group="([^"]+)"[^>]*>.*?</figure>',
            fill_editorial_slot, text, flags=re.S,
        )

        def replace_sample_image(match):
            tag = match[0]
            source = re.search(r'\bsrc=["\']([^"\']+)["\']', tag)
            if not source:
                return tag
            path = source[1].lstrip("/")
            name = path.removeprefix("assets/")
            if path.startswith("assets/") and name in OLD_IMAGES:
                photo = covers.get(OLD_IMAGES[name])
                return photo_image(photo) if photo else ""
            return tag

        text = re.sub(r"<img\b[^>]*>", replace_sample_image, text)

        def tidy_editorial_figure(match):
            figure = match[0]
            if "<img" not in figure:
                return ""
            if re.search(r"Representative species photo|Photo credit|creativecommons", figure):
                source = re.search(r'<img[^>]+src="([^"]+)"', figure)
                photo = by_source.get(source[1]) if source else None
                caption = esc(photo["label"]) if photo else "Parrot photograph"
                figure = re.sub(
                    r"<figcaption>.*?</figcaption>",
                    f"<figcaption>{caption}</figcaption>", figure, flags=re.S,
                )
            return figure

        text = re.sub(r"<figure\b[^>]*>.*?</figure>", tidy_editorial_figure, text, flags=re.S)

        def tidy_card(match):
            card = match[0]
            group = re.search(r'href="/parrots/([^/]+)/"', card)
            photo = covers.get(group[1]) if group else None
            if photo and "<img" not in card:
                image_slot = (
                    f'<div class="card-photo" data-photo-group="{esc(group[1])}">'
                    f'{photo_image(photo)}</div>'
                )
                card = re.sub(r'<div class="card-photo"[^>]*>.*?</div>', "", card, flags=re.S)
                card = card.replace('<div class="card-copy">', image_slot + '<div class="card-copy">', 1)
                card = card.replace("species-card--guide ", "")
                card = card.replace('<p class="eyebrow">Species guide</p>', "", 1)
            if "<img" not in card:
                card = re.sub(r'<div class="card-photo"[^>]*>.*?</div>', "", card, flags=re.S)
                if "species-card--guide" not in card:
                    card = card.replace('class="species-card ', 'class="species-card species-card--guide ', 1)
                    card = card.replace('<div class="card-copy">',
                                        '<div class="card-copy"><p class="eyebrow">Species guide</p>', 1)
            return card

        text = re.sub(
            r'<a\b(?=[^>]*class="[^"]*\bspecies-card\b)[^>]*>.*?</a>',
            tidy_card, text, flags=re.S,
        )

        relative = page.relative_to(DIST).parts
        editorial_groups = {
            "african-grey-parrots": "african-parrots",
            "macaws": "macaws", "cockatoos": "cockatoos",
            "amazon-parrots": "amazons", "conures": "conures",
            "caiques": "caiques", "eclectus-parrots": "eclectus",
            "parakeets-small-parrots": "parakeets-small-psittacines",
        }
        if len(relative) == 3 and relative[0] == "parrots-for-sale":
            group = editorial_groups.get(relative[1])
            photo = covers.get(group)
            if photo and 'class="editorial-photo"' not in text:
                figure = (
                    f'<figure class="editorial-photo" data-photo-group="{esc(group)}">'
                    f'{photo_image(photo)}<figcaption>{esc(photo["label"])}</figcaption></figure>'
                )
                text = re.sub(r'(<section class="page-intro">.*?)(</section>)',
                              lambda m: m[1] + figure + m[2], text, count=1, flags=re.S)
        if len(relative) == 3 and relative[0] == "parrots":
            group = relative[1]
            matching = [p for p in photos.values() if p["group"] == group and p.get("publish", True)]
            if group in covers:
                matching.sort(key=lambda p: (
                    p["id"] != covers[group]["id"],
                    p["identificationConfidence"] == "provisional",
                    p["id"],
                ))
            gallery = gallery_markup(matching) if matching else ""
            if '<div class="detail-gallery"' in text:
                text = re.sub(r'<div class="detail-gallery".*?(?=</section>)',
                              lambda _: gallery, text, count=1, flags=re.S)
            elif gallery:
                text = re.sub(r'(<section class="detail-intro">.*?)(</section>)',
                              lambda m: m[1] + gallery + m[2], text, count=1, flags=re.S)
            text = re.sub(r'<dialog id="photo-dialog".*?</dialog>', "", text, flags=re.S)
            if matching:
                text = re.sub(r'(<script src="/detail\.js(?:\?[^"]*)?">)',
                              lambda m: dialog_markup(matching[0]) + m[1], text, count=1)

        if text != original:
            page.write_text(text)
            updated += 1

    # No old sample asset is deleted while a public reference still exists.
    public_text = "\n".join(p.read_text() for p in DIST.rglob("*.html"))
    for old in OLD_IMAGES:
        if f"/assets/{old}" in public_text or f"assets/{old}" in public_text:
            raise ValueError(f"Sample photo still referenced: {old}")
    for old in OLD_IMAGES:
        (DIST / "assets" / old).unlink(missing_ok=True)
    print(f"Updated {updated} pages; published "
          f"{sum(p.get('publish', True) for p in photos.values())} matched photographs.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    catalogue = json.loads(MANIFEST.read_text())
    if args.archive:
        import_assets(catalogue, args.archive)
    for photo in catalogue["photos"]:
        if photo.get("publish", True):
            for key in ("src", "thumbnail"):
                if not (DIST / photo[key].lstrip("/")).is_file():
                    raise FileNotFoundError(photo[key])
    apply_catalogue(catalogue)


if __name__ == "__main__":
    main()