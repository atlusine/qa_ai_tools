## Test report: Toolshop smoke test

**Tested by:** Suren (run by Claude with Playwright MCP, following the `qa-core` skill) · **Date:** 2026-11-27 · **Testing type:** Smoke

> The `smoke-testing` skill was still empty, so this run applied `qa-core` only.

### Scope
- **In scope:** the main guest and customer flows: home page, search, product page, add to cart, cart, reaching checkout, customer login.
- **Out of scope:** payment and placing an order (it would create real orders on the shared site), registration, admin, the API on its own, the with-bugs version.

### Environment
- **URL:** https://practicesoftwaretesting.com (Toolshop v5.0, clean version from the Lesson 1 slides)
- **Build / version:** v5.0 (from the page title)
- **Browser / device:** Chromium via Playwright MCP, desktop
- **Accounts / roles:** guest, then the demo customer (Jane Doe)

### Results summary

| Passed | Failed | Blocked | Not run | Total |
|--------|--------|---------|---------|-------|
| 7      | 0      | 0       | 0       | 7     |

### Results per case

| ID | Title | Status | Evidence / bug |
|----|-------|--------|----------------|
| SMK-01 | Verify the home page lists products when opened as a guest | Passed | 9 products with name and price (page snapshot) |
| SMK-02 | Verify search returns only matching products when searching "pliers" | Passed | Caption "Searched for: pliers", 4 results, all contain "pliers" · [SMK-02-search-pliers.png](SMK-02-search-pliers.png) |
| SMK-03 | Verify the product page matches the catalog card | Passed | Combination Pliers, $14.15 on both, Quantity 1, Add to cart shown (page snapshot) |
| SMK-04 | Verify a product is added to the cart when quantity is 1 | Passed | Toast "Product added to shopping cart", badge `1` (page snapshot); `POST /carts` → 201, `POST /carts/<id>` → 200 · [SMK-04-added-to-cart.png](SMK-04-added-to-cart.png) shows the product page after the add |
| SMK-05 | Verify the cart shows the added product and the correct total | Passed | 1 row: Combination Pliers ×1, $14.15; total $14.15 · [SMK-05-cart.png](SMK-05-cart.png) |
| SMK-06 | Verify a customer lands on My account after logging in | Passed | Redirected to `/account`, heading "My account", user menu "Jane Doe" · [SMK-06-my-account.png](SMK-06-my-account.png) |
| SMK-07 | Verify "Proceed to checkout" reaches the sign-in step | Passed | Step 2 shows "Sign in" and "Continue as Guest" tabs (page snapshot) |

### Defects found

None.

### Observations (not failures)
1. **A console error appears while the cart loads.** `TypeError: Cannot read properties of null (reading 'cart_items')` was logged 8 times on `/checkout` before the cart rendered. Users don't see it, and the cart was shown correctly. Worth a closer look; it could become a Minor [FE] bug if it's reproducible.
2. **`GET /users/me` → 401** on page load as a guest. Expected for a user who isn't logged in, so not a bug.
3. **Pages render slowly.** The product list and the cart table appear after the page reports it has loaded, so automated tests must wait for content, not for page load.

### Risks and open questions
- Only the clean site was tested. The with-bugs version (`with-bugs.practicesoftwaretesting.com`) is where the course's planted bugs are.
- The checkout wasn't completed, so payment and order confirmation are untested.
- The site is shared, so product data can change between runs.

### Recommendation
**Ready** — all 7 smoke cases pass. The only open item is console observation 1.
