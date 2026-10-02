# Crownwing Parrots

## Run on Replit

Use the **Start application** workflow (the Run button) to serve the existing static website:

```sh
python3 tools/serve-site.py --port 5000 --bind 0.0.0.0 --directory dist
```

The preview serves `dist/` directly, including its nested page directories. The standard-library server adds canonical URL aliases, a branded HTTP 404, and disables directory listings. There are no third-party runtime dependencies, required secrets or database. Source-driven updates use `python3 tools/apply-breeder-positioning.py` to rebuild the site.

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
- Audit-led practical additions live in `tools/audit_quality_content.py` and are applied by the existing generator. Proposed city retirements need informed owner approval and production-supported HTTP redirects; preview-only Python redirects cannot be assumed to work on static hosting.
- Preserve `seo/content-register.json` across rebuilds. Historical dates are unknown unless verified; only substantive main-content changes update sitemap `lastmod`. Source-check dates are editorial checks, not professional review or proof of a bird's legality.
- The UK documentation guide distinguishes England/Wales, Scotland, Great Britain and Northern Ireland. Recheck its linked official sources before changing regulatory claims; no universal paperwork or transport promise.
- Availability thumbnails repeat their adjacent group labels visually: keep them decorative (`alt=""`, `aria-hidden="true"`). All meaningful gallery and bird images need accurate descriptive alternatives.
- Enquiry forms currently download a text copy; they do not send enquiries to an inbox or save them on a server.
- The owner-specified canonical origin is `https://crownwingparrots.co.uk`, configured centrally in `tools/site_config.py`. All canonicals, social metadata, structured data and the sitemap must use it, not preview or imported-site domains.
- The shared footer is generated in `tools/apply-breeder-positioning.py` and styled by `dist/footer.css`; retain the original brand and all policy links.
- Setting the canonical origin does not publish the site or connect domain DNS; configure the custom domain when publishing.
- For static hosting, publish `dist/`; the Python server above is for the development preview.