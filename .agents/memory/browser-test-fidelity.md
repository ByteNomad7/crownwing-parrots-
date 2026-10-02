---
name: Browser test fidelity
description: Avoid false layout failures when supplementing live screenshots with source-based browser checks.
---

Source-based browser checks supplement live verification; they do not prove that real network delivery, hosted fonts or external services work.

**Why:** Direct Chromium navigation failed while the development-domain HTTP request and running-app screenshots succeeded. Local-source checks could verify interactions independently, but should not be described as live end-to-end tests.

**How to apply:** Pair source-based interaction checks with screenshots of the running application and HTTP checks. State the distinction when it affects a claim about readiness.

Do not strip CSS imports with a regular expression that stops at the first semicolon. Quoted font URLs can themselves contain semicolons.

**Why:** Inlining styles this way corrupted the test stylesheet and produced false horizontal-overflow failures that were absent in the live preview.

**How to apply:** Use CSS-aware parsing, or remove whole known single-line import statements when constructing an isolated test document. Preserve the original cascade layers and responsive rules.

Static stylesheet changes require browser-cache invalidation, not just a workflow restart.

**Why:** The running preview reused an imported stylesheet after its source changed, so new markup rendered without the corresponding styles even though source and build checks passed.

**How to apply:** Version changed stylesheet imports or use content-hashed assets. Confirm the running preview displays the actual new styles; restarting the Python development server alone does not invalidate browser caches.

For photo-viewer checks, verify the rendered image's `currentSrc`, not only its `src` attribute or caption.

**Why:** A responsive candidate list can keep displaying the first image while the selected URL and photo counter change correctly. Attribute-only checks miss the visible failure.

**How to apply:** Exercise thumbnail selection and next/previous navigation in a real browser, wait for image loading, and compare `currentSrc` with the selected asset at desktop and mobile widths.