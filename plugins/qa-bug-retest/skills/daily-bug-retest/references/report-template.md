# Bug Re-check Report Templates

## HTML report (published as an artifact)

One self-contained page. Embed screenshots as base64 `data:` URIs so the page works without the files.

**Title:** `Bug Re-check <YYYY-MM-DD>`

Sections, in order:

1. **Header:** Jira project and query, run date and time (Asia/Yerevan), app URL and version (from the footer), browser.
2. **Summary bar:** counts of Still happening / Looks fixed / Changed / Intermittent / Can't retest, and an overall status:
   - 🟢 **Changes found**: at least one Looks fixed, and nothing Changed
   - 🔴 **New behaviour**: at least one Changed (a possible new bug or partial fix)
   - ⚪ **No change**: every retested bug is still happening
   - 🟠 **Blocked**: the app was down, or most bugs were Can't retest
3. **Results table:** one row per bug, in query order.

   | Key | Title | Priority | Verdict | Today's result | Screenshot | Next step |
   |-----|-------|----------|---------|----------------|------------|-----------|
   | SCRUM-41 | [Search] Text in the middle of a word is not found | High | 🔴 Still happening | "ammer" still shows "There are no products found." | thumbnail | — |
   | SCRUM-46 | [Search] Search field is emptied after every search | Low | ✅ Looks fixed | The field still shows "pliers" after the search | thumbnail | Ask the reporter to close |
   | SCRUM-43 | [Search] Search term with a decimal point finds nothing | Medium | 🟡 Changed | "7.5m" now finds Tape Measure 7.5m, but "7.5" still finds nothing | thumbnail | Possible new bug |
   | SCRUM-12 | Cart doesn't add my items sometimes | Medium | ⚫ Can't retest | Steps missing | — | Ask the reporter for steps |

   Clicking a thumbnail opens the full screenshot.
4. **Details for every bug that is not Still happening:** the steps followed, the bug's expected and actual result, today's result, the full screenshot, console errors, failed or checked API calls, and for Intermittent the result of each of the 5 runs.
5. **Jira comment drafts:** one per bug, in the format below, with a note saying whether they were posted.

## Chat summary

Keep it short; the report has the detail.

```
Bug re-check, <Fri 27 Nov, 09:00> (Yerevan): 9 open bugs, <✅ 1 looks fixed | 🟡 1 changed | ⚫ 1 can't retest | 🔴 6 still happening>
Project: SCRUM

✅ SCRUM-46 Search field emptied: the term now stays in the field. Ready for the reporter to close.
🟡 SCRUM-43 Decimal search: "7.5m" works now, "7.5" still finds nothing. Possible new bug.
⚫ SCRUM-12 Cart sometimes doesn't add items: steps missing.

Report: <artifact link>
Email: sent to 1 recipient
Jira comments: 9 drafts ready. Post them?
```

The same text is the email body; its first line is the email subject. In the email, drop the "Post them?" question.

- List only bugs that are not Still happening, one line each: key, short name, what is different today.
- When nothing changed, the message is the first line, the project line, the report link and the comments line.
- If the report couldn't be published, say so and include every bug's verdict in the summary instead.
- In a scheduled run, the last line is "Jira comments: drafts are in the report, not posted."

## Jira retest comment

One comment per bug. Plain text, short, facts only.

```
Retest <YYYY-MM-DD> (daily bug re-check): <Still happening | Looks fixed | Changed | Intermittent, x of 5 | Can't retest>
Environment: <app URL>, <app version>, <browser>, guest user
Result: <today's result, one or two sentences in the words of the bug's expected/actual result>
Evidence: <screenshot file name>; <API call and status, if checked>
<Only for Looks fixed:> Suggest closing after the reporter confirms.
<Only for Changed:> Behaviour differs from the original report; see the re-check report.
<Only for Can't retest:> Reason: <steps missing | login blocked by bot check | app down | ...>
```
