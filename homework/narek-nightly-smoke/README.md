# Lesson 3 homework: nightly guest smoke + triage

Automates an everyday QA job with a **script + agent + skill + schedule**: every morning, run the
`toolshop-automation` smoke tests and answer *"is the app OK, and if not, is it the app, the
test, or the environment?"*, without anyone opening a terminal.

## How it fits together

```
schedule (08:00 daily)
  └─ skill  nightly-smoke          the procedure
       ├─ run-guest-smoke.sh       deterministic: run tests, keep evidence, write summary.json
       ├─ agent smoke-triage       one per failed test, read-only: bucket + evidence
       └─ report.md                verdict, table, diff vs last run, "Needs you"
```

| Piece | File | Why it is this kind of piece |
|---|---|---|
| Script | `run-guest-smoke.sh` | Running tests needs no judgement: a script is cheap, repeatable and testable |
| Agent | `.claude/agents/smoke-triage.md` | Triage needs judgement. Screenshots and snapshots stay in the agent's own context, and with **Read/Glob/Grep only** it can't "fix" a real bug away or file noise in Jira |
| Skill | `.claude/skills/nightly-smoke/SKILL.md` | The written procedure and the "never" list, loaded on demand |
| Schedule | `scheduled-task-prompt.md` | A self-contained prompt for a Claude desktop scheduled task (each run starts with no memory) |

## Triage buckets

| Bucket | Example | Action |
|---|---|---|
| real-bug | Wrong total, app error on screen | Draft a bug report (never filed automatically) |
| test-bug | Selector gone while the page looks fine | Propose a fix (file:line) |
| flaky | Failed, then passed on retry | Note it, watch the trend |
| **blocked-environment** | Cloudflare "Verify you are human", site down, 5xx | No bug, no fix: report "could not test" |
| inconclusive | Evidence missing or unclear | Say what a human should check |

## Why guest-only

`TC01` (customer login) currently lands on a **Cloudflare bot check** on the public site
(4 of 4 attempts on 2026-11-27, guest pages load fine). A bot check is never clicked through or
automated. The job runs the guest smoke specs only (no password, no shared account) and every
report says out loud: *"Not covered: TC01 customer login"*. To cover login, run against a local
Toolshop (`BASE_URL=http://localhost:4200 API_URL=http://localhost:8091`).

## How to run

From the repo root, after the `toolshop-automation` setup (`npm install`, `npx playwright install chromium`):

```bash
bash homework/narek-nightly-smoke/run-guest-smoke.sh
```

Forced-red check of the automation itself (should be triaged as blocked-environment):

```bash
RUN_LABEL=forced-red BASE_URL=http://localhost:9 bash homework/narek-nightly-smoke/run-guest-smoke.sh
```

Full workflow with Claude: copy `.claude/agents/smoke-triage.md` and `.claude/skills/nightly-smoke/`
into the `.claude/` folder of the project you start Claude in, then say "run the nightly smoke".
To schedule it, create a desktop scheduled task with the prompt in `scheduled-task-prompt.md`
and click **Run now** once to approve its tools.

Each run lands in `runs/<YYYY-MM-DD_HHMMSS>[_label]/` (gitignored): `run-info.txt`, `summary.json`,
`results.json`, `console.log`, `artifacts/`, `report.md`. Example: `examples/report-green.md`.

## What testing the automation taught me

- **Dry-run the automation itself, green and forced red.** It caught my own bug: two runs in the same minute wrote into the same folder and the second overwrote the first. Fixed with seconds in the folder name.
- **Evidence is fragile.** Playwright empties the shared `test-results/` at the start of every run, so a later run deleted TC01's screenshot. That's why each run gets its own `--output` folder.
- **Missing evidence makes AI guess.** Without the screenshot the agent leaned "test-bug: selector drift" for TC01, because the `/account` URL check had passed. The Cloudflare page is served *at* the requested URL, so that check proves nothing. It did rate itself low confidence. The rules for this are now in the agent.
- **New agents load only in a new session.** That's fine for a scheduled task, which always starts fresh.
