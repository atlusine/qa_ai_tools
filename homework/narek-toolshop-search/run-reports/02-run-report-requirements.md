# Test run report: SCRUM-7 search, requirement-based cases (draft)

| | |
|---|---|
| Run | 2026-11-25 14:48 UTC, Playwright 1.65.1, Chromium, macOS, guest |
| Suite | `../playwright/tests/search-requirements.spec.ts` (cases in `../test-cases/01-test-cases-requirements.md`) |
| App | https://practicesoftwaretesting.com/ (Toolshop v5.0 / frontend v2.5) |
| Oracle | Fixed AC data, plus the live catalogue from the API (`/products`, 50 items) for "contains" checks |
| Result | **17 cases: 12 passed, 4 failed, 1 not run (manual)** |

## Results

| ID | Case | Result | Note |
|---|---|---|---|
| SRCH-001 | Controls shown | ✅ | |
| SRCH-002 | `pliers` → 4 pliers (AC-01) | ✅ | |
| SRCH-003 | Caption "Searched for: pliers" (AC-03) | ✅ | |
| SRCH-004 | `PLIERS` → 4 (AC-02) | ✅ | The intermittent failure from 14:00 did not happen again |
| SRCH-005 | `plier` → 4 (AC-02) | ✅ | |
| SRCH-006 | `pLiErS` → 4 | ✅ | |
| SRCH-007 | `lier` (mid-word) → 4 | ❌ | 0 results → **BUG-1 (SCRUM-41)** |
| SRCH-008 | `hammer` = catalogue | ❌ | 6 shown, 7 expected: **Sledgehammer missing** → **BUG-1 (SCRUM-41)** |
| SRCH-009 | `ham` = catalogue | ✅ | |
| SRCH-010 | Second search replaces first | ❌ | Replacing works, but the hammer results miss Sledgehammer (same as SRCH-008) → **BUG-1 (SCRUM-41)** |
| SRCH-011 | Caption exact text `PLIERS` | ✅ | |
| SRCH-012 | X restores list (AC-05) | ✅ | |
| SRCH-013 | Logged-in search (US-01) | ⏭ Not run | Needs a password typed by Narek |
| SRCH-014 | No-results message (AC-04) | ✅ | |
| SRCH-015 | No cards (AC-04) | ✅ | |
| SRCH-016 | X after no-results | ✅ | |
| SRCH-017 | `pliers!` → no results | ❌ | Shows the 4 pliers; the `!` is ignored → **BUG-4 (SCRUM-44)** (or a PO question) |

## Requirement coverage after the run

| Req | Status |
|---|---|
| FR-01, FR-04, FR-06, AC-01, AC-02, AC-03, AC-04, AC-05 | ✅ Pass |
| FR-02 "name contains the entered text" | ❌ Fail (SCRUM-41, SCRUM-44) |
| FR-03 "partial" matching | ❌ Fail (SCRUM-41): only matches at the **start of a word** |
| FR-05 | ⚠️ Pass for `xyzxyz`, but `pliers!` doesn't give no-results (SCRUM-44) |
| US-01 logged in | ⏭ Not run |

## Bugs found (details in Jira SCRUM-41…47 and the bug-reports PR)
- **BUG-1 → SCRUM-41 (Medium):** search only matches the start of words, so the text "inside" a word isn't found (`lier`, `iers`, `ammer`; Sledgehammer is missing for `hammer`). This breaks FR-02 and FR-03.
- **BUG-4 → SCRUM-44 (Low):** punctuation in the term is ignored, so `pliers!` returns the pliers. FR-02 says the name must *contain* the text. This may be wanted (more forgiving search), so the PO should decide.

## Note on AC data
All five acceptance criteria **pass**. The failures come from FR-02 and FR-03, which are wider than the ACs. The ACs only test `pliers`/`PLIERS`/`plier`, where the text is at the start of a word. **That's a gap in the ACs:** the bug fits through it.


> Filed in Jira on 2026-11-25: bugs SCRUM-41…47, test cases SCRUM-48 (requirements) and SCRUM-49 (extended), all under SCRUM-7.
