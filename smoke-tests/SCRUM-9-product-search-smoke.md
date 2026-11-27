# Smoke tests: Toolshop product search (SCRUM-9)

Manual smoke suite for product search on https://practicesoftwaretesting.com/. Picked from the 22 test cases in [SCRUM-9](https://atlusine.atlassian.net/browse/SCRUM-9) (epic SCRUM-7): the High-priority cases on the core path, one or more per acceptance criterion. Run it every morning; it takes about 5 minutes.

**Common preconditions (all cases):** Desktop Chrome (latest), guest user (not logged in), home page https://practicesoftwaretesting.com/ opened and the product grid fully loaded, search field empty.

## Test cases

| ID | Title | Priority | Type | Source | Steps | Test Data | Expected Result |
|----|-------|----------|------|--------|-------|-----------|-----------------|
| SMOKE-001 | Verify search controls are displayed when the home page loads | High | Positive | TC-001 | 1. Look at the left filter panel | — | The "Search" text field, the "Search" button and the "X" button are visible |
| SMOKE-002 | Verify only matching products are shown when searching "pliers" | High | Positive | TC-002 | 1. Enter `pliers` in the Search field<br>2. Click "Search" | `pliers` | At least one product card is shown, and every product name contains "pliers" (any letter case) |
| SMOKE-003 | Verify the search caption is shown when a search is performed | High | Positive | TC-003 | 1. Enter `pliers` in the Search field<br>2. Click "Search" | `pliers` | The caption "Searched for: pliers" is shown above the results |
| SMOKE-004 | Verify search is case-insensitive when the term is uppercase | High | Positive | TC-004 | 1. Enter `PLIERS` in the Search field<br>2. Click "Search" | `PLIERS` | The same products as SMOKE-002 are shown |
| SMOKE-005 | Verify search matches partially when the term is part of a word | High | Positive | TC-005 | 1. Enter `plier` in the Search field<br>2. Click "Search" | `plier` | The same products as SMOKE-002 are shown |
| SMOKE-006 | Verify the no-results message is shown when no product matches | High | Negative | TC-010, TC-011 | 1. Enter `xyzxyz` in the Search field<br>2. Click "Search" | `xyzxyz` | The message "There are no products found." is shown and the product grid has 0 cards |
| SMOKE-007 | Verify the full product list is restored when "X" is clicked after a search | High | Positive | TC-007 | 1. Enter `pliers` and click "Search"<br>2. Click "X" | `pliers` | The Search field is empty, the caption is gone, and the full product list (same as on first load) is shown |

## Traceability matrix

"Test Designed" ✅ means a smoke case is written for the requirement. It does not mean the case has been run.

| Requirement | Description | Smoke cases | Test Designed |
|-------------|-------------|-------------|---------------|
| FR-01 | Search controls in the left filter panel | SMOKE-001 | ✅ |
| AC-01 | Searching shows only matching products | SMOKE-002 | ✅ |
| AC-02 | Matching is case-insensitive and partial | SMOKE-004, SMOKE-005 | ✅ |
| AC-03 | "Searched for: <text>" caption | SMOKE-003 | ✅ |
| AC-04 | No-results message | SMOKE-006 | ✅ |
| AC-05 | "X" resets the search | SMOKE-007 | ✅ |

## Notes

- **Assert properties, not counts.** The demo data is shared and reset from time to time, so SMOKE-002 checks that every result matches rather than expecting exactly 4 products.
- **Guest only.** The smoke run never logs in, so it can't lock or change the shared demo accounts.
- **Known bugs on edge cases** (not in the smoke suite): [SCRUM-10](https://atlusine.atlassian.net/browse/SCRUM-10) (terms shorter than 3 characters are ignored) and [SCRUM-40](https://atlusine.atlassian.net/browse/SCRUM-40) (whitespace-only search).

## Summary

| Type | High | Total |
|------|------|-------|
| Positive | 6 | 6 |
| Negative | 1 | 1 |
| **Total** | **7** | **7** |
