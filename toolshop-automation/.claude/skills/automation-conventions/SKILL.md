---
name: automation-conventions
description: Spec-level conventions for toolshop-automation Playwright tests — file naming and placement (smoke vs regression), describe/test structure, tags, TC ids, title length, test data in beforeAll, independence and parallel safety, skip/fixme rules. Load when creating, moving, renaming or reviewing a .spec.js file.
---

# Spec conventions

## 1. Placement and naming

- `tests/smoke/smoke_test_<actor>_<feature>.spec.js`, tagged `@smoke`
- `tests/regression/regression_test_<actor>_<feature>.spec.js`, tagged `@regression`
- `<actor>`: `guest` | `customer` | `admin`. `<feature>`: snake_case noun (`cart`, `catalog`, `authentication`).
- Related tests share a file and a `describe`. Don't create one file per test unless the feature has only one.

## 2. Structure

```js
test.describe("<Feature in plain words>", { tag: "@regression" }, () => {
  let updatedQuantity;

  test.beforeAll("Test data preparation", () => {
    updatedQuantity = 3;
  });

  test("TC09 Change a cart quantity and verify the line price and total update", async ({ page }) => {
    const flowShopping = new FlowShopping(page);
    const cartPage = new CartPage(page);

    const product = await flowShopping.add_first_catalog_product_to_cart();
    await cartPage.update_product_quantity(product.name, updatedQuantity);
    await cartPage.assert_line_price_and_total(product.name, product.price, updatedQuantity);
  });
});
```

- Page objects are created inside each test from that test's `page`. Never share them across tests.
- Order inside a test: arrange (open or flow) → act → assert. Assertions come last and only through `assert_*`.
- No `beforeEach` login shared across tests unless every test in the describe needs exactly that state. Prefer the explicit call in each test.
- No `afterEach` / `afterAll` cleanup: each test gets a fresh browser context, so a guest cart vanishes automatically. If a test needs cleanup, it's probably mutating shared data, which the rules forbid.

## 3. Titles

`TC<nn> <Action> and verify <outcome>`, at most 85 characters. Drop words the `describe` already says. IDs are never reused, even when a test is deleted.

## 4. Retries, skip, only

- `retries: 1` comes from the config. Per-describe `test.describe.configure({ retries: n })` is allowed up to 3, and only with a justification in the PR description.
- `.only` is never committed. `forbidOnly` fails the run anyway.
- `test.skip` / `test.fixme` must have the issue URL in a comment directly above it. Use `fixme` for a known product bug and `skip` for an environment limitation.

## 5. Parallel safety

`fullyParallel: true` with 4 workers. A test is parallel-safe when it creates everything it uses inside its own browser context. Guest flows are; flows that log in to the same demo account and change its cart, favorites or profile are not. If you truly need one, put it in its own file with `test.describe.configure({ mode: "serial" })` and say why in the PR.
