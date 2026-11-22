---
name: bug-report
description: Write a clear, reproducible bug report from rough notes, a failed test case, logs, screenshots or a verbal description of a problem. Use when asked to write, log, file or format a bug, defect or issue, turn notes into a Jira bug, improve an existing bug report, or decide bug severity — even phrased as just "this is broken, help me report it".
---

# Bug Report

Create a bug report that a developer can reproduce and fix without asking follow-up questions.

## Inputs

Work from whatever the user gives: rough notes, a failed test case, console or server logs, screenshots, a screen recording description, a Jira ticket or a chat message.

## Required information

Do not create the bug report until all of the following are known:

- **What goes wrong** — a one-line summary of the problem
- **Bug type** — one of:
  - **FE** (Front end) — client-side logic: wrong behavior in the browser/app, JS errors, broken validation, wrong data shown although the server response is correct
  - **BE** (Back end) — server side: wrong API response or status code, wrong data saved, server errors (5xx), business logic on the server
  - **UI** — visual/layout only: alignment, colors, fonts, typos, overlapping or cut-off elements, responsiveness
- **Steps to reproduce** — from a clear starting state, with concrete data
- **Expected result**
- **Actual result**
- **Environment** — OS, browser version (or app), device, environment (dev/staging/prod), URL, user role

If any item is missing or unclear, stop and ask the user for exactly the missing items in one short list. Do not invent, guess or fill in placeholders. Write the report only after every required item is provided.

## Process

1. **Understand the problem.** Restate in 1–2 sentences what goes wrong, where, and for whom.
2. **Check required information.** Compare the input with **Required information** above. If anything is missing, ask for it and wait — do not continue.
3. **Check it is one bug.** If the input describes several independent problems, split them into separate reports.
4. **Reconstruct the steps to reproduce.** Start from a known state (logged out, fresh page, specific account) and list the minimum actions that trigger the bug, with concrete data.
5. **Separate expected from actual.** Expected comes from the requirement, acceptance criteria or common sense — say which. Actual is only what was observed: error text, wrong value, status code, UI state.
6. **Capture the environment.** OS, browser version (or app), device, environment (dev/staging/prod), URL, user role.
7. **Assess severity** using the definitions below.
8. **Collect evidence.** Reference screenshots, videos, logs, network requests, console errors. Quote error messages exactly.
9. **Write the report** in the format from `references/bug-report-template.md`.
10. **Review** against the checklist below before presenting.
11. **Present the draft and wait for approval.** See **Approval** below.

## Writing rules

- One report describes one bug.
- Title format: `[<Bug type>] <Area/Page>: <what goes wrong> when <condition>`, where Bug type is `FE`, `BE` or `UI` — e.g. `[FE] Checkout: total not updated when coupon is removed`, `[BE] Login: API returns 500 when password contains emoji`, `[UI] Header: logo overlaps menu when window is narrower than 768px`. No vague words like "broken", "doesn't work", "issue with".
- Steps are numbered, concrete and minimal ("Enter `test@mail` in Email", not "enter invalid email").
- Expected and Actual results are specific and comparable — the same aspect, two different outcomes.
- State only observed facts. Do not add guesses about the root cause.
- Quote error messages, codes and log lines exactly, in code formatting.
- Neutral, professional tone — describe the system, never blame people.

## Severity

Severity = impact on the system / user.

| Severity | Meaning |
|----------|---------|
| Critical | Crash, data loss, security hole, core flow fully blocked, no workaround |
| Major | Important feature broken or wrong result, workaround is hard |
| Minor | Feature works with a small defect or an easy workaround |
| Trivial | Cosmetic: typo, alignment, color |

## Output

Always use the Jira format from `references/bug-report-template.md`.

See `references/examples.md` for a complete worked example.

## Approval

**Never create the bug without the user's explicit approval.**

- Always show the full draft first and ask: "Do you approve creating this bug?"
- Only an explicit "yes" / "approve" / "create it" from the user counts as approval. Silence, "looks good so far" or a request for changes is not approval.
- If the user asks for changes, update the draft, show it again and ask for approval again.
- This applies to every way of creating the bug: Jira (including through a Jira/Atlassian tool), any other issue tracker, or saving it as a file.
- One approval covers one bug only. Each new bug needs its own approval.

## Review checklist

- [ ] All required information was provided by the user — nothing invented
- [ ] Title starts with the bug type `[FE]`, `[BE]` or `[UI]` provided by the user
- [ ] Title says where, what and when — readable without opening the report
- [ ] Steps start from a clear state and reproduce the bug with no extra steps
- [ ] Expected and actual results are specific and differ on the same point
- [ ] Environment is stated
- [ ] Severity is set and justified
- [ ] Evidence is referenced; error messages are quoted exactly
- [ ] Only observed facts — no root-cause guesses
- [ ] Draft shown to the user — bug not created until the user explicitly approves
