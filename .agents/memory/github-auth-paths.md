---
name: GitHub authorization paths
description: Connected GitHub access can work independently of the workspace Git credential helper.
---

A working GitHub App connection does not necessarily repair authentication for `git push` through an existing HTTPS remote.

**Why:** The connected account had repository write access through the authenticated connector while the Git CLI continued rejecting its existing credentials.

**How to apply:** Use the managed connection without extracting tokens. If transferring commits through GitHub's Git database API, preserve their files, metadata and parent history, verify object hashes, and advance the branch only with a non-forced fast-forward after checking the remote head.