# Rule — Testing standards

Always in context. Depth lives in the `automation-conventions` skill; load it before writing a spec.

## Spec shape — load-bearing, not stylistic

```js
import { test } from "@playwright/test";
import { CatalogPage } from "../../module_object/CatalogPage";

test.describe("Catalog browsing", { tag: "@regression" }, () => {
  let category;

  test.beforeAll("Test data preparation", () => {
    category = "Hammer";
  });

  test("TC05 Filter by a category and verify only that category is listed", async ({ page }) => {
    const catalogPage = new CatalogPage(page);

    await catalogPage.open_catalog();
    await catalogPage.filter_products_by_category(category);
    await catalogPage.assert_every_product_name_contains(category);
  });
});
```

- One `test.describe` per file, tagged **`@smoke`** (in `tests/smoke/`) or **`@regression`** (in `tests/regression/`).
- Every `test` is **independent**: it gets a fresh browser context, opens its own page through an `open_*` method, and never relies on another test having run first. `fullyParallel: true` will run them in any order.
- Test data goes in `beforeAll("Test data preparation")` as `let` variables, or in `support/users.js` for accounts.
- Titles: `TC<nn> <action> and verify <outcome>`, written as plain language. **85 characters at most**: the list reporter and the HTML report truncate titles, and the cut-off words are the ones that say what the test proves.

## Hard rules

| Rule                                                                  | Why it bites                                                                                       |
| --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| No `page.waitForTimeout(<ms>)`                                        | Too short on a slow run and wasted time on a fast one. Wait on a response or a web-first assertion |
| No `.only`; `forbidOnly: true` in config                              | It silently drops every other test from the run                                                    |
| `retries` is 1 (config). **Max 3** anywhere                           | A high retry count hides a race instead of fixing it                                               |
| No `page.goto` in a spec; use an `open_*` method                      | The app's `load` event never fires (third-party widget). `open_url` uses `domcontentloaded`        |
| No assertions (`expect`) in specs                                     | They belong in `assert_*` methods on the module object (`rules/assertions.md`)                     |
| No hardcoded selectors, credentials, or expected UI strings in specs  | `support/selectors.js`, `support/users.js`, `support/messages.js`                                  |
| Methods `snake_case`, variables, args and fields `camelCase`          | Matches the existing code. Every method starts with a verb                                         |
| No comments in committed code, except the issue URL above a skip      | The method name is the documentation                                                               |
| Never log in with wrong passwords against the shared demo accounts    | The public site locks an account after repeated failures, and that breaks every other student      |

**The one permitted comment** sits directly above a `test.skip` / `test.fixme` and carries the issue URL:

```js
// Cart total ignores discount — https://github.com/testsmith-io/practice-software-testing/issues/123
test.fixme("TC11 Apply a coupon and verify the total is discounted", async ({ page }) => {});
```

## The app is shared and public

`practicesoftwaretesting.com` is used by everyone at the same time and its data is reset periodically. So:

- **Assert invariants, not inventory.** "Every result contains *pliers*" survives a data change; "exactly 4 results" does not.
- **Prefer guest flows.** A guest cart lives in your own browser context; a logged-in cart is shared by everyone who uses that account.
- **Never change shared account data** (profile, password, address) from a test.
