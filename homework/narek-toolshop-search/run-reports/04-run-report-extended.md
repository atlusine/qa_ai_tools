# Test run report: SCRUM-7 search, full run (requirements + extended)

| | |
|---|---|
| Run | 2026-11-25 14:56–15:00 UTC, every test run **twice** (`--repeat-each=2`) |
| Tool | Playwright 1.65.1, Chromium, macOS, guest; mobile = 375×812 touch |
| Suites | `search-requirements.spec.ts` (17) + `search-extended.spec.ts` (41) |
| Oracle | Live catalogue from `GET /products` (50 products), rule FR-02/03 "name contains the text, case-insensitive" |
| Result | **58 cases: 39 passed, 18 failed, 1 not run.** No flaky results: every case gave the same result in both runs |

## Results by group

| Group | Cases | Pass | Fail | Failing cases → bug |
|---|---|---|---|---|
| Requirements (ACs and FRs) | 17 | 12 | 4 | SRCH-007/008/010 → BUG-1, SRCH-017 → BUG-4. SRCH-013 not run (login) |
| How the user submits (Enter, typing, keyboard, double-click, rapid, request count) | 6 | 6 | 0 | — |
| Length boundaries | 5 | 2 | 3 | EX-07/08 → **SCRUM-10** (exists), EX-11 → SCRUM-10 addendum |
| Spaces and empty | 4 | 2 | 2 | EX-13 → BUG-5, EX-15 → BUG-6 |
| Product-name shapes | 7 | 3 | 4 | EX-21 → BUG-1, EX-20 → BUG-3, EX-19/22 → BUG-4 |
| Special characters and security | 10 | 9 | 1 | EX-29 → BUG-4 |
| Combined with other actions | 5 | 4 | 1 | EX-33 → BUG-7 |
| Server and network problems (mocked) | 2 | 0 | 2 | EX-36/37 → BUG-2 |
| Monitoring | 2 | 1 | 1 | EX-38 → BUG-1 |

## What works well ✅
- All 5 acceptance criteria pass, and `PLIERS` was stable in 10 of 10 API calls (EX-39). The 14:00 failure has not come back.
- Enter key, slow typing, keyboard-only, double-click (no duplicates), 5 rapid searches (the last one wins) and exactly 1 request per search.
- **Security:** `%%%`, `pl_ers`, `' OR '1'='1`, `<script>`, `<b>` and backslash/quote input showed no script run, no HTML rendered, no 5xx and no wildcard behaviour.
- Multi-word (`long nose`), hyphen (`flat-head`), digits (`24v`), emoji and Cyrillic work.
- Search works with sorting, with the category filter, in German, and on a phone screen.
- Leading and trailing spaces are trimmed (`  pliers  ` → 4 pliers).

## What fails ❌

| Bug | Sev | Summary | Cases |
|---|---|---|---|
| BUG-1 (SCRUM-41) | Medium | Text inside a word is not found (`ammer`, `lier`; `hammer` misses Sledgehammer, `belt` misses Leather toolbelt, `driver` misses both screwdrivers) | SRCH-007, 008, 010, EX-21, EX-38 |
| BUG-2 (SCRUM-42) | High | A server error or network failure is shown as "0 products found / There are no products found." | EX-36, EX-37 |
| BUG-3 (SCRUM-43) | Medium | A term with a decimal point finds nothing: `7.5m` → 0 (Tape Measure 7.5m exists) | EX-20 |
| BUG-4 (SCRUM-44) | Low | Punctuation and word order are ignored, so extra results appear: `pliers!`, `*pliers*` → 4 pliers; `(set)` → also Chisels Set; `pliers long` → Long Nose Pliers | SRCH-017, EX-19, 22, 29 |
| BUG-5 (SCRUM-45) | Low | Whitespace-only search shows "Searched for:" and "0 products found" | EX-13 |
| BUG-6 (SCRUM-46) | Low | The search box is emptied after every search | EX-15 |
| BUG-7 (SCRUM-47) | Low | Back from a product page loses the search results | EX-33 |
| SCRUM-10 (exists) | — | 1–2 characters silently ignored (confirmed), **and also 41+ characters** (new info) | EX-07, 08, 11 |

**Root cause (likely):** the backend uses a **word-based (full-text) search**, not a "contains" substring match. It splits the input and the names into words, drops punctuation, and matches the start of words. That one design explains BUG-1, BUG-3 and BUG-4. The frontend separately only sends terms of 3–40 characters (SCRUM-10, EX-11).

## Not covered
- Logged-in search (SRCH-013): needs Narek to sign in.
- Search results across more than one page: no term in the current catalogue matches more than 9 products.
- Firefox and Safari (only Chromium is installed), screen-reader accessibility, performance under load.


> Filed in Jira on 2026-11-25: bugs SCRUM-41…47, test cases SCRUM-48 (requirements) and SCRUM-49 (extended), all under SCRUM-7.
