# Toolshop product search (SCRUM-7): bugs found

Found on 2026-11-25 by the automated search tests (tests, test cases and run reports are in the tests PR). Every bug failed **2 of 2** runs. Full reports with steps, expected/actual and evidence are in [`bug-reports.md`](bug-reports.md). All are filed in Jira under SCRUM-7.

| Jira | Severity | Bug | Evidence |
|---|---|---|---|
| SCRUM-41 | Medium | Text in the middle of a word is not found (`ammer`, `lier`); `hammer` misses Sledgehammer | `evidence/EX-21-ammer.png` |
| SCRUM-42 | **High** | A server error or network failure is shown as "There are no products found." | `evidence/EX-36-server-500.png`, `evidence/ac02-PLIERS-no-results.png` |
| SCRUM-43 | Medium | A term with a decimal point finds nothing (`7.5m`) | `evidence/EX-20-7.5m.png` |
| SCRUM-44 | Low (PO decision) | Punctuation and word order are ignored (`pliers!`, `*pliers*`, `(set)`, `pliers long`) | `evidence/EX-22-word-order.png` |
| SCRUM-45 | Low | Search with only spaces shows an empty "Searched for:" caption and "no products found" | `evidence/EX-13-whitespace.png` |
| SCRUM-46 | Low | The search field is emptied after every search | `evidence/EX-15-field-cleared.png` |
| SCRUM-47 | Low | Going Back from a product page loses the search results | `evidence/EX-33-back.png` |

**Existing ticket, not re-filed:** SCRUM-10 (1–2 character searches are ignored) is confirmed. New info: 41+ characters are also silently ignored (`evidence/EX-08-2-chars.png`, `evidence/EX-11-41-chars.png`). A comment for SCRUM-10 is drafted at the end of `bug-reports.md` and isn't posted yet.

**Likely root cause of SCRUM-41, 43 and 44:** the backend uses a word-based (full-text) search that splits on punctuation and matches word starts, instead of the "name contains the text" rule in FR-02.
