# Indexability audit scope

The CSV's robots/indexability columns describe source HTML metadata; its preview HTTP columns describe the actual HTTPS preview response separately. A preview `X-Robots-Tag` restriction is imposed by the preview network, not the app's HTML. It does not establish production crawlability or justify changing canonical/indexation policy. Production is not deployed/verified by this preview crawl.
