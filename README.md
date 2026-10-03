# Crownwing Parrots

UK parrot website with species profiles, care guides, commercial pages and city pages.

The static website is in `dist/`. Publish that directory with a static web host. Content generation and validation tools are in `tools/`.

## Build and checks

- `npm run build` regenerates the website and wires the contact form.
- `npm test` checks content, SEO, photos, redirects, buyer tools and Netlify submissions.
- `npm run audit:copy` checks customer-facing pages for development/demo wording.

## Netlify

`netlify.toml` sets the build command to `npm run build` and the publish directory
to `dist`. The contact form uses Netlify Forms, not downloadable enquiry files.
Enable form detection before deploying and configure submission notifications
in Netlify to receive enquiries by email. See [NETLIFY.md](NETLIFY.md) for setup
and published-site verification.

Gallery thumbnails have no repeated bird-name captions. Species headings,
descriptive image alternatives and selected-photo captions retain meaningful
context without repeating labels beneath every image.

## AI discovery

The build also generates crawler permissions, an optional `llms.txt` directory
and readable public-page text exports. See [AI-DISCOVERY.md](AI-DISCOVERY.md)
for limitations, release checks and search-versus-training controls.
