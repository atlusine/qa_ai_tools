---
name: automation-stabilization
description: Keeping toolshop-automation Playwright tests stable — no waitForTimeout, waiting on API responses captured before the action, web-first assertions instead of one-shot reads, expect.poll for computed checks, actionability instead of force, strict-mode scoping, and how to prove a test is not flaky. Load when writing waits or interactions, or when a test is flaky or timing-dependent.
---

# Stabilization: waits, clicks, flakes

A flaky test is worse than a missing one: it trains people to re-run instead of investigate. Almost every flake is an unstated assumption about timing. **Wait on something observable, always.**

## 1. No fixed waits [RULE]

`page.waitForTimeout(ms)` is banned and both hooks block it. It's too short on a slow run and wastes time on every fast one.

## 2. Wait on the right signal [RULE]

In order of preference:

1. **The API response that changes state**, captured **before** the action:
   ```js
   const productsCall = PlaywrightMethods.capture_api_call(this.page, "QUERY", "/products");
   await PlaywrightMethods.select_option_by_value(this.page, SELECTORS.sortSelect, "price,asc");
   await PlaywrightMethods.wait_api_call_and_assert_success_status(productsCall);
   ```
2. **A web-first assertion** on the resulting UI (`toHaveText`, `toBeVisible`, `toHaveValue`, `toHaveURL`). These retry up to `expect.timeout` (15 s).
3. **`expect.poll`** when the check is computed over several elements (sorted, every item matches):
   ```js
   await expect.poll(async () => {
     const prices = await PlaywrightMethods.get_all_element_prices(this.page, SELECTORS.productCardPrice);
     return prices.every((p, i) => i === 0 || prices[i - 1] <= p);
   }).toBe(true);
   ```

The response arriving doesn't mean Angular has rendered it. That's why step 1 is always followed by step 2 or 3.

## 3. Never compare a one-shot read [RULE]

`expect(await el.innerText()).toBe(x)` reads once. In this repo it read the cart total as `$14.15` while the correct `$42.45` was rendering. Use `assert_element_has_text`.

## 4. Click through actionability, not around it

`locator.click()` already waits for the element to be visible, stable, enabled and unobscured. `{ force: true }` skips all of that. On a disabled or covered button it "succeeds" and the test fails later, far from the cause, or passes over a real bug. Before reaching for force:

1. Is the locator pointing at the right element? (`npx playwright test --debug`, or the trace)
2. Is something covering it (toast, cookie banner, chat widget)? Close or wait for it.
3. Is it disabled for a real reason (form invalid)? That's a finding.

If force survives all three, justify it in the PR description.

## 5. Strict mode is your friend

`strict mode violation: resolved to 9 elements` means the locator is ambiguous. Fix it by scoping (`get_element(row, …)`), filtering (`.filter({ hasText })`), or explicitly taking `.first()` when "any one" is really what you mean. Don't fix it by switching to a CSS `nth-child`.

## 6. Proving stability

```bash
npx playwright test <spec> --retries=0 --repeat-each=5
npx playwright test --retries=0                          # under full parallel load
```

A test "fixed" without a repeat run hasn't been shown to be fixed.
