---
name: qa-bug-report
description: Write a clear, reproducible bug report from a failed test, an observed defect, screenshots or logs. Use when asked to report a bug, log a defect, file a Jira bug or turn a failed test case into a bug.
---

# QA Bug Report

Write a bug report that a developer can reproduce without asking questions.

## Before writing

1. Reproduce the bug from a clean state and note how often it happens.
2. Find the shortest steps that trigger it.
3. Collect a screenshot, log and video.

Do not invent missing information. If something is unknown, write it under **Notes**.

## Required fields

| Field | What to write |
| --- | --- |
| **Title** | `[Area] What is wrong when condition` |
| **Description** | One line: what is broken and how it affects the user. |
| **Environment** | Server (dev / staging / prod or URL), app version, browser and OS. |
| **Priority** | High, Medium or Low (see below). |
| **Preconditions** | What must be true before step 1: user role, data, starting page. |
| **Steps to reproduce** | Numbered, one action per step, with exact test data. |
| **Expected result** | What should happen. Cite the requirement or test case if there is one. |
| **Actual result** | What actually happens. Quote error messages exactly. |
| **Reproducibility** | Always, Sometimes (e.g. 2 of 5) or Once. |
| **Attachments** | Screenshot, log (console / server), video. |
| **Notes** | Workaround, where it does not happen, open questions. |

## Priority

- **High**: core feature broken, data loss or security issue, blocks testing or release.
- **Medium**: feature works incorrectly but there is a workaround.
- **Low**: cosmetic or rare edge case.

## Rules

- One bug per report.
- Facts only, no guesses about the cause.
- Remove passwords, tokens and personal data.

## Template

```markdown
**Title:** [Area] What is wrong when condition
**Description:** ...
**Environment:** Server: ... | Version: ... | Browser/OS: ...
**Priority:** High / Medium / Low

**Preconditions:** ...

**Steps to reproduce:**
1. ...
2. ...

**Expected result:** ...
**Actual result:** ...
**Reproducibility:** Always / Sometimes (x of y) / Once
**Attachments:** screenshot, log, video
**Notes:** ...
```

## Example

**Title:** [Search] Search is ignored when term is shorter than 3 characters
**Description:** Clicking "Search" with 1–2 characters does nothing and shows no message.
**Environment:** Server: https://practicesoftwaretesting.com | Version: v2.5 | Browser/OS: Chrome, Windows 11
**Priority:** Medium

**Preconditions:** Guest user, home page opened, search field empty.

**Steps to reproduce:**
1. Enter `p` in the "Search" field.
2. Click "Search".

**Expected result:** Products containing "p" are shown with caption "Searched for: p" (TC-017).
**Actual result:** Nothing happens. The product list does not change and no message is shown.
**Reproducibility:** Always (3 of 3)
**Attachments:** TC-017.jpg, console log (no search request sent)
**Notes:** Searches with 3 or more characters work.
