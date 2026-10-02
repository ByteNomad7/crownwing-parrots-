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
- Enquiry forms currently download a text copy; they do not send enquiries to an inbox or save them on a server.
- Canonical URLs and the sitemap retain the imported site's domain. Review these before publishing under a different domain.
- For static hosting, publish `dist/`; the Python server above is for the development preview.