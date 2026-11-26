---
description: Write a new Playwright spec for a practicesoftwaretesting.com scenario or manual test case — grounded in the live DOM, run until green, gated.
argument-hint: <scenario description | manual test case | path to a test-case file>
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Skill, mcp__plugin_playwright_playwright__browser_navigate, mcp__plugin_playwright_playwright__browser_snapshot, mcp__plugin_playwright_playwright__browser_click, mcp__plugin_playwright_playwright__browser_type, mcp__plugin_playwright_playwright__browser_select_option, mcp__plugin_playwright_playwright__browser_network_requests, mcp__plugin_playwright_playwright__browser_take_screenshot
---

Write the Playwright coverage for: **$ARGUMENTS**

Load the `create-test` skill and follow it end to end. Don't skip a step because it looks obvious.

Current state:

- Branch: !`git rev-parse --abbrev-ref HEAD`
- Last test id: !`grep -rhoE 'TC[0-9]+' tests | sort -t C -k2 -n | tail -1`

Non-negotiables:

1. **Ground every selector and string in the live app** (Playwright MCP snapshot or codegen) before writing it. Don't invent a `data-test` value, route, or message.
2. **Search before writing.** Read the relevant module object and `support/PlaywrightMethods.js` first.
3. **Wait on the API response, captured before the action.** No `waitForTimeout`.
4. **Specs are declarative.** No `expect`, locators, or `page.goto` in `tests/`.
5. **Run it:** `--retries=0 --repeat-each=5`, then the full suite. Then break the assertion once on purpose to see it fail, and revert.

If something is blocked (no `data-test`, app unreachable, behavior that looks like a product bug), finish everything else and state plainly what's blocked. Don't quietly narrow the scope.

Finish with `bash scripts/claude-hooks/review-diff.sh`, and report what you verified by running vs. what you assumed.
