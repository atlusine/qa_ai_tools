# Rule — The app under test

This repo contains **tests only**. The product is the Toolshop demo app: an Angular front end at `https://practicesoftwaretesting.com` and a Laravel REST API at `https://api.practicesoftwaretesting.com`. The source is public at `github.com/testsmith-io/practice-software-testing`.

## Grounding: confirm before you assert

Before writing a selector, route, or expected string, **see it in the running app**. Use the Playwright MCP browser (`browser_navigate` → `browser_snapshot`), `npx playwright codegen`, or the API docs at `https://api.practicesoftwaretesting.com/api/documentation`.

If you can't reach the app, say so and stop. Don't fill the gap from memory, and don't invent a `data-test` value, a route, or a message.

## Facts that cost time to rediscover

| Fact                                                                                 | Consequence                                                                     |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| The `load` event never fires reliably (a third-party widget keeps loading)            | Always navigate with `PlaywrightMethods.open_url` (`waitUntil: "domcontentloaded"`) |
| The product list is fetched with the HTTP method **`QUERY`**, not GET (`/products`, `/products/search`) | `capture_api_call(page, "QUERY", "/products")`                                  |
| Cart calls: `POST /carts`, `POST /carts/{id}`, `PUT /carts/{id}/product/quantity`, `DELETE /carts/{id}/product/{productId}` | Wait on these, not on the toast                                                 |
| Login is `POST /users/login`                                                         | `LoginPage.submit_credentials` captures it                                      |
| Category checkboxes have generated ULID test ids                                     | Located by role + label (`SELECTORS.categoryCheckbox`)                          |
| The cart's remove button has no `data-test`                                          | The single `by_css_without_test_id` selector                                    |
| Demo accounts: `customer@`, `customer2@`, `admin@practicesoftwaretesting.com`, password `welcome01` | Shared by everyone. Read-only use; never test lockout with them           |
| Logged-in contact form hides name/email fields                                       | Contact tests behave differently for guest vs. customer                         |

## Finding a bug

If a test fails because the app is wrong, that's a finding. **Never weaken the test to make it pass.** Report it with the `qa-bug-investigation` plugin's `bug-report` skill and mark the test `test.fixme` with the issue URL above it.
