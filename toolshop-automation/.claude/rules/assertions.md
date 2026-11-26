# Rule — Assertions

Always in context. Depth lives in `automation-architecture` §3 and `automation-stabilization`.

## Assertions live in module objects, never in specs

```js
// spec: declarative steps only
await loginPage.login(customer.email, get_user_password());
await loginPage.assert_my_account_page_opened();

// module object: the assertion
async assert_my_account_page_opened() {
  await PlaywrightMethods.assert_page_url_includes_text(this.page, "/account");
  await PlaywrightMethods.assert_element_has_text(this.page, SELECTORS.pageTitle, pageTitles.myAccount);
}
```

## Expected text lives in `support/messages.js`

Group by area, camelCase keys, and use functions for parameterized text:

```js
export const alertMessages = {
  search: { caption: (term) => `Searched for: ${term}` },
};
```

Copy the string from the live app. Don't paraphrase it from a ticket.

## Use web-first assertions; never compare a one-shot read

`await expect(locator).toHaveText(...)` retries until the DOM settles. `expect(await locator.innerText()).toBe(...)` reads once, often **before** Angular re-renders, and fails or (worse) passes on stale data.

This repo has already hit this: the cart total was read once right after a quantity update, got the old value `$14.15`, and failed. The fix was `assert_element_has_text`. When a value has to be computed (sorting, "every item contains"), wrap the read in `expect.poll(...)`.

## `assert_` vs `check_`

- `assert_`: pure assertion, no side effects.
- `check_`: navigates or interacts first, then asserts.

Name the method for the observable outcome: `assert_cart_is_empty`, not `assert_text_present`.

## An absence assertion must not be able to pass vacuously

"The product row is gone" is equally green when the cart page never loaded. **Anchor it**: assert something that must be *present* first, then assert the absence.

```js
async assert_cart_is_empty(removedProductName) {
  await PlaywrightMethods.assert_text_visible(this.page, alertMessages.cart.emptyCart);
  await expect(this.get_cart_row(removedProductName)).toHaveCount(0);
}
```

## Assert the state that actually gates the next step

A toast appearing doesn't mean the server agreed. Wait on the response that changes state, then assert the UI:

```js
const addToCartCall = PlaywrightMethods.capture_api_call(this.page, "POST", "/carts/*");
await PlaywrightMethods.click_on_element_when_visible(this.page, SELECTORS.productDetailsAddToCartButton);
await PlaywrightMethods.wait_api_call_and_assert_success_status(addToCartCall);
await PlaywrightMethods.assert_toast_message(this.page, SELECTORS.toastMessage, alertMessages.cart.productAdded);
```

**Capture before you act.** A `capture_api_call` issued after the click can miss a fast response.
