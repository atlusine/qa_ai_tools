# Scheduled task prompt

Claude desktop app → Scheduled → new task. Schedule: `0 8 * * *` (daily 08:00, local time).
Replace `<REPO>` with the absolute path of your `qa_ai_tools` clone. Each run starts with no
memory, so the prompt has to say everything.

```
Work only inside <REPO>.

Read <REPO>/homework/narek-nightly-smoke/.claude/skills/nightly-smoke/SKILL.md and follow it exactly:
1. Run: bash <REPO>/homework/narek-nightly-smoke/run-guest-smoke.sh  (it prints run_dir=...)
2. Read run_dir/summary.json.
3. For every test with outcome "unexpected" or "flaky", triage it with the smoke-triage agent
   (<REPO>/homework/narek-nightly-smoke/.claude/agents/smoke-triage.md). If that agent type is not
   available, use a general-purpose agent told to read that file first and use only Read, Glob and
   Grep. One agent per failed test.
4. Compare with the previous run folder that has a report.md.
5. Only for high/medium-confidence real-bug verdicts: write bug-draft-<TC>.md in the run folder
   (draft only).
6. Write run_dir/report.md in the skill's format and end with its Verdict line and "Needs you".

Hard limits: no Jira writes, no git commits/pushes, no PRs, no messages; never edit anything under
toolshop-automation/; never read or print .env; never log in; never click or automate a
Cloudflare / "Verify you are human" check; run the suite once only.
```
