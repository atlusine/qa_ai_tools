---
name: bug-report
description: Reproduce a suspected bug, confirm it is real (not flaky, not a test mistake), collect evidence, check the tracker for duplicates and write a clear, verifiable bug report with severity and priority; file it in Jira only after the user says yes. Use when asked to write, check or file a bug report, "is this a bug?", "reproduce this", "report what failed", after a failed test run, or when an exploratory session finds something wrong — for any feature, not one area.
---

# Bug Report

Turn "something looks wrong" into a bug report a developer can reproduce and fix without asking a single question.

## Inputs

Work from whatever the user gives: a failed test, a description, a screenshot, a customer complaint, a Jira ticket, or a page to explore. If something needed to reproduce is missing (URL, user role, test data, browser), ask once or state the assumption. Don't guess silently.

## Safety rules

- **Never file, comment on or edit a ticket without the user's explicit yes.** Trackers are shared, so draft first and show the draft.
- Use test or made-up data only. Never type real passwords, card numbers or personal data. If a step needs a login, ask the user to sign in.
- Say **"mocked"** whenever a failure was produced by faking a server response (e.g. Playwright `page.route`).
- On public demo sites, stay with light single-user actions. No load testing.

## Process

### 1. Reproduce and give a verdict
1. Follow the steps exactly, with the exact data. Use the browser tool if available (e.g. the Playwright MCP); otherwise reproduce by hand or with a test.
2. Do it **at least twice**. Record "N of N".
3. Save evidence as you go: screenshot of the actual result, console errors, failed API calls (method, URL, status, response body).
4. Give a verdict:

| Verdict | When |
|---|---|
| **REPRODUCED** | Fails every time (N of N) |
| **INTERMITTENT** | Fails sometimes (e.g. 1 of 3). Report the frequency and the times, never "always" |
| **NOT REPRODUCED** | Never fails. Write what you tried and what you saw; don't write a bug |

If the user only asked to reproduce, stop here and answer with the verdict and the evidence.

### 2. Make sure it's the app, not the test
- Look at the screenshot yourself. Does it really show the failure?
- Test-side causes: reading the page before the response arrived (wait for the response, not a timer), wrong selector, stale data, wrong environment.
- Ask the API the same question (same input). API wrong means **backend** bug; API right but page wrong means **frontend** bug.

### 3. Find the pattern
Vary the input to learn **when it breaks and when it doesn't**: case, position inside a word, length (min−1/min/max/max+1), punctuation, spaces, another item, another role, mobile, slow or failed network. One sentence like "only text at the start of a word matches" is worth more than ten screenshots. Note the likely root cause if the pattern shows it.

### 4. Check it against the requirement
Quote the requirement or acceptance criterion it breaks. If the spec doesn't define the behaviour, write the expected result as an **assumption**, add a **question for the PO**, and keep the priority low.

### 5. Check for duplicates
Search the tracker before writing (e.g. JQL `project = <KEY> AND issuetype = Bug AND text ~ "<key words>"`, plus the epic's child items).
- **Same bug already exists** → draft a **comment** with the new information (steps, pattern, boundary, evidence) instead of a new ticket.
- A vague existing report (e.g. a customer complaint) that your bug explains → a comment with your repro steps.
- **One root symptom = one bug.** Don't split one cause into many tickets, and don't hide two different visible problems in one ticket.

### 6. Write the report
Use `references/bug-template.md`. Set severity and priority with `references/severity-priority.md`, each with a one-line reason. See `references/examples.md` for a complete worked example.

### 7. File (only after the user says yes)
1. Show the list first: title, severity, priority, parent epic.
2. File **one** ticket (type Bug, parent = the epic, labels, priority). Read it back and check the parent, labels and priority, then file the rest.
3. Jira gotcha: inside **table cells**, Markdown numbered steps get mangled ("1. Type 2. Click" shows as "Type 2. Click"). Use `Step 1) … Step 2) …` in tables. Normal numbered lists are fine.
4. Re-search to confirm every ticket exists, and give the user the keys as links. New tickets are in the **Backlog** or under the epic, not on the Board until they're added to a sprint.

## Writing rules
- **Title:** `[Area] What is wrong (exact data)`, e.g. `[Search] "7.5m" finds nothing although "Tape Measure 7.5m" exists`. Never "X doesn't work".
- Steps: numbered, one action each, exact data in `code`, runnable by someone who has never seen the app.
- Expected: what the requirement says, quoted. Actual: the **exact text on screen**, quoted.
- Facts, not opinions. No "obviously", no guesses presented as facts. Put guesses under "Likely cause".
- One bug per report.

## Output
1. **Verdict** (REPRODUCED / INTERMITTENT / NOT REPRODUCED) with N of N and the evidence list.
2. The **bug report(s)** in the template, or a **comment draft** for an existing ticket.
3. **Open questions** for the PO, if any.
4. After filing: the ticket keys as links.

## Review checklist
- [ ] Reproduced at least twice; the verdict matches N of N
- [ ] Test-side causes ruled out; API checked where there is one
- [ ] Pattern described (when it fails / when it works)
- [ ] Requirement quoted, or the expected result marked as an assumption
- [ ] Duplicate search done; no duplicate ticket
- [ ] Title says what + where with exact data
- [ ] Steps runnable by a stranger; exact on-screen text in Actual
- [ ] Severity and priority each have a reason
- [ ] Evidence named; "mocked" stated where used
- [ ] Nothing filed without the user's yes
