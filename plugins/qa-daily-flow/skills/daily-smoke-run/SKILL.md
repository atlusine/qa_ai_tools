---
name: daily-smoke-run
description: Run a manual smoke test suite in the browser, record Pass / Fail / Blocked with a screenshot for every case, and deliver the results as an HTML report with a short summary and the report link in the chat. Use for the daily smoke check, "run the smoke tests", "is search still working?", or when building a smoke suite from a larger set of manual test cases.
---

# Daily Smoke Run

Execute a suite of **manual** smoke test cases exactly as written, the way a tester would, and report the result. This skill runs existing test cases; it does not write automation code.

## Inputs

- **The suite.** A Markdown file under `smoke-tests/` (for example `smoke-tests/SCRUM-9-product-search-smoke.md`). The repo file is the source of truth; don't read the suite from Jira.
- **Where to deliver.** Publish the HTML report as an artifact and post the summary with the report link in the chat. Use another channel (Slack, email) only when the user asks for it.

## Process

1. **Load the suite.** Read every case: ID, title, preconditions, steps, test data, expected result. Don't skip, merge or reorder cases.
2. **Check the environment.** Open the app URL from the suite. If it doesn't load (blank page, error, timeout after a retry), mark every case **Blocked**, take a screenshot of what you see, and go to step 6.
3. **Run each case in a fresh state.** Reload the home page and wait until the product grid has loaded before every case. Follow the steps literally with the given test data. Use the Playwright MCP browser tools when they're available; otherwise drive the browser with a short Playwright script (see *Running without Playwright MCP*).
4. **Capture evidence.** For every case, take one screenshot of the screen that shows the expected result (scroll it into view first). Name it `<ID>-<pass|fail|blocked>.png`. For a failure, also note the console errors and any failed API call.
5. **Decide the verdict** using the rules below, and write one sentence of **actual result** in the same words as the expected result.
6. **Build the report** with the layout in `references/report-template.md`, embedding the screenshots.
7. **Deliver.** Publish the report and post the chat summary (`references/report-template.md`, *Chat summary*). Put failures first.
8. **Follow up on failures.** List each failure as **Possible bug** and suggest filing it with the `bug-report` skill. Don't search or change Jira during a smoke run, and never create issues without a person confirming.

## Verdict rules

| Verdict | When |
|---------|------|
| **Pass** | Every part of the expected result is seen on screen. |
| **Fail** | The step could be done, but what is on screen differs from the expected result. Quote the difference. |
| **Blocked** | A step couldn't be done (site down, element missing, error page), so the expected result couldn't be checked. |

- Check properties, not inventory: "every name contains *pliers*" passes whatever the number of products.
- Retry a failing case **once** from a fresh page. If it passes the second time, mark it **Pass** and add "flaky: failed on first try" to the notes.
- Never mark a case Pass without a screenshot that shows the expected result.

## Running without Playwright MCP

In a cloud or CI session the Playwright MCP tools may be missing. Then:

```bash
mkdir -p /tmp/smoke && cd /tmp/smoke
npm init -y >/dev/null && npm install playwright@1 >/dev/null
npx playwright install --with-deps chromium
```

Write one script that runs the cases in order (a fresh `page` per case, `page.goto(url, { waitUntil: "domcontentloaded" })`, then wait for `[data-test="product-name"]`), saves a screenshot per case, and prints a JSON line per case with `id`, `verdict` and `actual`. Useful selectors on the Toolshop app: `[data-test="search-query"]`, `search-submit`, `search-reset`, `search-caption`, `no-results`, `product-name`.

## Building a smoke suite

When asked to make a smoke suite from a full set of manual test cases (for example from the `manual-test-cases` skill):

- Take **High** priority cases on the core path only, guest user, no shared-account changes.
- Cover every acceptance criterion at least once; drop edge cases and known bugs.
- Keep it under 10 cases and about 5 minutes to run by hand.
- Give the cases `SMOKE-<NNN>` IDs, keep a **Source** column with the original test case ID, and save the suite to `smoke-tests/<JIRA-KEY>-<feature>-smoke.md` using the same table layout.

## Review checklist

- [ ] Every case in the suite has a verdict, an actual result and a screenshot
- [ ] Failures quote the difference between expected and actual
- [ ] Blocked is used only when a step couldn't be done, never for a wrong result
- [ ] The report states the date and time (Asia/Yerevan), the app URL and the browser
- [ ] Each failure is listed as a possible bug with the `bug-report` skill suggested
- [ ] The chat summary ends with the report link
