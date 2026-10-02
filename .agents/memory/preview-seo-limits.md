---
name: Preview SEO limits
description: Distinguish development-proxy indexing restrictions from the site's own SEO configuration.
---

Do not change Crownwing's canonical hostname or source indexing policy merely to improve a development-host Lighthouse score.

**Why:** The HTTPS preview crawl returned an externally added `X-Robots-Tag` blocking indexing, despite indexable app metadata and an allowing robots.txt. Lighthouse's indexing failure was a network-environment limitation, not an accidental page noindex. Official documentation search did not establish a universal platform policy, so treat it as an observed condition rather than a guarantee.

**How to apply:** Inspect response headers as well as HTML. Label preview lab results honestly; separately verify HTTPS, hostname redirects, crawlability and Search Console on the published host. Never claim Google indexing or field Core Web Vitals from a preview lab test.