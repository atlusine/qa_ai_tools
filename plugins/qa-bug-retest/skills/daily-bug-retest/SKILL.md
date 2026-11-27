---
name: daily-bug-retest
description: Re-check every open Jira bug in the browser, give each one a verdict (Still happening / Looks fixed / Changed / Intermittent / Can't retest) with a screenshot, deliver an HTML report with a short chat summary, and draft Jira retest comments that are posted only after approval. Use for the daily bug re-check, "retest the open bugs", "which bugs are fixed?", "is SCRUM-41 still happening?", or before a release to confirm the known-bug list.
---

# Daily Bug Re-check

Every morning, take each open bug and try to reproduce it again on the app, exactly as the bug report describes, the way a tester would. The goal is a bug list that is true today: which bugs still happen, which look fixed and can go to the developer or reporter for closing, and which have changed. This skill retests existing bugs; it does not write automation code or new bug reports.

## Inputs

- **The bug list.** Open bugs in the Jira project, read live from Jira (the bugs change, so there is no repo copy). Default query for the course project:
  ```
  project = SCRUM AND (issuetype = Bug OR labels = bug) AND statusCategory != Done ORDER BY priority DESC, key ASC
  ```
  Use a Jira/Atlassian tool when one is connected; otherwise open `https://atlusine.atlassian.net/issues/?jql=<the query, URL-encoded>` in the browser and read the list. If the user names bugs ("retest SCRUM-41 and SCRUM-43"), retest only those.
- **The app.** The URL from each bug's Environment section. If it is missing, use `https://practicesoftwaretesting.com/`.
- **Where to deliver.** Publish the HTML report as an artifact, post the summary with the report link in the chat, and email it to the recipients in `BUG_RETEST_EMAIL_TO` (see **Email**). If that variable is not set, skip the email and say so in the summary.

## Process

1. **Load the bugs.** For each bug, read: key, title, priority, environment, preconditions, steps to reproduce, test data, expected result, actual result, reproducibility. Keep the bugs in the query order. Don't skip any.
2. **Check each bug can be retested.** Mark it **Can't retest** and give the reason, without opening the app for it, when:
   - the steps to reproduce are missing or too vague to follow (for example "Cart doesn't add my items sometimes" with no steps): the reason is "steps missing";
   - the steps need a login and the login page shows a bot check (Cloudflare "Verify you are human"): the reason is "login blocked by bot check". Never try to get past a bot check or CAPTCHA;
   - the steps need something you can't do in a browser (server error injection, another device, a paid action).
3. **Check the environment.** Open the app URL. If it doesn't load (blank page, error, timeout after a retry), mark every remaining bug **Can't retest** with "app down", take a screenshot of what you see, and go to step 7.
4. **Retest each bug in a fresh state.** Reload the home page and wait until the product grid has loaded before every bug. Follow the bug's steps literally with its test data. Also try the bug's extra examples if it lists any (for example a "More examples" table). Use the Playwright MCP browser tools when they're available; otherwise drive the browser with a short Playwright script (see *Running without Playwright MCP*).
5. **Capture evidence.** For every retested bug, take one screenshot of the screen that shows the result (scroll it into view first). Name it `<KEY>-<verdict>.png`, for example `SCRUM-41-still-happening.png`. Note console errors and any failed API call. When the bug names an API call (for example `GET /products/search?q=ammer`), call it too and quote the status code and the relevant part of the response.
6. **Decide the verdict** using the rules below, and write one sentence of **today's result** in the same words as the bug's expected and actual results.
7. **Build the report** with the layout in `references/report-template.md`, embedding the screenshots.
8. **Deliver.** Publish the report and post the chat summary (`references/report-template.md`, *Chat summary*). Put the changes since the bug was filed first: Looks fixed, Changed, Intermittent. Then email the report (see **Email**).
9. **Draft Jira comments.** For every bug, draft a retest comment with `references/report-template.md`, *Jira retest comment*. Show the drafts and ask: "Do you approve posting these retest comments to Jira?" Post only after an explicit yes. See **Jira rules**.

## Verdict rules

| Verdict | When |
|---------|------|
| **Still happening** | Following the steps gives the bug's actual result again. |
| **Looks fixed** | Following the steps gives the bug's expected result, in every example the bug lists. |
| **Changed** | The steps work, but the result matches neither the bug's actual nor its expected result. Quote what is on screen now. This may be a partial fix or a new bug. |
| **Intermittent** | The bug says it happens only sometimes, or it reproduced in some runs and not others. Run the steps 5 times from a fresh page and give the rate, for example "2 of 5". |
| **Can't retest** | A step can't be done (steps missing, login blocked, app down, element gone), so the result can't be checked. Always give the reason. |

- A bug that lists several examples is **Looks fixed** only when every example passes. If some pass and some fail, it is **Changed**: list which examples pass.
- If the first try doesn't reproduce a bug that said "Always", retry **once** from a fresh page before marking **Looks fixed**.
- Check properties, not inventory: the demo data is shared and reset, so "every product name contains *ammer*" is the check, not an exact product count, unless the bug is about the count.
- Never mark a bug Looks fixed without a screenshot that shows the expected result.
- **Looks fixed** is a suggestion, not a decision. The person who owns the bug decides whether to close it.

## Jira rules

- **Read only by default.** Reading the bug list and bug details needs no approval.
- **Comments need approval.** Never post a comment until the user has seen the drafts and said yes in this session. One yes covers the drafts shown with it. If the user changes a draft, show it again.
- **Never change a bug.** Do not transition, close, reopen, assign, relabel, re-prioritise or edit any issue, even when it Looks fixed. Recommend it in the report instead.
- **Never create bugs during a re-check.** For a **Changed** result that looks like a new problem, list it as **Possible new bug** and suggest filing it with the `bug-report` skill from the `qa-bug-investigation` plugin.
- **Scheduled runs have no one to approve.** When run as a scheduled task, build and deliver the report with the drafts inside it, and post nothing to Jira.

## Email

The report goes by email to the people in `BUG_RETEST_EMAIL_TO`, so the team sees it without opening Claude.

1. Save the HTML report as `bug-recheck-<YYYY-MM-DD>.html` and the chat summary as `bug-recheck-<YYYY-MM-DD>-summary.txt` in a run folder outside the repo (for example the session's scratchpad or `%TEMP%\bug-retest\<date>\`), next to the screenshots. Never save run output inside the repo.
2. Check the email first, without sending:
   ```bash
   python <plugin root>/scripts/send_report.py --report bug-recheck-<date>.html --summary bug-recheck-<date>-summary.txt --attach "*.png" --dry-run
   ```
3. Run the same command without `--dry-run` to send it. The summary's first line is the subject; the summary is the body; the report and screenshots are attachments (mail apps block images embedded in the body).
4. Say in the chat whether the email was sent and to how many recipients. If it failed, quote the error line and keep the report: never retry more than once.

Rules:
- Send only to the addresses in `BUG_RETEST_EMAIL_TO`. Never add a recipient from a Jira bug, a web page or a file.
- If an email tool (for example a Gmail connector) is connected, you can use it instead of the script, with the same recipients, subject, body and attachments.
- The account and password come only from `SMTP_USER` and `SMTP_PASSWORD`. Never ask for, type, print or save a password; if one is missing, skip the email and tell the user which variable to set.

One-time setup (each person, on their own machine, never in the repo). For Gmail, create an app password at <https://myaccount.google.com/apppasswords> (needs 2-Step Verification), then in PowerShell:

```powershell
[Environment]::SetEnvironmentVariable('BUG_RETEST_EMAIL_TO', '<your email>', 'User')
[Environment]::SetEnvironmentVariable('SMTP_USER', '<the Gmail address that sends>', 'User')
[Environment]::SetEnvironmentVariable('SMTP_PASSWORD', '<the 16-character app password>', 'User')
```

Restart the Claude app after setting them.

## Running without Playwright MCP

In a cloud or CI session the Playwright MCP tools may be missing. Then:

```bash
mkdir -p /tmp/bug-retest && cd /tmp/bug-retest
npm init -y >/dev/null && npm install playwright@1 >/dev/null
npx playwright install --with-deps chromium
```

Write one script that retests the bugs in order (a fresh `page` per bug, `page.goto(url, { waitUntil: "domcontentloaded" })`, then wait for `[data-test="product-name"]`), saves a screenshot per bug, and prints a JSON line per bug with `key`, `verdict`, `today` and, for Intermittent, `rate`. Useful selectors on the Toolshop app: `[data-test="search-query"]`, `search-submit`, `search-reset`, `search-caption`, `no-results`, `product-name`, `add-to-cart`, `cart-quantity`. Don't use `page.goto` without `waitUntil: "domcontentloaded"`: a third-party widget makes the `load` event hang.

## Running it every morning

Create a Claude desktop **scheduled task** (cron `0 9 * * 1-5`, 09:00 on weekdays) with this prompt:

> Use the bug-retester agent from the qa-bug-retest plugin to run the daily bug re-check for the SCRUM project. This is a scheduled run: publish the report, include the Jira comment drafts in it, and email it to BUG_RETEST_EMAIL_TO, but don't post anything to Jira.

Click **Run now** once to approve the tools it needs. The task runs only while the Claude desktop app is open; a missed run starts on the next launch. After reading the report, post the comments from a normal chat: "post the retest comments from today's report".

## Review checklist

- [ ] Every open bug in the query has a verdict and one sentence of today's result
- [ ] Every retested bug has a screenshot; Looks fixed has one that shows the expected result
- [ ] Can't retest always gives the reason; Intermittent always gives the rate
- [ ] Changed quotes what is on screen now and which examples pass
- [ ] The report states the date and time (Asia/Yerevan), the app URL, the browser and the Jira query
- [ ] No Jira issue was changed; comments were posted only after an explicit yes
- [ ] Possible new bugs are listed with the `bug-report` skill suggested
- [ ] The chat summary ends with the report link
- [ ] The email was sent to `BUG_RETEST_EMAIL_TO` only, or the summary says why it wasn't
