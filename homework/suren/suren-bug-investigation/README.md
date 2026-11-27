# suren-bug-investigation

Bug investigation by testing type, on a shared `bug-core` skill.

```
bug skill  =  bug-core  +  <type>-bug-investigation
```

> **Status:** `bug-core` has content. The type skills are structure only (TODO).

## Skills

| Skill | What it does |
|---|---|
| `bug-core` | Asks Jira which fields a Bug needs, fills them, puts the rest in the description, and creates the bug after approval |
| `api-bug-investigation` | API bugs: requests, responses, status codes |
| `smoke-bug-investigation` | Bugs that block a main flow on a new build |
| `uat-bug-investigation` | Bugs against acceptance criteria |
| `exploratory-bug-investigation` | Bugs found while exploring, from session notes |

## How it fits with the course plugin

The report text (title format, required information, severity, approval) comes from
`qa-bug-investigation:bug-report`. This plugin adds the Jira field flow and the
type-specific investigation, so nothing is copied.

## Jira fields (SCRUM project, checked 2026-11-27)

- **Required:** Project, Issue Type, Summary
- **Optional and used:** Description, Labels, Linked Issues, Attachment
- **Not available:** Severity, Priority, Environment, so they go in the description

## Install on this PC

```
claude plugin marketplace add C:\Users\Goya\PycharmProjects\qa_ai_tools\homework\suren
claude plugin install suren-bug-investigation@suren-qa
```

After editing a skill: `claude plugin marketplace update suren-qa`, then restart Claude.
