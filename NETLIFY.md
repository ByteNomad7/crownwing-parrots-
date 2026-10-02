# Publish Crownwing on Netlify

## Git-connected site

Commit/push the updated project, including the existing `dist/` assets.
The root `netlify.toml` supplies these settings:

- Base directory: repository root (leave blank).
- Build command: `npm run build`.
- Publish directory: `dist`.
- Python: 3.12; Node: 22.

Redeploy after updating the repository. Netlify serves the HTML files directly;
do not configure the Gunicorn command as its build command.

## Manual upload

Extract the provided `crownwing-netlify.zip`, or use the built `dist` folder.
Upload the folder whose top level contains `index.html`,
`_redirects`, `404.html`, `assets/`, and the page folders.
Do not upload the repository root or only the homepage file.

## Routing and checks

The build creates `_redirects` from the 13 approved city/directory mappings,
plus explicit index-file aliases. Netlify handles slashless equivalents and
preserves query parameters. It also automatically uses `404.html` for missing
paths. No catch-all rewrite sends every URL to the homepage.

After deploying, verify:

- `/`, `/available-birds/`, a species gallery, and `/guides/` load.
- `/locations/london/?keep=1` redirects permanently to
  `/guides/choosing-a-parrot/?keep=1`.
- `/locations/belfast/` remains available.
- An invented URL returns HTTP 404 with the Crownwing error page.
- Photos change when clicking thumbnails or viewer arrows.

The canonical domain remains the owner-specified `crownwingparrots.co.uk`.
Connect/verify that domain in Netlify if Netlify is the chosen production host.
If the root URL still displays Netlify's default 404, inspect the published
deploy's file browser for `index.html` and confirm the custom domain is attached
to the correct Netlify site. A screenshot alone cannot distinguish a wrong
publish folder from a missing/stale deploy or a domain pointing at another site.

Replit's existing Autoscale configuration is unchanged; Netlify uses native
static-host redirect rules instead of that Python server.