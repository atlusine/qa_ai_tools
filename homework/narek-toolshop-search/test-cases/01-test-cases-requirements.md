# SCRUM-7 Product Search: requirement-based test cases

- **Source:** SCRUM-7 (US-01, FR-01..FR-06, AC-01..AC-05), read again on 2026-11-25
- **App:** https://practicesoftwaretesting.com/ (Toolshop)
- **Common preconditions:** desktop Chromium, guest user, home page open with the product grid loaded, Search field empty
- **Automated in:** `../playwright/tests/search-requirements.spec.ts` (test titles start with the ID)
- **In Jira:** SCRUM-48 (filed 2026-11-25)
- **SCRUM-9 column:** Lusine's matching case, so both sets can be compared

## Feature summary
- Guests and logged-in customers search products by name from the left filter panel.
- Matching is **partial** and **case-insensitive**. Results replace the grid, with the caption "Searched for: <text>".
- No match shows "There are no products found." **X** clears the field and shows the full list again.
- Out of scope (SCRUM-7): category, brand and price filters, sorting, pagination.

## Positive

| ID | Title | Pri | Req | SCRUM-9 | Steps | Test data | Expected result |
|---|---|---|---|---|---|---|---|
| SRCH-001 | Verify Search input, Search button and X button are shown when the home page loads | High | FR-01 | TC-001 | 1. Open home page | — | All 3 controls are visible and enabled |
| SRCH-002 | Verify exactly the 4 pliers are shown when searching "pliers" | High | AC-01, FR-02 | TC-002 | 1. Type text 2. Click Search | `pliers` | Exactly: Combination Pliers, Pliers, Long Nose Pliers, Slip Joint Pliers |
| SRCH-003 | Verify caption is shown when searching "pliers" | High | AC-03, FR-04 | TC-003 | 1. Type 2. Click Search | `pliers` | Caption "Searched for: pliers" above the results |
| SRCH-004 | Verify same 4 pliers when the term is uppercase | High | AC-02, FR-03 | TC-004 | 1. Type 2. Click Search | `PLIERS` | Same 4 products as SRCH-002 |
| SRCH-005 | Verify same 4 pliers when the term is a partial word | High | AC-02, FR-03 | TC-005 | 1. Type 2. Click Search | `plier` | Same 4 products as SRCH-002 |
| SRCH-006 | Verify same 4 pliers when the term is mixed case | Medium | FR-03 | TC-006 | 1. Type 2. Click Search | `pLiErS` | Same 4 products as SRCH-002 |
| SRCH-007 | Verify products are found when the term is in the middle of a word | High | FR-02, FR-03 | — | 1. Type 2. Click Search | `lier` | Same 4 products ("contains the entered text") |
| SRCH-008 | Verify results match the catalogue when searching "hammer" | High | FR-02 | TC-009 | 1. Type 2. Click Search | `hammer` | Exactly the catalogue products whose name contains "hammer" (7), nothing missing, nothing extra |
| SRCH-009 | Verify products are found when the term is the start of a word | Medium | FR-03 | — | 1. Type 2. Click Search | `ham` | Same products as SRCH-008 |
| SRCH-010 | Verify the second search replaces the first results | Medium | FR-02, FR-04 | TC-009 | 1. Search `pliers` 2. Replace text with `hammer` 3. Click Search | `pliers`, `hammer` | Only hammer products; caption "Searched for: hammer" |
| SRCH-011 | Verify caption shows the text exactly as typed | Low | FR-04 | TC-022 | 1. Type 2. Click Search | `PLIERS` | Caption "Searched for: PLIERS" |
| SRCH-012 | Verify X restores the full list after a search | High | AC-05, FR-06 | TC-007 | 1. Search `pliers` 2. Click X | — | Field empty, caption gone, same product grid as on first load |
| SRCH-013 | Verify search works for a logged-in customer | Medium | US-01 | TC-008 | 1. Sign in 2. Search `pliers` | `pliers` | Same 4 products. **Not automated:** needs a password typed by Narek |

## Negative

| ID | Title | Pri | Req | SCRUM-9 | Steps | Test data | Expected result |
|---|---|---|---|---|---|---|---|
| SRCH-014 | Verify no-results message when nothing matches | High | AC-04, FR-05 | TC-010 | 1. Type 2. Click Search | `xyzxyz` | "There are no products found." |
| SRCH-015 | Verify no product cards are shown when nothing matches | High | AC-04 | TC-011 | 1. Type 2. Click Search | `xyzxyz` | 0 product cards |
| SRCH-016 | Verify X restores the full list after a no-results search | Medium | FR-06 | TC-012 | 1. Search `xyzxyz` 2. Click X | — | Field empty, message gone, full grid shown |
| SRCH-017 | Verify no-results when a valid word has an extra character | Medium | FR-05 | — | 1. Type 2. Click Search | `pliers!` | "There are no products found.", 0 cards |

## Traceability matrix

| Requirement | Test cases | Covered |
|---|---|---|
| US-01 guest / logged in | SRCH-002 (guest), SRCH-013 (logged in, manual) | ✅ / ⚠️ manual |
| FR-01 | SRCH-001 | ✅ |
| FR-02 | SRCH-002, 007, 008, 010 | ✅ |
| FR-03 | SRCH-004, 005, 006, 007, 009 | ✅ |
| FR-04 | SRCH-003, 010, 011 | ✅ |
| FR-05 | SRCH-014, 017 | ✅ |
| FR-06 | SRCH-012, 016 | ✅ |
| AC-01 | SRCH-002 | ✅ |
| AC-02 | SRCH-004, 005 | ✅ |
| AC-03 | SRCH-003 | ✅ |
| AC-04 | SRCH-014, 015 | ✅ |
| AC-05 | SRCH-012 | ✅ |

## Open questions (for the PO)
- **Q1:** Is there a minimum and maximum search length? SCRUM-7 doesn't say, but the UI only searches 3–40 characters (SCRUM-10). This is covered in the extended set.
- **Q2:** Is the search term trimmed? Not specified. Covered in the extended set.
- **Q3:** Should Enter submit the search? Not specified. Covered in the extended set.
- **Q4:** AC-01 says "exactly 4 products", which depends on the demo catalogue. SRCH-008 compares against the live catalogue (API) instead of a fixed list.

## Summary
| Type | High | Medium | Low | Total |
|---|---|---|---|---|
| Positive | 8 | 4 | 1 | 13 |
| Negative | 2 | 2 | 0 | 4 |
| **Total** | **10** | **6** | **1** | **17** |

16 are automated and 1 is manual (SRCH-013).
