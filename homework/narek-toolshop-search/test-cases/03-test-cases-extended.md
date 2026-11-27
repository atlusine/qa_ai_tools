# SCRUM-7 Product Search: extended test cases (self-monitoring)

These cases go beyond the ACs and cover **everything a person can do with the search box**: how they submit, what they type, what they do before and after, devices, languages, and what happens when the network or server misbehaves. They also include a **monitoring sweep** that compares the UI with the live catalogue.

- **In Jira:** SCRUM-49 (filed 2026-11-25)
- **Automated in:** `../playwright/tests/search-extended.spec.ts`
- **Oracle:** FR-02/FR-03 ("name contains the text, case-insensitive") applied to the live catalogue from `GET /products`
- **(A)** = SCRUM-7 doesn't define this behaviour. The expected result is a reasonable assumption and doubles as a PO question.
- **Common preconditions:** desktop Chromium, guest, home page loaded, Search field empty.

## 1. How the user submits

| ID | Title | Pri | Steps / data | Expected result |
|---|---|---|---|---|
| EX-01 | Verify Enter submits the search (A) | Medium | Type `pliers`, press Enter | 4 pliers, caption shown |
| EX-02 | Verify typing letter by letter gives the same result | Low | Type `pliers` one key at a time, click Search | 4 pliers |
| EX-03 | Verify keyboard-only use works | Medium | Focus field, type `pliers`, Tab to Search, press Enter | 4 pliers |
| EX-04 | Verify double-click on Search shows each product once | Medium | Type `pliers`, double-click Search | 4 pliers, no duplicate cards |
| EX-05 | Verify the last of 5 rapid searches wins | High | `saw`, `drill`, `hammer`, `wrench`, `pliers` fast | Caption "Searched for: pliers" and the 4 pliers |
| EX-06 | Verify one click sends exactly one search request | Low | Type `pliers`, click Search | 1 request to `/products/search` |

## 2. Length boundaries

| ID | Title | Pri | Data | Expected result |
|---|---|---|---|---|
| EX-07 | Verify 1 character is searched (SCRUM-10) | Medium | `p` | Products whose name contains "p" (FR-02) |
| EX-08 | Verify 2 characters are searched | Medium | `pl` | Products containing "pl" |
| EX-09 | Verify 3 characters are searched | Medium | `pli` | Products containing "pli" |
| EX-10 | Verify 40 characters are searched | Low | `a`×40 | Request sent, "There are no products found." |
| EX-11 | Verify 41 characters are searched or explained (A) | Low | `a`×41 | Request sent, caption "Searched for: a…a", or a message about the limit. **Not** silently ignored |

## 3. Spaces and empty input

| ID | Title | Pri | Data | Expected result |
|---|---|---|---|---|
| EX-12 | Verify Search with an empty field keeps the full list (A) | Low | (empty) | Full list, no caption, no error |
| EX-13 | Verify whitespace-only behaves like empty (A) | Low | 3 spaces | Full list, no caption, no error |
| EX-14 | Verify leading and trailing spaces are trimmed (A) | Medium | `  pliers  ` | 4 pliers |
| EX-15 | Verify the field keeps the term after searching (A) | Low | `pliers` | Field still shows `pliers` (FR-06 implies the field holds the text until X) |

## 4. What the user types: real product-name shapes

| ID | Title | Pri | Data | Expected result |
|---|---|---|---|---|
| EX-16 | Verify a multi-word term | Medium | `long nose` | Long Nose Pliers |
| EX-17 | Verify a hyphenated term | Medium | `flat-head` | Flat-Head Wood Screws |
| EX-18 | Verify letters and digits | Medium | `24v` | Cordless Drill 24V |
| EX-19 | Verify parentheses | Low | `(set)` | Open-end Spanners (Set) |
| EX-20 | Verify a decimal point | Low | `7.5m` | Tape Measure 7.5m |
| EX-21 | Verify a mid-word term | High | `ammer` | All 7 hammers incl. Sledgehammer |
| EX-22 | Verify words in a different order are not matched | Low | `pliers long` | No results ("contains" is literal) |

## 5. Special characters and security (overlaps with SCRUM-20)
Each data value is searched separately. Expected for all: **no alert dialog, no 5xx, caption shows the text literally**, and results follow FR-02 (no product contains these, so no results).

| ID | Data | Pri |
|---|---|---|
| EX-23 | `%%%` (SQL wildcard) | High |
| EX-24 | `pl_ers` (`_` = SQL single-character wildcard; must NOT find "pliers") | High |
| EX-25 | `' OR '1'='1` (SQL injection) | High |
| EX-26 | `<script>alert(1)</script>` (XSS) | High |
| EX-27 | `<b>pliers</b>` (HTML rendering) | Medium |
| EX-28 | `\\\` and `"""` | Medium |
| EX-29 | `*pliers*` | Medium |
| EX-30 | `🔨🔨🔨` and `Плоскогубцы` (emoji, Cyrillic) | Low |

Special characters are used 3 at a time because 1–2 character terms are never searched (SCRUM-10). A single `%` only tests that rule.

## 6. Search combined with other actions

| ID | Title | Pri | Steps | Expected result |
|---|---|---|---|---|
| EX-31 | Verify sorting keeps the search | Medium | Search `hammer`, sort Price High–Low | Only hammers, sorted by price descending |
| EX-32 | Verify the category filter narrows the search | Medium | Search `claw`, tick category Hammer | Only claw hammers |
| EX-33 | Verify results survive product page → Back (A) | Low | Search `pliers`, open a result, browser Back | The 4 pliers and the caption are still shown |
| EX-34 | Verify search in German UI | Low | Switch language to DE, search `pliers` | 4 pliers |
| EX-35 | Verify search on a phone screen (375×812) | Medium | Mobile viewport, search `pliers` | Controls reachable, 4 pliers |

## 7. Server and network problems

| ID | Title | Pri | Steps | Expected result |
|---|---|---|---|---|
| EX-36 | Verify a server error is shown as an error (A) | High | Search API returns 500 (mocked) | An error message. **Not** "There are no products found." |
| EX-37 | Verify a network failure is shown as an error (A) | Medium | Search request aborted (mocked) | An error message. **Not** "There are no products found." |

## 8. Monitoring

| ID | Title | Pri | Steps | Expected result |
|---|---|---|---|---|
| EX-38 | Verify 30 common terms match the live catalogue | High | Search each in the UI | UI results = catalogue names containing the term |
| EX-39 | Verify AC terms are stable over repeats | High | `pliers`, `PLIERS`, `plier` × 5 via API | 4 pliers every time, HTTP 200 every time |
