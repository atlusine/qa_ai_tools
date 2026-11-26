# module_object/: page layer

One class per page or persistent region. Constructor takes `page`, stores `this.page`, and nothing else.

| Class          | Owns                                                   |
| -------------- | ------------------------------------------------------ |
| `Header`       | Nav bar: sign-in link, user menu, cart icon and badge  |
| `CatalogPage`  | Home/catalog: search, sort, category filter, cards     |
| `ProductPage`  | Product details: quantity, add to cart, unit price     |
| `CartPage`     | `/checkout` step 1: rows, quantity, remove, total      |
| `LoginPage`    | `/auth/login` and landing on `/account`                |
| `RegisterPage` | `/auth/register` validation                            |

## Method contract

- **Actions** (`open_`, `click_`, `type_`, `select_`, `search_`, `filter_`, `add_`, `update_`, `remove_`, `submit_`) capture the API call they trigger **before** acting, then wait on it with `wait_api_call_and_assert_success_status`.
- **Getters** (`get_`) return plain data (`{ name, price }`, a number), never a locator to a spec.
- **Assertions** (`assert_`) use web-first assertions through `PlaywrightMethods`, or `expect.poll` for computed checks.
- Reusable constants are class fields (`sortValues`, `requiredFieldErrors`).
- **Search before adding.** Open the class and `support/PlaywrightMethods.js`; the method you need may already exist under a different verb.

A journey that spans pages (catalog → product → cart) goes in `flows/`, composed from these classes, not copied into a spec.
