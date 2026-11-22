 # Worked Example

Shows the full flow: rough notes → asking for missing information → draft → approval.

## 1. User input

> Coupon bug on checkout. I added SAVE10, total went down, then I removed the coupon and the total stayed discounted. Chrome on my Mac, staging.

## 2. Check required information

| Required item | Provided? |
|---------------|-----------|
| What goes wrong | ✅ Total stays discounted after the coupon is removed |
| Bug type | ❌ Missing |
| Steps to reproduce | ⚠️ Partly — cart contents and starting state unknown |
| Expected result | ⚠️ Implied, needs confirming |
| Actual result | ⚠️ Exact totals unknown |
| Environment | ⚠️ Partly — OS version, Chrome version, URL and user role missing |

Items are missing, so Claude does **not** write the report yet. It asks:

> Before I write the bug report I need a few more details:
> 1. **Bug type** — FE, BE or UI? (FE if the API returns the correct total but the page shows the old one; BE if the API itself returns the discounted total.)
> 2. **Steps** — what was in the cart and its price? Were you logged in?
> 3. **Totals** — the total before the coupon, with the coupon, and after removing it.
> 4. **Expected result** — should the total return to the original amount?
> 5. **Environment** — macOS version, Chrome version, checkout URL and user role.

## 3. User answers

> FE — the /cart API returns 50.00 after removing, but the page shows 45.00. Logged in as a regular customer, 1 × "Blue T-shirt" at 50.00. Total 50.00 → 45.00 with SAVE10 → still 45.00 after removing. Yes, it should go back to 50.00. macOS 14.5, Chrome 131, https://staging.shop.example/checkout. No console errors. Screenshot: checkout-total.png.

All required information is now known.

## 4. Draft shown to the user

**Summary:** `[FE] Checkout: total not updated when coupon is removed`
**Severity:** Major

```
h3. Environment
* *OS:* macOS 14.5
* *Browser / App:* Chrome 131
* *Device:* Desktop
* *Environment:* staging
* *URL:* https://staging.shop.example/checkout
* *User role:* Regular customer

h3. Preconditions
* User is logged in as a regular customer
* Cart contains 1 × "Blue T-shirt" (50.00)

h3. Steps to Reproduce
# Open https://staging.shop.example/checkout
# Enter {{SAVE10}} in the Coupon field and click *Apply*
# Check that the total shows 45.00
# Click *Remove* next to the applied coupon

h3. Expected Result
The total returns to 50.00. _(Source: common sense — the discount no longer applies)_

h3. Actual Result
The coupon disappears from the page but the total still shows 45.00.
The {{/cart}} API response after removing the coupon contains the correct total:
{code}
"total": 50.00
{code}

h3. Severity
Major — the customer sees a wrong order total at checkout.

h3. Attachments
* checkout-total.png
```

> Do you approve creating this bug?

## 5. Approval

- User: "change severity to Minor" → Claude updates the draft, shows it again and asks for approval again. **Not approval.**
- User: "looks good" → ambiguous. Claude asks: "Should I create it?" **Not approval.**
- User: "yes, create it" → **Approval.** Only now is the bug created in Jira.

## Why this example is good

- Claude stopped and asked for missing items instead of guessing.
- The bug type came from the user and is supported by a fact (API returns 50.00, page shows 45.00).
- Steps start from a clear state and use concrete data.
- Expected and actual compare the same thing — the total — with exact values.
- No root-cause guesses: the report states what the API returned and what the page showed, nothing more.
- The bug was created only after an explicit "yes".
