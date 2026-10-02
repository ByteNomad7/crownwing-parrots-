# Technical SEO and experience evidence

## Coverage

- All 69 canonical routes crawled through the running HTTPS preview; HTTP 200 count 69.
- Every route rendered at 390×900 with JavaScript, live H1/canonical/link checks, overflow containment and mobile-menu opening; observed failures 0.
- Every source checked for metadata, headings, assets, image attributes, schema syntax/types and sitemap inclusion.
- No client-side route shell; meaningful main content and normal href links are in response HTML.
- Current generated HTML and served body hashes compared, including all 69 pages.
- Query probe is identical to the canonical commercial response: True.
- A nonexistent route returns 404; uppercase probe returns 404.
- Existing index-document/slash aliases resolve to canonical routes; source tests cover combined www/HTTPS/path handling. No published-host www/DNS/redirect assertion is made.

## Indexing and sitemap

Source robots content:

User-agent: *
Allow: /
Sitemap: https://crownwingparrots.co.uk/sitemap.xml

The actual preview robots response starts with: 'User-agent: *\nAllow: /\nSitemap: https://crownwingparrots.co.uk/sitemap.xml\n'. Sitemap response content type: text/xml. Source sitemap has 69 entries; 0 current route mismatches.

Development-proxy noindex affects 69 routes. Do not change truthful canonicals or application policy to raise a preview Lighthouse SEO score. Published-host headers and Search Console need a separate check.

## Structured data

Recursive @graph/type extraction is used; graph containers are not falsely reported as unknown schema. JSON syntax is checked. Organization/WebSite, WebPage/CollectionPage, BreadcrumbList and Article types should match visible roles. No Product/Offer/Review/AggregateRating is justified by educational photos or group-by-enquiry pages. Publication/expert-review dates and reviewers remain unknown unless genuinely supported; no requirement is solved by fabricating them.

## Images and external references

Every source image occurrence is in crownwing-image-audit.csv, including alt role, dimensions, source bytes, responsive sources and loading/priority. Decorative labelled thumbnails and branding are treated differently from meaningful bird photos. Filename/alt correctness and ambiguous mutation/hybrid identities require owner/editorial verification; a present alt is not proof of exact species or current stock. Compression analysis uses source bytes, not full browser transfer size.

All 20 distinct external href references returned readable content through webFetch and are saved in crownwing-external-source-checks.json. This is not a raw HTTP-status claim or legal/veterinary endorsement. SpeciesPlus requires interactive species-specific lookup. Older Eclectus roratus references can refer to a broader pre-split complex: do not present them as Papuan-specific taxonomy evidence. External information and rules can change.

## Page speed, accessibility and limits

Existing choosing-guide Lighthouse results remain applicable because public pages were not changed: mobile 87 / LCP 2.9s / CLS 0 / TBT 0; desktop 99 / LCP 0.8s / CLS 0.011. Mobile LCP is above the 2.5s good threshold in that lab run. Investigate font/image resource timing on representative homepage, commercial, image-heavy species and legal templates before claiming site-wide performance.

No field CWV/INP, production CrUX, complete route-by-route Lighthouse run, screen-reader audit or WCAG conformance claim. All-page mobile structural/navigation checks are broader than the previous two-tool tests, but do not cover every gallery/form interaction. Existing buyer-tools-browser.json covers desktop/mobile comparison and budget interactions plus no-JS safeguards.

## Mechanical source findings

None observed.