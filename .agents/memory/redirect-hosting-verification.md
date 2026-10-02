---
name: Redirect hosting verification
description: Verify real HTTP redirect support against the official reference, not generated documentation summaries
---

Treat URL rewrites and HTTP 301 redirects as different capabilities. A generated documentation-search answer is not sufficient evidence that a deployment configuration option exists.

**Why:** Documentation search gave conflicting answers and suggested an undocumented `deployment.redirects` block. The linked official static-deployment reference instead described rewrites that keep the original URL visible and listed `Location` as a reserved response header.

**How to apply:** Read the actual official configuration reference and verify status/Location behaviour before retiring public URLs. If reliable redirects require changing from static to server-hosted publishing, obtain approval for that hosting and billing change separately. Never substitute rewrites, JavaScript or meta-refresh for the requested permanent HTTP redirects.