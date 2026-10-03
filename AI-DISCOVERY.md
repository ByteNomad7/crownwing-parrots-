# AI search discoverability

Crownwing's public HTML remains the primary source for search and AI citations.
The site is rendered as static HTML, with canonical URLs, a sitemap, descriptive
images, internal links, official-source links in guides and structured data.

## What the build adds

- Explicit `robots.txt` access for OpenAI search, Perplexity, Claude search,
  Google and Bing, plus the existing wildcard permission for other crawlers.
- A visible buying FAQ whose answers match its JSON-LD exactly.
- Business identity structured data linked to the existing contact page and
  company approach page. No invented stock, prices, reviews or qualifications.
- An optional `/llms.txt` directory of all sitemap-listed public pages.
- `/ai-pages/*.md` text exports derived from each page's main content, including
  links to source material. Navigation, scripts and form fields are excluded.
  Each export identifies the original HTML URL as the citation target.

`llms.txt` is an emerging convention, not a universally supported discovery
standard. Google explicitly says its AI search features require no additional
AI-specific files or special schema. These text exports supplement HTML; they
do not replace search indexing or fix Search Console errors.

Text exports are excluded from the XML sitemap and served with
`X-Robots-Tag: noindex` to avoid creating duplicate search landing pages.
Netlify uses generated `dist/_headers`; the Flask preview supplies equivalent
headers. Normal HTML pages remain indexable.

## Search versus model training

Search discovery is different from model training. The previous wildcard
`Allow: /` remains unchanged, including its treatment of training crawlers.
This update does not introduce a separate training opt-in or opt-out.
OpenAI's `OAI-SearchBot` and `GPTBot` are independent controls; Claude also
distinguishes search, user retrieval and model-development crawlers.

## Release and verification

1. Run `npm run build` and `npm test`. Generated files must survive rebuilding.
2. Deploy the updated build through the existing Netlify release process.
3. Check `/robots.txt`, `/llms.txt` and `/ai-pages/home.md` on the published
   domain. Check their response codes, content types and headers.
4. Check that hosting firewalls or bot protection do not block legitimate
   crawler IPs. A successful request with a spoofed user-agent is not proof that
   the actual provider can crawl the site.
5. Confirm Google Search Console sitemap processing, inspect important pages,
   and submit the same sitemap in Bing Webmaster Tools. This requires access
   to the owner's accounts; local checks cannot confirm provider-side indexing.
6. Periodically check representative buying and care queries in AI search.
   Record the date, query, cited URL and engine, rather than claiming a score
   or guaranteed visibility. Referral data can supplement these checks.

## Primary documentation

- OpenAI: https://developers.openai.com/api/docs/bots
- Claude: https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler
- Google: https://developers.google.com/search/docs/appearance/ai-features
- Perplexity: https://www.perplexity.ai/help-center/en/articles/10354969-how-does-perplexity-follow-robots-txt
- Netlify custom headers: https://docs.netlify.com/manage/routing/headers/