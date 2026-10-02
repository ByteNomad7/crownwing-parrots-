# Crownwing Parrots

## Run on Replit

Use the **Start application** workflow (the Run button) to serve the existing static website:

```sh
python3 -m http.server 5000 --bind 0.0.0.0 --directory dist
```

The preview serves `dist/` directly, including its nested page directories. Python 3.12 is already configured; there are no third-party runtime dependencies, required secrets, database, or build step.

## Project maintenance

- Keep the existing static HTML, CSS, JavaScript, and images in `dist/`.
- Content generation and validation scripts live in `tools/`.
- Check the site's links, metadata, structured data, and sitemap with `python3 tools/check-site.py`.
- After changing pages or image metadata, also run `python3 tools/check-seo-enhancements.py` to verify sharing images, site identity, image dimensions and responsive sources.
- Enquiry forms currently download a text copy; they do not send enquiries to an inbox or save them on a server.
- The owner-specified canonical origin is `https://crownwingparrots.co.uk`, configured centrally in `tools/site_config.py`. All canonicals, social metadata, structured data and the sitemap must use it, not preview or imported-site domains.
- The shared footer is generated in `tools/apply-breeder-positioning.py` and styled by `dist/footer.css`; retain the original brand and all policy links.
- Setting the canonical origin does not publish the site or connect domain DNS; configure the custom domain when publishing.
- For static hosting, publish `dist/`; the Python server above is for the development preview.