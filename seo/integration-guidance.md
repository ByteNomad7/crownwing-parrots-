# Content registry integration

`tools/content_registry.py` exposes:

- `sync_content_registry(dist) -> mapping`, keyed by canonical route (for example
  `/guides/example/`). Each value has `published`, `last_modified`,
  `last_reviewed`, `reviewed_by`, `review_scope`, `review_status`, `sources`,
  `owner`, `publisher`, `review_reminder_due` and `history`.
- `write_sitemap(dist, origin, paths)`, which writes the supplied indexable paths
  to `dist/sitemap.xml`. It adds `<lastmod>` only where a registry date is known.

Date meanings:

- `published` is `null` until deployment/publication is independently established;
  a local static build is not proof of publication.
- `last_modified` stays `null` for the 66-route historical baseline. On later
  runs it changes only when extracted main-content headings/paragraphs or image
  source URLs change. New routes first observed after baseline receive their
  observed creation date. Template, navigation, metadata and style-only changes
  do not bump it.
- `last_reviewed` is populated only from visible, explicit `Sources checked:
  YYYY-MM-DD` copy. Such entries are marked `review_status: sources_checked`,
  with scope clarifying that this is not expert review and no person is named.
  The reminder is six calendar months from that explicit source-check date.

For a real dated article, supply the article's verified publication date in its
Article metadata independently of this registry; do not use today's date as a
fallback or derive an article date from a build. The registry does not infer
publication dates. Before sitemap generation, call the synchroniser and pass
the generator's actual indexable route list:

```python
from content_registry import sync_content_registry, write_sitemap

sync_content_registry(dist)
write_sitemap(dist, PUBLIC_ORIGIN, indexable_paths)
```

For eligible dated `Article` JSON-LD, use the article's genuine source date as
`datePublished`. Set `dateModified` only to a genuine, observed substantive
editorial change date from the registry (or omit it when unknown). Do not
convert a registry `last_reviewed` value into `dateModified`, and do not add
Article dates to service, legal, calculator or other non-article pages. These
SEO reports and the registry live under workspace `seo/`; only the sitemap
helper's explicitly supplied `dist` destination is intended for generator
integration.