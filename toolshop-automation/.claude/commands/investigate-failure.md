---
description: Diagnose a failing or flaky Playwright spec — classify it as product bug, test bug, race, data drift or environment, then fix the cause, not the symptom.
argument-hint: <spec path | TC id | pasted error>
allowed-tools: Read, Glob, Grep, Bash, Skill, mcp__plugin_playwright_playwright__browser_navigate, mcp__plugin_playwright_playwright__browser_snapshot, mcp__plugin_playwright_playwright__browser_take_screenshot
---

Investigate the failure: **$ARGUMENTS**

Load the `analyze-failure` skill and follow it.

Latest artifacts:

!`ls -t test-results 2>/dev/null | head -5`

1. **Read the error and `error-context.md` verbatim before forming a theory.**
2. **Classify before fixing.** The table in the skill maps symptoms to causes.
3. **Look upstream.** A `waitForResponse` timeout usually means the action never fired, or the method is wrong (`QUERY`, not `GET`).
4. **Check the state questions:** alone vs. in parallel, once vs. `--repeat-each=5`.

Hard constraints: don't raise `retries`, don't add `waitForTimeout` or `force: true`, and don't loosen an assertion. If it's a product bug, say so, mark the test `test.fixme` with the issue URL above it, and stop.

Report the category, the evidence, and the fix, separating what you verified by running from what you inferred.
