---
name: Redirect hosting verification
description: Verify real HTTP redirect support against the official reference, not generated documentation summaries
---

Treat URL rewrites and HTTP 301 redirects as different capabilities. A generated documentation-search answer is not sufficient evidence that a deployment configuration option exists.

**Why:** Documentation search gave conflicting answers and suggested an undocumented `deployment.redirects` block. The linked official static-deployment reference instead described rewrites that keep the original URL visible and listed `Location` as a reserved response header.

**How to apply:** Read the actual official configuration reference and verify status/Location behaviour before retiring public URLs. If reliable redirects require changing from static to server-hosted publishing, obtain approval for that hosting and billing change separately. Never substitute rewrites, JavaScript or meta-refresh for the requested permanent HTTP redirects.

The owner approved Autoscale server-hosted publishing after the usage-based compute billing difference was explained.

**Why:** The approved city consolidation requires actual permanent HTTP redirects rather than URL-preserving static rewrites.

**How to apply:** Preserve server-side redirect behaviour in future publishing changes. Do not revert to static-only hosting without a separately verified permanent-redirect mechanism.

Netlify is a separate supported static-host target, not equivalent to Replit Static hosting. Its official routing reference documents native `_redirects` HTTP 301s, query forwarding and automatic `404.html` handling.

**Why:** The owner subsequently requested Netlify compatibility. The earlier need for Autoscale concerned Replit's static redirect limitations, not every static host.

**How to apply:** Keep Netlify's generated routing rules aligned with the same approved merge manifest. Publish only the built static directory, retain genuine HTTP 404s for unknown URLs, and do not add an SPA homepage fallback. Verify actual Netlify-host behaviour after deployment rather than claiming local rule checks prove CDN behaviour.

Before shipping dependency lockfiles to external hosts, check for Replit-only registry addresses.

**Why:** Netlify failed before the site build because the npm lockfile referenced `package-firewall.replit.internal`, which is not resolvable outside Replit.

**How to apply:** Preserve package versions/integrity while making external-host archive URLs portable. Replit package operations may reintroduce internal URLs, so keep the external-host validation guard. Avoid installing unused development-only audit packages in the static production build.