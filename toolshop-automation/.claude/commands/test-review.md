---
description: Review the current test diff against every binding rule before commit or PR — blocking issues, advisories, and what the PR description must justify.
argument-hint: [file or spec path — defaults to the whole diff vs main]
allowed-tools: Read, Glob, Grep, Bash, Skill
---

Review the automation change for: **$ARGUMENTS** (empty ⇒ the whole diff vs `main`).

Load the `review-test` skill and work through it.

Diff under review:

!`git diff --stat main -- . 2>/dev/null | tail -20; git ls-files --others --exclude-standard -- . | head -20`

Automated gate:

!`bash scripts/claude-hooks/review-diff.sh 2>&1 | tail -60`

The gate only sees patterns. Also answer: Is each test independent and parallel-safe? Can any assertion pass vacuously? Is every new selector or string present in the live app? Was it run with `--repeat-each=5`?

Report findings most severe first with `file:line`, split into **Blocking** / **Advisory** / **Pre-existing**. Be explicit about what you couldn't verify.
