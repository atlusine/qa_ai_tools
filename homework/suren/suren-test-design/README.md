# suren-test-design

Test design and execution by testing type: one main QA skill and four testing approaches.
Each agent loads the main skill plus the skill for its approach.

```
agent  =  qa-core  +  <approach skill>
```

> **Status:** structure only. Descriptions and content are TODO.

## What's inside

| Agent | Skills it loads | Use it for |
|-------|-----------------|------------|
| `api-tester` | `qa-core` + `api-testing` | API and back-end checks: endpoints, status codes, data saved on the server |
| `smoke-tester` | `qa-core` + `smoke-testing` | A quick check that the main flows work on a new build or release |
| `uat-tester` | `qa-core` + `uat-testing` | Checking a feature against its acceptance criteria, as the user sees it |
| `exploratory-tester` | `qa-core` + `exploratory-testing` | Ad hoc, time-boxed exploring to find bugs no test case covers |

```
suren-test-design/
├── .claude-plugin/plugin.json
├── skills/
│   ├── qa-core/              main skill, shared by every agent
│   │   ├── SKILL.md
│   │   └── references/test-report-template.md
│   ├── api-testing/SKILL.md
│   ├── smoke-testing/SKILL.md
│   ├── uat-testing/SKILL.md
│   └── exploratory-testing/SKILL.md
└── agents/
    ├── api-tester.md
    ├── smoke-tester.md
    ├── uat-tester.md
    └── exploratory-tester.md
```

## Not duplicated here

These come from the course plugins, so this plugin reuses them instead of copying:

- Test case design: `qa-test-design:manual-test-cases`
- Bug reports: `qa-bug-investigation:bug-report`

## Install on this PC

```
claude plugin marketplace add C:\Users\Goya\PycharmProjects\qa_ai_tools\homework\suren
claude plugin install suren-test-design@suren-qa
```

After editing a skill: `claude plugin marketplace update suren-qa`, then restart Claude.
