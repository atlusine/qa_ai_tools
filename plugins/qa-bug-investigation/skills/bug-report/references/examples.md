# Worked Example

> Illustrative example for teaching. The observed behaviour below is a sample, not a verified result from the live site.

## Input

> TC-017 failed on practicesoftwaretesting.com. I typed `p` in the search box and clicked Search, but the product list didn't change at all — no "Searched for" caption. Same with `pl`. With `pli` it works. Chrome.

## Output

# [Search] Search is ignored when the term is shorter than 3 characters

| Field | Value |
|-------|-------|
| Priority | Medium |
| Reproducibility | Always (3 of 3) |
| Environment | https://practicesoftwaretesting.com/ (Toolshop v5.0), Chrome 1xx, Windows 11 |
| User / role | Guest |
| Related | TC-017, FR-02, SCRUM-9 |

### Preconditions
- Home page opened, product grid fully loaded, search field empty.

### Steps to reproduce
1. Enter `p` in the **Search** field in the left filter panel.
2. Click **Search**.

### Expected result
Only products whose name contains "p" (case-insensitive) are shown, with the caption "Searched for: p" (source: TC-017, FR-02).

### Actual result
The product grid does not change and no "Searched for:" caption appears. No error is shown.

### Screenshots
| # | File | Step | Shows |
|---|------|------|-------|
| 1 | `search-01-term-entered.png` | Step 1 | `p` typed in the Search field, full product grid visible |
| 2 | `search-02-results-unchanged.png` | Step 2 | Actual result: grid unchanged after clicking Search, no "Searched for:" caption |
| 3 | `search-03-three-chars-works.png` | Comparison | Same steps with `pli`: grid filtered and caption "Searched for: pli" shown |

![Actual result](search-02-results-unchanged.png)

### Logs
- Network: no search request is sent after clicking **Search** (checked in DevTools → Network).

### Scope / variations
| Variation | Reproduces? |
|-----------|-------------|
| `p` (1 char) | Yes |
| `pl` (2 chars) | Yes |
| `pli` (3 chars) | No — results filtered correctly |
| Logged-in customer | Not checked |
| Firefox | Not checked |

### Notes
- Hypothesis (unverified): the client enforces a 3-character minimum before sending the request.

### Open questions / assumptions
- Is a 3-character minimum intended? If yes, the UI should say so and TC-017 needs updating; if no, this is a bug.

### Related items
- Test case: TC-017 (SCRUM-9)
- Requirement: FR-02

**Priority justification:** Medium — users cannot search by 1–2 letter terms, but typing 3+ letters is an easy workaround.
