# Publish Crownwing on Netlify

## Git-connected site

Commit/push the updated project, including the existing `dist/` assets.
The root `netlify.toml` supplies these settings:

- Base directory: repository root (leave blank).
- Build command: `npm run build`.
- Publish directory: `dist`.
- Python: 3.12; Node: 22.
- Npm registry: public `https://registry.npmjs.org`.
- Install flags: `--omit=dev`. The static build uses Python's standard library,
  not the development-only Lighthouse audit package.

Redeploy after updating the repository. Netlify serves the HTML files directly;
do not configure the Gunicorn command as its build command.

If a build log reports `ENOTFOUND package-firewall.replit.internal`, push the
updated `package-lock.json` and `netlify.toml`, then retry with a cleared build
cache. The lockfile preserves the same versions and integrity hashes but uses
public npm archive URLs. Ensure the deploy is building the commit containing
these fixes; changing the build command alone cannot fix an earlier dependency
installation failure.

## Manual upload

Extract the provided `crownwing-netlify.zip`, or use the built `dist` folder.
Upload the folder whose top level contains `index.html`,
`_redirects`, `404.html`, `assets/`, and the page folders.
Do not upload the repository root or only the homepage file.

## Contact form

The contact form uses **Netlify Forms**, named `contact`, with a spam honeypot.
It submits the customer's name, email, bird interest and message, rather than
downloading a file. No API key or custom server is required.

Before deploying:

1. Open your Netlify site's **Forms** section and **Enable form detection**.
2. Redeploy the updated site (or upload the updated ZIP).
3. Confirm the `contact` form appears in **Forms**, then submit a test enquiry
   on the published site and check it appears under submissions.
4. For email delivery, go to **Forms > Submission notifications >
   Add notification**, choose email, and set the Crownwing inbox you want to use.

The Replit preview cannot receive Netlify Forms submissions. It will show an
honest submission error, not a false success. Published submission storage and
email receipt must be checked after the Netlify redeploy.

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