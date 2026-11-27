# qa-ai-tools

A Claude Code plugin marketplace with QA workflow plugins.

## Structure

```
qa-ai-tools/
├── .claude-plugin/
│   └── marketplace.json              # catalog of all plugins
├── plugins/
│   ├── qa-test-design/               # Lesson 2
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/
│   │       └── manual-test-cases/
│   │           ├── SKILL.md
│   │           └── references/       # templates, techniques, examples
│   ├── qa-bug-investigation/         # Lesson 3
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/
│   │       └── bug-report/
│   │           ├── SKILL.md
│   │           └── references/       # Jira template, worked example
│   └── qa-automation/                # Lessons 4–5: skills + agents/
├── toolshop-automation/              # Playwright E2E framework for practicesoftwaretesting.com
│   ├── CLAUDE.md                     # routes to rules / skills / commands / agents
│   ├── .claude/                      # settings.json (hooks + permissions), rules, skills, commands, agents
│   ├── scripts/claude-hooks/         # session-context · validate-edit · lint-before-commit · review-diff
│   ├── tests/{smoke,regression}/     # 10 test cases (TC01–TC10)
│   ├── module_object/  flows/  support/
│   └── playwright.config.js
└── README.md
```

## Plugins

| Plugin | Status | What it does |
|--------|--------|--------------|
| `qa-test-design` | ✅ Ready | `manual-test-cases` skill: designs manual test cases from requirements using EP, BVA, decision tables and state transitions, with a traceability matrix |
| `qa-bug-investigation` | ✅ Ready | `bug-report` skill: writes reproducible bug reports in Jira format with an `[FE]`/`[BE]`/`[UI]` title prefix and severity; asks for missing required information and creates the bug only after explicit approval |
| `qa-automation` | 🚧 Lessons 4–5 | Test automation skills and agents |

Only finished plugins are listed in `marketplace.json`. Add a plugin there when it has content.

## Install

Students: follow the full [Student Setup Guide](STUDENT_SETUP.md) (Node.js, Claude Code, plugins, Playwright, Jira).

From a local clone:

```
/plugin marketplace add /path/to/qa_ai_tools
/plugin install qa-test-design@qa-ai-tools
/plugin install qa-bug-investigation@qa-ai-tools
```

From a Git remote:

```
/plugin marketplace add <git-url-or-owner/repo>
/plugin install qa-test-design@qa-ai-tools
/plugin install qa-bug-investigation@qa-ai-tools
```

## Usage

Ask Claude something like:

- "Write test cases for this user story: …"
- "What should I test for JIRA-123?"
- "Give me test cases for the login form as CSV for TestRail"
- "Write a bug report: the total stays discounted after I remove the coupon"
- "Turn these notes into a Jira bug: …"

## Automation framework (`toolshop-automation/`)

A Playwright (JavaScript) test suite for the course's practice app, with its own Claude Code setup. Start Claude **inside** the folder so its `CLAUDE.md`, hooks, and permissions load:

```bash
cd toolshop-automation
npm install && npx playwright install chromium && cp .env.example .env   # then set USER_PASSWORD in .env
npx playwright test            # or: npx playwright test --grep @smoke
claude                         # then: /generate-test, /investigate-failure, /test-review
```

## Adding a plugin

1. Create `plugins/<name>/.claude-plugin/plugin.json`.
2. Add skills under `plugins/<name>/skills/<skill>/SKILL.md` and agents under `plugins/<name>/agents/<agent>.md`.
3. Register it in `.claude-plugin/marketplace.json`.
4. Validate: `claude plugin validate .`
