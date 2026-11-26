---
name: automation-architecture
description: Where code goes in toolshop-automation — the spec / flow / module_object / support layering, the PlaywrightMethods wrapper, the SELECTORS registry and resolver, messages.js and users.js, API-response waiting. Load when adding a method, selector, expected string, flow or helper.
---

# Architecture

```
spec (tests/)            what is tested: declarative calls only
  └─ flow (flows/)       multi-page journeys reused by several specs
      └─ module_object/  one class per page: actions, getters, assertions
          └─ support/PlaywrightMethods.js   the only Playwright locator/expect wrapper
              ├─ support/selectors.js       SELECTORS: every locator definition
              ├─ support/messages.js        every expected UI string
              ├─ support/users.js           accounts (+ get_user_password)
              └─ support/environment.js     BASE_URL / API_URL
```

Dependencies point **down only**. A module object never imports a spec; `PlaywrightMethods` never imports a module object.

## 1. PlaywrightMethods

Static methods, `snake_case`, first argument is the scope (`page` or a `Locator`). Add a method here only when it's **page-agnostic** and needed by two or more module objects; otherwise it belongs in the module object. Current building blocks:

| Need                         | Method                                                             |
| ---------------------------- | ------------------------------------------------------------------ |
| Navigate                     | `open_url(page, path)`                                             |
| Locate                       | `get_element(scope, SELECTORS.x, params)`                          |
| Wait on the backend          | `capture_api_call(page, method, endpoint)` → `wait_api_call_and_assert_success_status(call)` |
| Act                          | `click_on_element_when_visible`, `type_text_into_element_when_visible`, `select_option_by_value`, `check_checkbox` |
| Read                         | `get_element_text`, `get_all_element_texts`, `get_element_price`, `get_all_element_prices` |
| Assert                       | `assert_element_visible`, `assert_first_element_visible`, `assert_element_has_text`, `assert_element_contains_text`, `assert_element_has_value`, `assert_text_visible`, `assert_toast_message`, `assert_page_url_includes_text`, `assert_amount_equals` |

## 2. Selectors

```js
const by_test_id = (testId) => ({ kind: "testId", value: testId });
const by_role = (role, name) => ({ kind: "role", role, name });
const by_css_without_test_id = (value) => ({ kind: "css", value });

export const SELECTORS = {
  cartRowLinePrice: by_test_id("line-price"),
  categoryCheckbox: by_role("checkbox", "%CATEGORY%"),
  registerFieldError: by_test_id("%FIELD%-error"),
};
```

- Key: `<area><Element><Type>`, camelCase. Group keys by page with a blank line between groups.
- Parameterize with `%UPPER_SNAKE%` instead of adding near-duplicate keys.
- The same `data-test` may appear under two keys (`productCardName`, `productDetailsName`) when it means different things on different pages. That's intentional: the key names the meaning.

## 3. Module objects

```js
export class CartPage {
  constructor(page) { this.page = page; }

  get_cart_row(productName) { … }                         // scoping helper, returns a Locator, internal use

  async update_product_quantity(productName, quantity) {   // action: capture → act → wait → confirm
    const updateCall = PlaywrightMethods.capture_api_call(this.page, "PUT", "/carts/*/product/quantity");
    …
    await PlaywrightMethods.wait_api_call_and_assert_success_status(updateCall);
  }

  async assert_cart_is_empty(removedProductName) { … }     // assertion: anchored, web-first
}
```

## 4. API endpoints

`capture_api_call` takes a path relative to `API_URL`, with globs: `*` matches one segment and `**` matches any depth. The query string is ignored. Look the method up in the network panel; `/products` is `QUERY`.

## 5. Test data

- Accounts: `support/users.js`, snake_case keys named for the purpose (`customer_login`, `unregistered_user`). Password only via `get_user_password()`.
- Per-test values (search terms, quantities): `beforeAll` in the spec.
- Values read from the app at runtime (first product's name and price) beat hardcoded product names, because they survive data resets.
