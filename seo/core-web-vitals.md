# Core Web Vitals

Lighthouse figures are lab measurements, not field Core Web Vitals. INP remains unmeasured.
- mobile: Lighthouse performance score 87; accessibility 100; best practices 100; LCP 2.9 s; CLS 0; TBT 0 ms; INP unmeasured. Lighthouse SEO score 66; failed SEO audits: is-crawlable.
- desktop: Lighthouse performance score 99; accessibility 100; best practices 100; LCP 0.8 s; CLS 0.011; TBT 0 ms; INP unmeasured. Lighthouse SEO score 66; failed SEO audits: is-crawlable.

**Preview-proxy crawlability limitation:** the HTTPS preview responds with `X-Robots-Tag: none, noindex, noarchive, nofollow, nositelinkssearchbox, noimageindex`. Lighthouse's `is-crawlable` failure reflects that preview-network header, not page markup. Source HTML metadata remains indexable where shown; this preview is not a published production origin and this report does not claim Google can crawl it.
