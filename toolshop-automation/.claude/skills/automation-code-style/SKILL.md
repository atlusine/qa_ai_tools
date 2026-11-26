---
name: automation-code-style
description: Naming and formatting conventions for toolshop-automation — snake_case verb-first methods, camelCase variables and selector keys, file and class naming, no comments, imports. Load when naming or formatting anything.
---

# Code style

## 1. Files and classes

| Thing          | Convention                                   | Example                                   |
| -------------- | -------------------------------------------- | ----------------------------------------- |
| Spec           | `<suite>_test_<actor>_<feature>.spec.js`     | `regression_test_guest_cart.spec.js`      |
| Module object  | PascalCase class = file name, `<Name>Page`   | `CartPage.js` → `class CartPage`          |
| Flow           | `Flow<Journey>.js`                           | `FlowShopping.js`                         |
| Support        | camelCase data modules, PascalCase classes   | `selectors.js`, `PlaywrightMethods.js`    |

## 2. Names

- **Methods: `snake_case`, starting with a verb**: `open_`, `click_`, `type_`, `select_`, `check_`, `search_`, `filter_`, `sort_`, `add_`, `update_`, `remove_`, `submit_`, `login`, `get_`, `assert_`, `format_`.
- **Variables, parameters, fields, selector keys, message keys: `camelCase`**: `updatedQuantity`, `cartRowLinePrice`.
- **User keys: `snake_case`**: `customer_login`.
- Name for intent, not mechanics: `add_first_catalog_product_to_cart`, not `click_card_then_button`.

## 3. No comments

Committed code carries no comments. If a line needs explaining, extract a method whose name explains it. The only exception is the issue URL directly above a `test.skip` / `test.fixme`.

## 4. Formatting

- 2-space indent, double quotes, semicolons, trailing commas in multi-line literals.
- Imports: `@playwright/test` first, then `support/`, then `module_object/` and `flows/`. Relative paths only.
- One blank line between "create page objects" and the steps inside a test.
- `async`/`await` everywhere. Never leave a promise floating, except a `capture_api_call` that's awaited later in the same method.
