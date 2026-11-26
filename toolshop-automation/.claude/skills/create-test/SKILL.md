---
name: create-test
description: End-to-end procedure for adding a Playwright test to toolshop-automation — grounding the scenario in the live practicesoftwaretesting.com DOM, registering selectors and messages, choosing the suite, writing module-object methods and then the spec, and proving it passes repeatedly with retries off. Load when asked to write, add, extend or automate a test case, spec or scenario in this folder.
---

# Create a test

The procedure for landing a new `.spec.js`. It sequences the convention skills, so load each one at the step that needs it.

Related: `automation-conventions` (spec shape), `automation-architecture` (where code goes), `automation-code-style` (naming), `automation-stabilization` (waits), `review-test` (the gate before commit).

---

## Step 0: Don't start from a blank file

```bash
grep -rn "<feature keyword>" tests/ module_object/ flows/
grep -n "static async" support/PlaywrightMethods.js
grep -n "<element guess>" support/selectors.js
```

The page class, the flow, or the selector probably exists already. **Read the file before adding to it.**

## Step 1: Pin down the scenario

You need, in writing: preconditions, steps, and **one observable expected result per test**. If the input is a manual test case (from the `manual-test-cases` skill), use its steps verbatim. If it's vague ("test the cart"), propose 1–3 concrete cases and confirm them before writing code.

Drop any case that would mutate shared demo-account data or lock an account (`rules/app-under-test.md`).

## Step 2: Ground every element and string in the live app

Open the page and read the DOM. Don't recall it from memory.

- Playwright MCP: `browser_navigate` → perform the steps → `browser_snapshot` after each one. Note every `data-test` value, the exact visible text of toasts and errors, and the URL.
- Note the **API call** each action triggers (`browser_network_requests`). That's what the module object will wait on. Watch for the HTTP method `QUERY` on product lists.

Nothing seen means nothing asserted. If an element has no `data-test` and no accessible name, say so explicitly.

## Step 3: Register selectors and messages first

- New selectors → `support/selectors.js`, following the preference order in `rules/selectors.md`. Name them `<area><Element><Type>`: `cartRowQuantityInput`, `loginSubmitButton`.
- New expected text → `support/messages.js`, copied character for character from Step 2.
- New accounts → `support/users.js`. Only demo accounts that exist on the site; never a password literal.

## Step 4: Choose the suite

Smoke only if a release truly can't ship when it fails. Otherwise regression. Placement and file naming are in `tests/CLAUDE.md`.

## Step 5: Module-object methods before the spec

Load `automation-architecture`. For each step of the scenario, one verb-prefixed `snake_case` method:

- the action captures its API call **before** acting and waits on it after
- the outcome check is an `assert_*` method that uses web-first assertions
- an absence check is anchored on something present (`rules/assertions.md`)

A multi-page journey reused by more than one test goes in `flows/`.

## Step 6: Write the spec

Load `automation-conventions`. Pick the next `TC<nn>`, keep the title at 85 characters or fewer, and use only module-object calls. The `validate-edit` hook runs on every write. Fix what it reports right away; don't batch the fixes.

## Step 7: Prove it

```bash
npx playwright test -g "TC<nn>" --retries=0                 # passes once
npx playwright test -g "TC<nn>" --retries=0 --repeat-each=5  # passes repeatedly
npx playwright test --retries=0                              # nothing else broke (parallel run)
```

**Then break it on purpose:** change the expected message or value in the module object, confirm the test goes red with a readable error, and revert. A test you haven't seen fail can't be trusted to catch anything.

## Step 8: Gate and report

```bash
bash scripts/claude-hooks/review-diff.sh
```

Add the row to the *Implemented test cases* table in `CLAUDE.md`. In your summary, separate what you **ran** from what you **assumed**, and list anything blocked (no `data-test`, app unreachable, behavior that looks like a product bug).
