---
name: bug-report
description: Write a clear, reproducible bug report with screenshots from a failed test case, a tester's notes, a user complaint, a screenshot, console/network logs or a reproduction run. Use when asked to report, log, file, write up or describe a bug or defect, to turn a failed test into a Jira issue, or to review and improve an existing bug report — even phrased as just "this doesn't work, write it up".
---

# Bug Report

Turn an observed problem into a bug report, with screenshots, that a developer can reproduce and fix without asking follow-up questions.

## Inputs

Work from whatever the user gives: a failed test case (ID, steps, expected result), free-text notes, screenshots, console errors, a HAR or network log, a reproduction run by the `bug-reproducer` agent, or an existing ticket to improve. If something that changes the report is missing (environment, build/version, exact data, whether it reproduces every time), list it under **Open questions** instead of guessing — do not block on it.

## Process

1. **Confirm it is a bug.** Compare the actual result with a source of truth: requirement, acceptance criterion, test case expected result, or established product behaviour. If there is no source of truth, report it as a *suspected* bug and say so in **Open questions**.
2. **Gather facts.** Environment (URL, build/version, browser + version, OS, device, user role), exact test data, timestamp, console errors and failed network requests (method, URL, status, response body excerpt).
3. **Capture screenshots.** Every report has at least one screenshot of the **actual result**. See **Screenshots** below.
4. **Minimise the steps.** Keep only the steps needed to trigger the bug, starting from a clearly stated precondition. Note whether it is reproducible **Always / Intermittently (x of y) / Once**.
5. **Isolate the scope.** Where cheap, check one or two variations (other browser, other role, other data, guest vs logged-in) and record which ones do and do not reproduce. Do not invent results for variations you did not try.
6. **Check for duplicates** when a tracker is available (e.g. Jira search on key words from the title). Link related issues instead of filing a duplicate.
7. **Set the priority** using `references/priority.md`.
8. **Write the report** in the format from `references/bug-report-template.md`.
9. **Review** against the checklist below before presenting.

## Screenshots

- **Required:** one screenshot of the actual (wrong) result, taken right after the last step.
- **Add when useful:** the state just before the failing action (e.g. input filled in), and the expected behaviour for comparison if it can be shown (e.g. the same search with a term that works).
- **How to capture:** if a browser tool such as Playwright is available, reproduce the steps and take the screenshots yourself (viewport by default, full page only when the problem is off-screen). Otherwise ask the user to attach them and list the exact screenshots needed.
- **Naming:** `<bug-area>-<nn>-<what-it-shows>.png`, e.g. `search-01-term-entered.png`, `search-02-results-unchanged.png`. Save them next to the report (or in the folder the user names) and reference them by file name.
- **In the report:** list each screenshot under **Screenshots** with a one-line caption saying what it shows and which step it belongs to. In Jira, attach the files to the issue — never link local paths.
- **Mask sensitive data** (passwords, tokens, emails, personal data) before sharing.
- If a screenshot could not be taken, say so explicitly under **Open questions** — never claim one exists.

## Writing rules

- **Title:** `[Area] <what goes wrong> when <condition>` — specific enough to find in search. Not "Search broken".
- **One bug per report.** If two different failures appear, write two reports and link them.
- **Steps** are numbered, concrete actions with concrete data ("Enter `pl` in Search"), starting from the precondition.
- **Expected** cites its source (AC-02, TC-017, spec section). **Actual** describes only what was observed — no guesses about the cause.
- **Facts vs. hypotheses:** a suspected root cause goes in **Notes**, labelled as a hypothesis.
- **Logs** are quoted verbatim in code blocks, trimmed to the relevant lines.
- Neutral tone — describe the system's behaviour, never blame people.

## Output

Default to the Markdown template. If the user asks for Jira, use the Jira layout from `references/bug-report-template.md`; if a Jira connector is available and the user asks to file it, confirm the project and issue type before creating the issue.

End with:
- **Open questions / assumptions**
- **Related items** — linked test cases, requirements and existing issues

See `references/examples.md` for a complete worked example.

## Review checklist

- [ ] Title states the symptom and the condition
- [ ] Someone who was not there can reproduce it from the preconditions and steps alone
- [ ] Expected result cites a source of truth
- [ ] Actual result is observed fact, not interpretation
- [ ] At least one screenshot of the actual result, captioned and linked to a step
- [ ] Environment and reproducibility rate are stated
- [ ] Sensitive data is masked in steps, logs and screenshots
- [ ] Priority follows the guide and is justified in one line
- [ ] Only one bug is described; related issues are linked
