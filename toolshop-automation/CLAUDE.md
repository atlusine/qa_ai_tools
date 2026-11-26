# toolshop-automation

Playwright end-to-end tests for **[practicesoftwaretesting.com](https://practicesoftwaretesting.com/)** (the Toolshop demo app). JavaScript, `@playwright/test`, page-object architecture. This folder holds **tests only** and always runs against a deployed app: the public site by default, or a local Docker copy through `BASE_URL`.

> Claude Code loads this file, `.claude/settings.json` (hooks and permissions), rules, skills, commands, and agents **only when it's started inside `toolshop-automation/`**. Run `cd toolshop-automation && claude`.

---

## Always-loaded rules

@.claude/rules/testing-standards.md
@.claude/rules/selectors.md
@.claude/rules/assertions.md
@.claude/rules/app-under-test.md

---

## Load a skill before you write

The rules above are the hard edges. The depth lives in skills, so load the one that matches the task **before** writing code.

| Task                                                    | Load                       |
| ------------------------------------------------------- | -------------------------- |
| **Write a new test** (procedure, end to end)            | `create-test`              |
| **A test is failing or flaky**                          | `analyze-failure`          |
| **About to commit or open a PR**                        | `review-test`              |
| Creating, naming or placing a `.spec.js`                | `automation-conventions`   |
| Adding a method, selector, message or flow              | `automation-architecture`  |
| Naming or formatting anything                           | `automation-code-style`    |
| Waits, clicks, timing, flakiness                        | `automation-stabilization` |

The first three are workflows. The rest are the conventions those workflows apply.

## Slash commands

|                                           |                                                    |
| ----------------------------------------- | -------------------------------------------------- |
| `/generate-test <scenario \| test case>`  | Write the spec, grounded in the live DOM, then run it |
| `/investigate-failure <spec \| error>`    | Classify and diagnose a failure                    |
| `/test-review [path]`                     | Run the full gate over the diff                    |

## Agents

|                    |                                                       |
| ------------------ | ----------------------------------------------------- |
| `test-generator`   | Scenario → implemented, passing spec                  |
| `test-reviewer`    | Diff → ranked findings (read-only)                    |
| `failure-analyzer` | Failure → classification and proposed fix (read-only) |

For test *design* (which cases to write), use the `qa-test-design` plugin's `manual-test-cases` skill from this repo's marketplace first, then implement the result with `test-generator`.

---

## Commands

```bash
npm install && npx playwright install chromium && cp .env.example .env   # once
npx playwright test                                # everything (10 tests, ~10 s)
npx playwright test --grep @smoke                  # smoke suite only
npx playwright test tests/regression/regression_test_guest_cart.spec.js
npx playwright test -g "TC09"                      # one test by id
npx playwright test --retries=0 --repeat-each=3    # flake check before committing a new test
npx playwright test --headed --workers=1           # watch it
npx playwright show-report report                  # HTML report: screenshots, video, trace on failure
npx playwright show-trace test-results/<dir>/trace.zip
bash scripts/claude-hooks/review-diff.sh           # pre-commit gate (also: npm run review)
```

`BASE_URL` / `API_URL` point the suite at another deployment, for example the app's own `docker compose` stack:

```bash
BASE_URL=http://localhost:4200 API_URL=http://localhost:8091 npx playwright test
```

---

## Repo map

```
CLAUDE.md                     This file: routes to rules and skills
.claude/
  ├─ settings.json            Hooks and shared permissions (settings.local.json is yours, gitignored)
  ├─ rules/                   Always-loaded hard rules, @imported above
  ├─ skills/                  3 workflows + 4 convention references
  ├─ commands/                /generate-test  /test-review  /investigate-failure
  └─ agents/                  test-generator · test-reviewer · failure-analyzer
scripts/claude-hooks/         session-context · validate-edit · review-diff
playwright.config.js          baseURL, testIdAttribute=data-test, retries 1, video/trace on failure
tests/smoke/                  @smoke: login, search, add to cart        → own CLAUDE.md
tests/regression/             @regression: catalog, auth, cart
module_object/                Page classes: Header, CatalogPage, ProductPage, CartPage, LoginPage, RegisterPage  → own CLAUDE.md
flows/                        Cross-page journeys (FlowShopping)
support/
  ├─ PlaywrightMethods.js     The only file that talks to Playwright's locator API directly
  ├─ selectors.js             Every selector (SELECTORS)
  ├─ messages.js              Every expected UI string
  ├─ users.js                 Test accounts; password from USER_PASSWORD
  └─ environment.js           BASE_URL / API_URL
```

## Implemented test cases

| ID   | Suite      | Scenario                                                             |
| ---- | ---------- | -------------------------------------------------------------------- |
| TC01 | smoke      | Customer logs in and lands on *My account* with their name in the nav |
| TC02 | smoke      | Search "pliers": caption shown, every result matches                 |
| TC03 | smoke      | Add a product with quantity 2: toast, badge 2, cart row quantity 2   |
| TC04 | regression | Sort by price low→high: prices ascending                             |
| TC05 | regression | Filter by *Hammer*: every result is a hammer                         |
| TC06 | regression | Product page name and price match the catalog card                   |
| TC07 | regression | Unknown account login shows "Invalid email or password"              |
| TC08 | regression | Empty registration form shows required-field errors                  |
| TC09 | regression | Cart quantity change recomputes line price and total                 |
| TC10 | regression | Removing the only product empties the cart                           |

---

## Gotchas that cost real time

**`page.goto(url)` hangs for 30 s and times out.** The `load` event waits on a third-party widget. Always use `PlaywrightMethods.open_url`, which waits for `domcontentloaded`.

**A one-shot read after an action returns the old value.** `get_element_price` right after a quantity change read `$14.15` instead of `$42.45`. Use `assert_element_has_text` or `expect.poll`.

**`getByTestId("product-name")` matches 9 elements.** On the catalog, card-level test ids repeat. Asserting on the whole list throws a strict-mode violation; use `.first()`, or scope to a card or row.

**Locking a shared account breaks the class.** Negative login tests use `users.unregistered_user`, never a real demo account.

**The data is shared and reset.** Assert properties ("every result contains…", "sorted ascending"), not exact counts or specific product lists.
