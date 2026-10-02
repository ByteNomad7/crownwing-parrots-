# Applied changes and remaining manual review

The audit classified all 69 actual pages before changes: original 66 plus three later buyer-library additions. Those classifications remain the audit baseline, not an invented final page-count target.

## Approved consolidation completed

- 12 Great Britain city guides and /locations/ have been merged into the strongest existing guides. There are now 56 canonical HTML pages; Belfast remains as a scoped Northern Ireland aid.
- Useful city topics were consolidated into practical shared-home, weekly-care, first-time expectation, backup-care, safe-room/exercise, feeding-record, enclosure/activity and identity/terms sections. The guide library links directly to these resources, Belfast and shared contact access.
- 13 source URLs no longer have public index documents, are absent from the sitemap and are not used as internal links. Their city-labelled download forms are replaced by /contact/; no buyer records existed to delete.
- A shared redirect manifest supplies real HTTP 301s, including slashless and /index.html aliases. Query strings survive; host/protocol corrections and merges resolve in one hop.
- Autoscale configuration and the production Gunicorn/Flask workflow replace static-only hosting, with the user's approval of usage-based compute billing. No publication was performed.
- Private copies of retired city HTML are in seo/retired-city-pages/. The original audit snapshot and all 69 classifications are preserved.
- The existing brand, logo/favicon, nature-led styling, photo galleries and remaining enquiry/tool behaviour are preserved. Shared footer and breadcrumb/navigation links now go directly to surviving resources.

## Earlier safe improvements retained

- Seller checklist: specific questions and documented/observed/unknown evidence categories.
- Nutrition: feeding observations, hygiene, vet discussion and dated welfare references.
- Housing: enclosure/room screening, enrichment review and repeatable supervision.
- Home preparation: readiness, household/fume hazards and quiet arrival checks.
- Purchase prices: individual quotation/inclusion comparison, without fictitious prices.
- Belfast: DAERA/APHA source links and origin/destination/purpose checks, without local-service claims.
- Availability metadata: offered groups and details by enquiry, not implied published individual prices/ages.

## Exact permanent redirect destinations

| Retired URL | Direct destination |
|---|---|
| /locations/ | /guides/ |
| /locations/birmingham/ | /guides/choosing-a-parrot/ |
| /locations/bristol/ | /guides/preparing-for-a-parrot/ |
| /locations/cardiff/ | /guides/choosing-a-parrot/ |
| /locations/edinburgh/ | /guides/parrot-ownership-costs/ |
| /locations/glasgow/ | /guides/parrot-diet-nutrition/ |
| /locations/leeds/ | /guides/parrot-housing-enrichment/ |
| /locations/liverpool/ | /guides/buying-a-parrot-checklist/ |
| /locations/london/ | /guides/choosing-a-parrot/ |
| /locations/manchester/ | /guides/choosing-a-parrot/ |
| /locations/newcastle/ | /guides/buying-a-parrot-checklist/ |
| /locations/nottingham/ | /guides/choosing-a-parrot/ |
| /locations/sheffield/ | /guides/parrot-housing-enrichment/ |

## Verification and limits

The full npm test suite passes. Production-app tests cover all 13 redirect rules and three path variants with GET/HEAD, query retention, combined host/protocol correction, every surviving page's index/slash aliases, sitemap/robots content, no internal retired links, private-file protection, branded 404s and non-submitting contact behaviour.

All 56 surviving pages pass live mobile title/H1/navigation/error/overflow checks. The running preview uses the same Gunicorn/Flask service configured for publishing. These are development/production-app tests, not proof of a published deployment or actual Google indexing. Rebuild checks verify the 56/13 route split and managed additions remain stable.

## Remaining manual review

1. Publish the configured Autoscale app, connect/verify the owner-specified crownwingparrots.co.uk domain and check all 13 HTTP redirects on the real published host. Production has not been published or verified.
2. Confirm the 16 named species are genuinely within the intended offered range; complete the specific evidence/depth briefs without treating photos as stock proof.
3. Provide first-party business/care/buying/aftercare facts for /our-approach/. No credentials, years of experience or guarantees were invented.
4. Verify actual individual birds, prices and any handover arrangements before publishing them.
5. Obtain Search Console/backlink history and field-CWV evidence. Historical city traffic, rankings, keyword volumes/difficulty and Google indexation remain unverified.
6. Keep legal/veterinary professional review distinct from editorial source checks.
