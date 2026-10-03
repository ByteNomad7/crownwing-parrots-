---
name: Impure helper persistence
description: Cross-call reuse of an impure sandbox function can fail even when inline execution works.
---

For multi-batch connector work, persist serializable progress between calls, but recreate the impure helper inside each execution block.

**Why:** A helper containing `use impure` worked in its defining block but failed when invoked from a later notebook block with `executeJs is not defined`. Recreating the same helper inline succeeded.

**How to apply:** Keep connection clients local to each impure call and pass ordinary IDs, offsets and hashes between batches. Do not interpret this helper-reuse error as a missing integration or request credentials again.