# Toolshop product search (SCRUM-7): test cases, automation, run reports

Homework by Narek, lesson 2. App: https://practicesoftwaretesting.com/ (Toolshop).
Jira: epic **SCRUM-7**. Test cases are in **SCRUM-48** (requirements) and **SCRUM-49** (extended). Bugs are **SCRUM-41 … SCRUM-47**.

## What's here

| Path | What |
|---|---|
| `test-cases/01-test-cases-requirements.md` | 17 cases (SRCH-001…017) covering US-01, FR-01…06, AC-01…05, mapped to SCRUM-9, with a traceability matrix |
| `test-cases/03-test-cases-extended.md` | 41 "every human action" / self-monitoring cases (EX-01…39): submit methods, length limits, spaces, real name shapes, special characters and security, combined actions, mobile, mocked server/network errors, catalogue sweep |
| `run-reports/02-run-report-requirements.md` | Run of the requirement cases: 12 pass, 4 fail, 1 manual |
| `run-reports/04-run-report-extended.md` | Full run (58 cases × 2): 39 pass, 18 fail (none flaky), 1 manual, plus the likely root cause |
| `playwright/` | Playwright project: `tests/search-requirements.spec.ts`, `tests/search-extended.spec.ts`, shared `tests/search-helpers.ts`, and `summarize.py` |

## How to run

```bash
cd homework/narek-toolshop-search/playwright
npm ci
npx playwright install chromium
npx playwright test                       # all search tests (18 failures are expected: they are the bugs)
npx playwright test --repeat-each=2       # run twice to catch flaky results
```

Short PASS/FAIL/FLAKY summary:

```bash
PLAYWRIGHT_JSON_OUTPUT_NAME=r.json npx playwright test --reporter=json; python3 summarize.py r.json
```

## How the tests decide pass/fail
- **Oracle:** the live catalogue from `GET https://api.practicesoftwaretesting.com/products` (all pages), filtered by the FR-02/FR-03 rule "name contains the text, case-insensitive". The AC cases also check the fixed AC data (the 4 pliers).
- Toolshop marks elements with `data-test`, so the config sets `testIdAttribute: 'data-test'`.
- Server and network errors (EX-36/37) are **mocked** with `page.route`.
- SRCH-013 (logged-in search) is `test.fixme`: it needs a real login, and passwords are not typed by the automation.
