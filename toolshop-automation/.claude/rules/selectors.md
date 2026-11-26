# Rule — Selectors

Always in context. Depth lives in `automation-architecture` §2.

## One source, one resolver

**Every selector is registered in `support/selectors.js` and resolved through `PlaywrightMethods.get_element(scope, SELECTORS.<key>, params)`.**

```js
await PlaywrightMethods.click_on_element_when_visible(this.page, SELECTORS.productDetailsAddToCartButton);
await PlaywrightMethods.check_checkbox(this.page, SELECTORS.categoryCheckbox, { CATEGORY: "Hammer" });
await PlaywrightMethods.assert_element_has_text(row, SELECTORS.cartRowLinePrice, "$42.45");
```

- `scope` is the `page` or a `Locator`. Scoping to a row or card is how you target one item in a list.
- `%KEY%` placeholders are filled from `params`. A missing param throws immediately instead of matching nothing.
- `playwright.config.js` sets `testIdAttribute: "data-test"`, so `by_test_id("add-to-cart")` resolves `[data-test="add-to-cart"]`.

## Preference order — use the first one that exists

1. `by_test_id("…")`: the app ships a `data-test` attribute on nearly every control. **This is the default.**
2. `by_role(role, name)`: for accessible controls whose test id is generated (category checkboxes have ULID test ids, so they're located by their label).
3. `by_css_without_test_id("…")`: **last resort**, only when the app renders neither a test id nor an accessible name. The name is deliberately ugly so it stands out in review. Today there is exactly one: `cartRowRemoveButton` (`a.btn-danger`).

## Banned outside `support/selectors.js` and `support/PlaywrightMethods.js`

| Banned                                                       | Instead                                         |
| ------------------------------------------------------------ | ----------------------------------------------- |
| `page.locator(".class")`, `page.locator("#id")`, XPath       | `SELECTORS.<key>`                               |
| `page.getByTestId("…")`, `page.getByRole(…)`, `getByText(…)` | Register it, then use `PlaywrightMethods`       |
| `nth-child`, text-match XPath, `>> nth=3` positional chains  | Scope to a parent (`row`, `card`) and filter    |
| Inventing a `data-test` value you have not seen in the DOM   | See below                                       |

## Finding a selector — never guess

Look at the live DOM before adding a key:

- Playwright MCP: `browser_navigate` to the page, then `browser_snapshot` and read the `data-test` attributes, or
- `npx playwright codegen https://practicesoftwaretesting.com/<route>`, or
- DevTools: `document.querySelectorAll('[data-test]')`.

If the element really has no `data-test`, say so in your summary and use the next option in the order above. Never invent one.
