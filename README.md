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
│   ├── qa-bug-investigation/         # Lesson 3 (later)
│   └── qa-automation/                # Lessons 4–5: skills + agents/
└── README.md
```

## Plugins

| Plugin | Status | What it does |
|--------|--------|--------------|
| `qa-test-design` | ✅ Ready | `manual-test-cases` skill: designs manual test cases from requirements using EP, BVA, decision tables and state transitions, with a traceability matrix |
| `qa-bug-investigation` | 🚧 Lesson 3 | Bug investigation and reporting |
| `qa-automation` | 🚧 Lessons 4–5 | Test automation skills and agents |

Only finished plugins are listed in `marketplace.json`. Add a plugin there when it has content.

## Install

From a local clone:

```
/plugin marketplace add /path/to/qa_ai_tools
/plugin install qa-test-design@qa-ai-tools
```

From a Git remote:

```
/plugin marketplace add <git-url-or-owner/repo>
/plugin install qa-test-design@qa-ai-tools
```

## Usage

Ask Claude something like:

- "Write test cases for this user story: …"
- "What should I test for JIRA-123?"
- "Give me test cases for the login form as CSV for TestRail"

## Adding a plugin

1. Create `plugins/<name>/.claude-plugin/plugin.json`.
2. Add skills under `plugins/<name>/skills/<skill>/SKILL.md` and agents under `plugins/<name>/agents/<agent>.md`.
3. Register it in `.claude-plugin/marketplace.json`.
4. Validate: `claude plugin validate .`
