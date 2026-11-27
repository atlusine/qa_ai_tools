---
name: nightly-smoke
description: Run the nightly guest smoke of toolshop-automation (practicesoftwaretesting.com), triage every failure with the smoke-triage agent, compare with the previous run and write a short morning report in homework/narek-nightly-smoke/runs/. Use when the scheduled "nightly smoke" task fires, or when the user says "run the nightly smoke", "did last night break anything", "smoke + triage". Drafts bug reports, never files them.
---

# Nightly guest smoke + triage

Goal: one glance in the morning answers "is the app OK, and if not, is it the app, the test, or the environment?"

## Never (without the user's explicit yes in chat)
- Write to Jira (no issues, no comments), push, open PRs, send messages.
- Edit anything in `toolshop-automation/` (the shared framework; tests are not ours to "fix" at night).
- Log in, read or print `.env`, or click/automate a bot check (Cloudflare "Verify you are human").
- Re-run the suite more than once per run (shared public site; light load only).

## Steps

1. **Run** (deterministic, no AI):
   ```bash
   bash homework/narek-nightly-smoke/run-guest-smoke.sh      # from the repo root
   ```
   It prints `run_dir=…`. Everything for this run lives there: `run-info.txt`, `summary.json`, `console.log`, `results.json`, `artifacts/`.

2. **Read `summary.json`** (not `results.json`, which is big). If it has `error`, the run itself broke: read the last 30 lines of `console.log`, report "run broken", stop.

3. **Triage**: for every test whose `outcome` is `unexpected` or `flaky`, start the `smoke-triage` agent, one per test, in parallel. Give it: TC id + title, spec file:line, every attempt's `status` + `error`, the artifact paths, and the `botCheckPage` flag. Why an agent: screenshots and snapshots stay in its context, not in yours, and it has read-only tools.
   - If every failure has `botCheckPage: true` or a connection error, you may skip the agents and bucket them `blocked-environment` yourself; say so in the report.

4. **Compare with the previous run**: the newest other folder in `homework/narek-nightly-smoke/runs/` that has a `report.md`. Per TC: `new failure`, `still failing (since <date>)`, `recovered`, or `unchanged`.

5. **Bug drafts**: for each `real-bug` verdict with high/medium confidence, write `bug-draft-<TC>.md` in the run folder using the `bug-report` skill's format. **Draft only.** Before drafting, search the course Jira read-only for a duplicate (`project = SCRUM AND text ~ "<key words>"`) and mention any match.

6. **Write `report.md`** in the run folder (format below), and print it.

## report.md format

```
# Nightly guest smoke — <YYYY-MM-DD HH:MM>
Verdict: 🟢 all passed | 🟡 flaky only | 🔴 <n> real bug(s) | ⚪ blocked by environment | 🟠 test bug(s)
Ran: <n> tests, <passed> passed, <failed> failed, <flaky> flaky · <duration>s · commit <sha> · <base_url>
Not covered: TC01 customer login (bot check on the public site's login)

| TC | Test | Result | Bucket | vs last run | Next action |
|----|------|--------|--------|-------------|-------------|

## Details
<one short block per non-green test: the agent's evidence + next action>

## Needs you
<bullets: bug drafts to review, test fixes to propose to Lusine, or "nothing">
```

Verdict priority when mixed: 🔴 > 🟠 > ⚪ > 🟡 > 🟢.
Keep it short: a green night is 5 lines.
