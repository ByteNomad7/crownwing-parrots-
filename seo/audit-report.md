# Crownwing SEO source audit

- Source pages: **69**
- Configured canonical origin: `https://crownwingparrots.co.uk`
- Source route crawl: `69 / 69` HTTP requests attempted; 69 returned below 400.
- HTTP redirects observed: **0**; not-found probe status: **404**.
- Historical routes retained: **66/66**; newly observed routes since baseline: **3**; removed historical routes: **0**.
- Article-family JSON-LD: **8 routes**; explicit valid `datePublished` or `dateModified`: **4 routes** (`datePublished` on 0). Main-provided source QA reports 69/69 pages pass, eight Article routes/date checks and no route losses.
- Explicit visible source-check dates were extracted on **1 route(s)**; 43 external source links were extracted overall. Buyer/cost source-check/source-link gaps to reconcile manually: `/guides/buying-a-parrot/`, `/guides/parrot-ownership-costs/`. No review dates or sources are inferred for them.
- Deployment tooling reports `success=true`, `isDeployed=false`; no deployed artifact was validated. Production HTTPS/domain and www redirect are not verified by this preview crawl. Search Console and CrUX are unverified, not passing.
- Google Search Console connector returned no integration/property data. Manual handover: verify the `crownwingparrots.co.uk` domain property in Search Console, submit the canonical sitemap, review Page indexing/Crawl stats and inspect Performance after sufficient data accrues; record dates and property evidence. Do not infer rankings from this audit.
- Duplicate non-empty titles: **0 groups**; duplicate non-empty descriptions: **0 groups**; pages missing/multiplying H1: **0 / 0**.
- Missing alt attributes: **0** (explicit empty decorative alt is valid); local images over 500 KiB: **0**; internal links with query strings: **65**.
- Invalid JSON-LD syntax: **0**. Targeted buyer-tool interaction/browser checks were supplied and passed; no whole-site rendered crawl or field CWV measurement is claimed.
- Form semantics and submission flows are not assumed or tested here; calculator forms are not classified as enquiry/download forms by this audit.
- Local file/fragment findings: **0**; duplicate-content candidates: **0** (five-word containment ≥0.65; manual review only); thin-content review flags: **2**.
- Orphan/reachability flags: **0** with no inbound internal source; **0** unreachable from home. New routes observed since baseline: `/guides/`, `/guides/buying-a-parrot/`, `/guides/cites-parrots-uk/`. All three requested new guides passed the Replit Agent editorial/source and utility gate (`editorial-gate.md`); owner/human and professional/legal approval remains unperformed and recommended before publication. No automatic noindex.
- Preview-network caveat: X-Robots-Tag observed on 69 routes (HTTP statuses 200); the header is from the preview proxy, while page metadata is audited separately. Production is not published/verified from this preview.
- Buyer tools browser evidence (`buyer-tools-browser.json`): actual HTTPS preview tests at 1366px and 390px passed comparison/budget checks with no horizontal overflow; all eight groups remained readable without JavaScript. The evidence also covers valid budget, same-group error, reset and missing-field checks.
- Report generation is observational. It does not modify page indexability or content.

## Deliverable status

| Deliverable | Status | Evidence / limits |
|---|---|---|
| URL inventory | generated | All source index.html routes |
| Keyword map | generated | Search rankings explicitly unmeasured; Search Console not connected |
| Content cluster map | generated | Route families |
| Internal-link map | generated | Local source links classified main/chrome |
| Sitemap | copied from dist | Does not add SEO outputs to public dist |
| Robots.txt | copied from dist | Private SEO copy |
| Canonical audit | generated | Source metadata compared with configured public origin |
| Indexability audit | generated | No indexation policy changes made |
| Structured-data audit | generated | JSON parse checks only; eligibility not verified |
| Duplicate-content report | generated | Five-word shingle containment; threshold 0.65; manual-review flags |
| Thin-content report | generated | Word thresholds and exceptions; manual review only |
| Orphan-page report | generated | Internal graph reachability from home |
| Broken-link report | generated | Local files/fragments plus live crawl statuses |
| Core Web Vitals | generated | Mobile/desktop Lighthouse lab results; field CrUX unavailable; INP unmeasured |
| Mobile SEO | generated | Static checks plus supplied 390px/1366px browser evidence |
| UK legal sources | generated | Extracted cited external links; not independently verified |
| Content gaps | generated | Qualitative editorial review suggestions |
| Next content priorities | generated | Qualitative, not traffic/ranking data |
