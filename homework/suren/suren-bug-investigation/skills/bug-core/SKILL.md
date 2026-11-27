---
name: bug-core
description: Shared foundation for creating a bug in Jira. Finds which fields the Jira project requires for a Bug, fills them, and puts everything else in the description. Use before creating or updating any bug in Jira, together with the course's bug-report skill. Not for writing the report text itself (bug-report does that) or for investigating the cause (the type-specific bug skills do that).
---

# Bug Core

The shared foundation for every bug skill in this plugin. It answers two questions:
**which Jira fields does this bug need**, and **where does each piece of information go**.

The report's content and format come from `qa-bug-investigation:bug-report` (title format,
required information, severity, Jira template, approval). This skill doesn't repeat them.

## What every bug must contain

Taken from `bug-report`. A bug is not created until all of these are known:

| Information | Where it goes |
|---|---|
| Bug type: `FE`, `BE` or `UI` | Summary prefix + label |
| What goes wrong, where, when | Summary |
| Environment: OS, browser/app, device, env, URL, user role | Description → Environment |
| Preconditions | Description → Preconditions |
| Steps to reproduce, with concrete data | Description → Steps to Reproduce |
| Expected result, with its source | Description → Expected Result |
| Actual result, with exact errors | Description → Actual Result |
| Severity: Critical / Major / Minor / Trivial | Description → Severity |
| Evidence: screenshots, logs, requests | Attachment field + Description → Attachments |

## Flow: from Jira fields to a created bug

1. **Find the project and issue type.** Use the project from the ticket under test, e.g. `SCRUM`.
   The issue type is `Bug`.
2. **Ask Jira for the fields.** With the Atlassian MCP, run `getJiraIssueTypeMetaWithFields`
   (`projectIdOrKey`, `issueTypeId`, `requiredFieldsOnly: false`). Get `issueTypeId` from
   `listJiraProjectIssueTypesMetadata`. Projects differ, so never assume the fields: always check.
3. **Fill every required field.** If a required field has `allowedValues`, use one of them
   exactly. If a value is unknown, ask the user. Never guess.
4. **Fill the optional fields that exist** (see Field rules below). Skip any that the project
   doesn't have.
5. **Put everything else in the Description**, using the `bug-report` template sections in
   the same order. The MCP takes Markdown, so convert `h3.` → `###`, `#` → `1.`, `{code}` → triple backticks.
6. **Show the full draft** (fields and description) and wait for an explicit "yes", as
   `bug-report` requires.
7. **Create the bug** with `createJiraIssue`, then add the links and attachments.
8. **Report back** the new key and link, e.g. `SCRUM-48`.

## Field rules

| Field | Rule |
|---|---|
| Project | The project of the ticket under test |
| Issue Type | `Bug` |
| Summary | `[<FE/BE/UI>] <Area/Page>: <what goes wrong> when <condition>`. No vague words |
| Description | All `bug-report` template sections. Nothing invented, no `<...>` placeholders |
| Labels | The bug type in lower case (`fe`, `be`, `ui`) and the testing type (`api`, `smoke`, `uat`, `exploratory`) |
| Linked Issues | "relates to" the story or ticket under test, e.g. `SCRUM-12` |
| Attachment | Screenshots, videos, HAR or log files that the description lists |
| Priority, Assignee, Sprint, Due date | Leave empty. Triage sets them, not the tester |

## Fields in the SCRUM project (checked 2026-11-27)

| Required | Optional, useful for bugs | Not available on create |
|---|---|---|
| Project, Issue Type, Summary | Description, Labels, Linked Issues, Attachment, Parent | Severity, Priority, Environment, Components |

That's why Severity and Environment live in the description in this project. Re-check with
step 2 if the project changes.

## Rules

- One bug per issue. Split independent problems.
- Search for duplicates first: run a JQL search for the same page or area and error text.
  If a match exists, add a comment to it instead of creating a new bug.
- Only observed facts. No root-cause guesses in the bug itself.
- No real customer data, passwords or tokens in any field or attachment.
