# Crownwing Parrots

## Run on Replit

Use the **Start application** workflow (the Run button) to serve the existing static website:

```sh
python3 -m gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 4 --access-logfile - tools.production_site:app
```

The production-ready Gunicorn/Flask service serves generated `dist/` HTML directly, with no client-side rendering requirement. It supplies approved HTTP 301s, canonical path/host aliases and a branded 404, without directory listings. Runtime packages are tracked in `pyproject.toml` and `uv.lock`; no secrets or database are required. Source-driven updates use `python3 tools/apply-breeder-positioning.py` to rebuild the site.

## Project maintenance

- Keep the existing static HTML, CSS, JavaScript, and images in `dist/`.
- Content generation and validation scripts live in `tools/`.
- Check the site's links, metadata, structured data, and sitemap with `python3 tools/check-site.py`.
- After changing pages or image metadata, also run `python3 tools/check-seo-enhancements.py` to verify sharing images, site identity, image dimensions and responsive sources.
- Run `python3 tools/check-buyer-search-intent.py` after changing commercial copy to verify buying keywords, enquiry boundaries and the separation from informational guides.
- Run `npm test` for the complete generated-site and buyer-tools checks. Lighthouse is a development-only tool; Node is not needed to serve the website.
- Buyer library content lives in `tools/buyer_resource_content.py`; scoped calculator/comparison assets live in `site/`. Both tools retain readable content without JavaScript and do not send or store user inputs.
- Run `python3 tools/audit-seo-foundation.py --final --crawl` after a rebuild with the preview running. Evidence and downloadable reports live in private workspace `seo/`, not public `dist/`.
- The full qualitative audit is in `seo/crownwing-page-classification.md` and its implementation plan/summary. Its original 66-page cohort is distinguished from the 3 later buyer-library pages; classifications are not automatic implementation instructions.
- Preserve `seo/crownwing-classification-before.json` as the pre-change audit evidence. The complete audit helper overwrites that snapshot, so do not rerun it over an implemented site merely to refresh technical evidence.
- Audit-led practical additions and owner-approved city consolidation are applied by the generator. `site/redirects.json` is shared by production and validation: 13 legacy routes resolve directly to guides; Belfast remains. Do not restore city index documents during rebuilds.
- Run `tools/finalize-city-consolidation.py` after current mobile evidence to refresh the implementation reports without overwriting the original 69-page audit. The older classification finaliser intentionally validates the pre-consolidation safe-expansion phase only.
- Preserve `seo/content-register.json` across rebuilds. Historical dates are unknown unless verified; only substantive main-content changes update sitemap `lastmod`. Source-check dates are editorial checks, not professional review or proof of a bird's legality.
- The UK documentation guide distinguishes England/Wales, Scotland, Great Britain and Northern Ireland. Recheck its linked official sources before changing regulatory claims; no universal paperwork or transport promise.
- Availability thumbnails repeat their adjacent group labels visually: keep them decorative (`alt=""`, `aria-hidden="true"`). All meaningful gallery and bird images need accurate descriptive alternatives.
- Enquiry forms currently download a text copy; they do not send enquiries to an inbox or save them on a server.
- The owner-specified canonical origin is `https://crownwingparrots.co.uk`, configured centrally in `tools/site_config.py`. All canonicals, social metadata, structured data and the sitemap must use it, not preview or imported-site domains.
- The shared footer is generated in `tools/apply-breeder-positioning.py` and styled by `dist/footer.css`; retain the original brand and all policy links.
- Setting the canonical origin does not publish the site or connect domain DNS; configure the custom domain when publishing.
- Publishing is configured for Autoscale with Gunicorn/Flask, with owner approval of usage-based compute billing. The build generates static HTML, but the production server is required for permanent redirects; publishing raw `dist/` alone loses that behaviour.
- Netlify is also supported via root `netlify.toml` and generated `dist/_redirects`/`404.html`; its native redirect engine supplies the permanent HTTP redirects. See `NETLIFY.md`. Never add a catch-all homepage rewrite.