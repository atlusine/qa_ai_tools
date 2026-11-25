# Bug reports: SCRUM-7 Product Search (filed in Jira on 2026-11-25)

Common environment for all bugs:
- URL: https://practicesoftwaretesting.com/ (Toolshop v5.0, frontend v2.5 built 2026-10-11)
- Chromium (Playwright 1.65.1), macOS, guest user, 2026-11-25 14:56–15:00 UTC
- Reproducibility: every bug failed **2 of 2** automated runs, and the test is named in each bug
- Filed under parent SCRUM-7 with labels `narek`, `search`, `bug`: **SCRUM-41 … SCRUM-47** (one per bug below). Test cases: SCRUM-48 (requirements), SCRUM-49 (extended)

Search Jira before filing (audited on 2026-11-25: SCRUM-10, 11 and 12 were the only existing bugs). **None of these duplicate an existing ticket.** SCRUM-10 already covers the 1–2 character problem, so the 41+ character finding goes there as a comment.

---

## BUG-1 → [SCRUM-41](https://atlusine.atlassian.net/browse/SCRUM-41): Search doesn't find text in the middle of a word ("ammer", "lier"); "hammer" misses Sledgehammer

| Severity | Priority | Breaks |
|---|---|---|
| Medium: customers don't see products that match their search | High: core search requirement | FR-02 "name contains the entered text", FR-03 "partial" |

**Steps**
1. Open the home page.
2. Type `ammer` in Search and click **Search**.

**Expected:** the 7 products whose name contains "ammer": Claw Hammer, Claw Hammer with Fiberglass Handle, Claw Hammer with Shock Reduction Grip, Court Hammer, Hammer, Sledgehammer, Thor Hammer.
**Actual:** "0 products found for 'ammer'", "There are no products found."

**More examples (same cause):**

| Term | Missing from results |
|---|---|
| `hammer` | Sledgehammer |
| `belt` | Leather toolbelt |
| `driver` | Mini Screwdriver, Phillips Screwdriver |
| `lier` | all 4 pliers |

Matching only works at the **start of a word** (`ham`, `pli` work). See the root-cause note in the run report (tests PR).

**Evidence:** `evidence/EX-21-ammer.png`. Tests SRCH-007, SRCH-008, SRCH-010, EX-21, EX-38.

---

## BUG-2 → [SCRUM-42](https://atlusine.atlassian.net/browse/SCRUM-42): A server error or network failure is shown as "There are no products found."

| Severity | Priority | Breaks |
|---|---|---|
| High: customers are told a product doesn't exist when the search is actually broken, and outages stay hidden | High | FR-05 (the no-results message is only for "no product matches") |

**Steps**
1. Open the home page.
2. Make the search API fail. In the test, `/products/search` is mocked to return **HTTP 500**, or the request is aborted.
3. Type `pliers` and click **Search**.

**Expected:** an error message such as "Search is not available, please try again". **Not** a no-results message.
**Actual:** "Searched for: pliers", "**0 products found for 'pliers'**", "There are no products found."

**Real-world evidence:** this also happened **without mocking** at about 14:00 UTC on 2026-11-25. A real `PLIERS` search got HTTP 500 from the server, and the page said "There are no products found." (`evidence/ac02-PLIERS-no-results.png`).
**Evidence:** `evidence/EX-36-server-500.png`. Tests EX-36 (500), EX-37 (network failure).

---

## BUG-3 → [SCRUM-43](https://atlusine.atlassian.net/browse/SCRUM-43): A search term with a decimal point finds nothing ("7.5m")

| Severity | Priority | Breaks |
|---|---|---|
| Medium: product sizes like 7.5m and 1.5mm are typical search terms in a tool shop | Medium | FR-02 |

**Steps:** type `7.5m` and click **Search**.
**Expected:** Tape Measure 7.5m.
**Actual:** "There are no products found." `5m` finds both tape measures, and `7.5` and `measure 7.5m` find nothing, so the `.` seems to split the term.
**Evidence:** `evidence/EX-20-7.5m.png`. Test EX-20.

---

## BUG-4 → [SCRUM-44](https://atlusine.atlassian.net/browse/SCRUM-44): Punctuation and word order are ignored, so wrong products are shown

| Severity | Priority | Breaks |
|---|---|---|
| Low | Low, **PO decision needed** (a forgiving search may be wanted) | FR-02 "name contains the entered text" (taken literally) |

| Term | Expected by FR-02 | Actual |
|---|---|---|
| `pliers!` | no results | 4 pliers |
| `*pliers*` | no results | 4 pliers |
| `(set)` | Open-end Spanners (Set) | + Chisels Set |
| `pliers long` | no results | Long Nose Pliers |

**Question for the PO:** should search be literal "contains" (as FR-02 says) or a forgiving word search? If it's word search, FR-02 needs updating.
**Evidence:** `evidence/EX-22-word-order.png`. Tests SRCH-017, EX-19, EX-22, EX-29.

---

## BUG-5 → [SCRUM-45](https://atlusine.atlassian.net/browse/SCRUM-45): A search of spaces only shows "Searched for:" and "0 products found"

| Severity | Priority |
|---|---|
| Low | Low |

**Steps:** type 3 spaces, click **Search**.
**Expected:** same as an empty search: full list, no caption (spaces are already trimmed for `  pliers  `).
**Actual:** a request is sent with `{"q":"   "}`. The page shows the caption "Searched for:" with nothing after it, then "There are no products found." and an empty grid.
**Evidence:** `evidence/EX-13-whitespace.png`. Test EX-13.

---

## BUG-6 → [SCRUM-46](https://atlusine.atlassian.net/browse/SCRUM-46): The search box is emptied after every search

| Severity | Priority |
|---|---|
| Low (usability) | Low |

**Steps:** type `pliers`, click **Search**.
**Expected:** the field still shows `pliers`, so the user can fix a typo. FR-06 says X "clears the search field", which means the field still holds the text after a search.
**Actual:** the field is empty right after the search. Only the caption shows the term.
**Evidence:** `evidence/EX-15-field-cleared.png`. Test EX-15.

---

## BUG-7 → [SCRUM-47](https://atlusine.atlassian.net/browse/SCRUM-47): Going Back from a product page loses the search results

| Severity | Priority |
|---|---|
| Low (usability) | Low |

**Steps:** search `pliers`, open "Pliers", click the browser **Back** button.
**Expected:** the 4 pliers and the caption "Searched for: pliers" are still shown.
**Actual:** the full, unsearched product list is shown, so the user has to search again.
**Evidence:** `evidence/EX-33-back.png`. Test EX-33.

---

## Comment for existing SCRUM-10 (don't file as a new bug; NOT posted yet)

> Confirmed on 2026-11-25 (Playwright, 2 of 2 runs): `p` and `pl` send no request and show no message.
> **The same silent ignore also happens at the upper end:** 40 characters are searched, but **41+ characters send no request**, and the previous caption stays on screen. The frontend apparently only accepts 3–40 characters. If that's intended, both limits should be shown to the user.
> Evidence: `EX-08-2-chars.png`, `EX-11-41-chars.png`. Tests EX-07, EX-08, EX-11.
