# Smoke Run Report Templates

## HTML report (published as an artifact)

One self-contained page. Embed screenshots as base64 `data:` URIs so the page works without the files.

**Title:** `Smoke Run <YYYY-MM-DD>`

Sections, in order:

1. **Header:** suite name and source (file path or Jira key), run date and time (Asia/Yerevan), app URL, browser.
2. **Summary bar:** counts of Pass / Fail / Blocked, and an overall status:
   - 🟢 **All passed**: every case passed
   - 🔴 **Failures**: at least one Fail
   - 🟠 **Blocked**: no Fail, but at least one Blocked
3. **Results table:** one row per case, in suite order.

   | ID | Title | Verdict | Actual result | Screenshot | Notes / bug |
   |----|-------|---------|---------------|------------|-------------|
   | SMOKE-001 | Verify … | ✅ Pass | The Search field, Search button and X button are visible | thumbnail | — |
   | SMOKE-006 | Verify … | ❌ Fail | "0 products found" text shown instead of "There are no products found." | thumbnail | Possible bug |

   Clicking a thumbnail opens the full screenshot.
4. **Failures and blocked cases:** for each one, the steps, expected, actual, the full screenshot, console errors and failed API calls.

## Chat summary

Keep it short; the report has the detail.

```
Smoke run, <Fri 27 Nov, 09:30> (Yerevan): <🟢 All 7 passed | 🔴 2 of 7 failed | 🟠 7 blocked>
Suite: Product search (SCRUM-9)

❌ SMOKE-006 No-results message: "0 products found" shown instead of "There are no products found."
❌ SMOKE-007 Reset: caption still shown after clicking X

Report: <artifact link>
```

- List only failed and blocked cases, one line each: ID, short name, the difference.
- When everything passes, the message is the first line, the suite line and the report link.
- If the report couldn't be published, say so and include every case's verdict in the summary instead.
