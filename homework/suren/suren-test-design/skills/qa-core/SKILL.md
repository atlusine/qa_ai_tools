---
name: qa-core
description: Shared QA foundation that every tester agent in this plugin applies before its testing type (API, smoke, UAT, exploratory). Defines the testing workflow, how to prioritise by risk, execution statuses, evidence rules, test data rules, defect handoff and the test report format. Use whenever a feature, ticket or build is being tested or a test result is being reported. Not for writing test cases (use qa-test-design:manual-test-cases) or writing bug reports (use qa-bug-investigation:bug-report).
---

# QA Core

How a QA engineer works, whatever the testing type. Each tester agent loads this skill
**and** one testing-type skill. This one says *how we work*; the type skill says *what is
special about that kind of testing*.

## Principles

- **Evidence over opinion.** A result is a screenshot, a response, a log line or a value, not "looks fine".
- **Test by risk.** Spend time where a failure would hurt most: money, data, security, the main user flows.
- **Nothing invented.** No made-up requirements, data, selectors or results. If something is unknown, ask or list it as an open question.
- **Check AI work.** What Claude finds in the browser or writes is a draft until it is run and checked.
- **Test data only.** Test sites and test accounts. Never real customer data.

## Workflow

| # | Step | Output |
|---|------|--------|
| 1 | **Understand**: read the ticket, acceptance criteria, linked issues and comments. Restate the feature in 2–4 bullets | Scope: in / out |
| 2 | **Plan**: choose the testing type(s), environment, accounts and data. Decide what is *not* tested and why | A short test plan |
| 3 | **Design**: write test cases with `qa-test-design:manual-test-cases` | Test cases + traceability matrix |
| 4 | **Execute**: run each case, record a status and evidence | Results per case |
| 5 | **Report defects**: hand each failure to `suren-bug-investigation:bug-core` | Bugs, created only after approval |
| 6 | **Report results**: summarise with `references/test-report-template.md` | Test report |

Skip step 3 when the cases already exist (e.g. a Jira comment). Never skip step 6.

## Inputs to collect before testing

- Ticket key and acceptance criteria (Jira, via the Atlassian MCP)
- Environment and URL, e.g. `https://practicesoftwaretesting.com` or the with-bugs version
- Build or version, if known
- User roles and test accounts (password from `.env` or the user, never written into files)
- Test data that has to exist before step 1 (products, cart state, orders)

If any of these change the result and is missing, ask once in a short list.

## Prioritising by risk

| Priority | When | Run |
|---|---|---|
| High | Core flow, money, data loss, security, a reported customer problem | First, always |
| Medium | Alternative flows, validation, error messages | When High passes |
| Low | Cosmetic, rare edge cases | When time allows |

These match the priorities in `manual-test-cases`.

## Execution statuses

| Status | Meaning |
|---|---|
| **Passed** | Actual result matches the expected result, with evidence |
| **Failed** | Actual differs from expected. A defect is reported or linked |
| **Blocked** | Can't run: environment down, missing data or access, or blocked by another defect (name it) |
| **Not run** | Not executed in this cycle. Give the reason |

Never mark a case Passed without having observed the result.

## Evidence

- A screenshot of the final state for each Failed case, and for each key Passed case
- Exact error text, quoted in a code block
- API calls: method, URL, status code, response body. Remove tokens and passwords
- Browser console errors, when relevant
- Name files so they can be found: `<ticket>-<case>-<what>.png`, e.g. `SCRUM-12-TC-006-toast.png`

## Tools

| Need | Tool | Rule |
|---|---|---|
| Ticket, acceptance criteria, comments | Atlassian MCP | Read freely. **Write (comment, bug, transition) only after the user's explicit "yes"** |
| Explore or run a flow in the browser | Playwright MCP | Results can vary between runs. Repeat a failure before reporting it |
| A test that has to run every time | Playwright tests in the repo | Explore with MCP, keep a real test |

## Defect handoff

When a case fails:
1. Repeat it once to confirm it is not a one-off.
2. Hand it to `suren-bug-investigation:bug-core` with the case ID, steps, expected and actual results, and the evidence.
3. Mark the case **Failed** and link the bug key in the report.

Severity, the title format and approval are defined in `qa-bug-investigation:bug-report`. Don't redefine them here.

## Reporting

Every testing session ends with a report in the format of `references/test-report-template.md`.
Keep it short: someone should understand the state of the feature in one minute.

## Rules for every testing type

- One case checks one thing. Concrete data in every step.
- Stay in scope. Note new findings outside scope as open questions, don't test them silently.
- State every assumption.
- Don't change data other testers depend on (shared demo accounts, shared products).
- Report what was **not** tested, not only what was.
