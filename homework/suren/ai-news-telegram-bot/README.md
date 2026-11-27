# AI News Telegram Bot

A daily digest of up to five recent AI news stories sent to Telegram, plus a reusable
Telegram notifier for CI test results and GitHub events. Built for the ACA course
*AI in QA: End to End*, assignment 1. The scheduled parts run on GitHub Actions, so no server needs to stay online. The optional
on-demand button bot runs on your own PC.

| Part | What it does | Entry point | Workflow |
|---|---|---|---|
| Phase 1 | Daily AI news digest | `python -m news_digest` | `daily-digest.yml` |
| Phase 2 | Test / pipeline result notifications | `python -m notifier.ci_summary` | `ci-notify-demo.yml` |
| Phase 3 | "Pull request merged" notifications | `python -m notifier.github_events` | `pr-merged-notify.yml` |
| Shared | Send any text to Telegram | `python -m notifier.telegram` | n/a |
| On demand | "Get AI news digest" button in Telegram | `python -m bot` | n/a (runs on your PC) |

## Local setup

Requires Python 3.10+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest                      # all tests use fixtures and mocks; no network, no Telegram
```

## Preview mode (no Telegram needed)

```powershell
python -m news_digest --preview
```

Preview mode fetches the feeds and prints the exact message that would be sent. It doesn't
read the Telegram variables and never contacts Telegram.

## How the digest works

* **Feeds:** listed in [`feeds.txt`](feeds.txt) as `Display name | URL`, one per line. To
  override the list without editing the file, set `RSS_FEEDS` (entries separated by
  newlines or `;`).
* **Time window:** a story is eligible if it was published within the last **24 hours**
  before the run (`DIGEST_WINDOW_HOURS` or `--window-hours`). Undated entries are ignored,
  and so are entries dated more than 1 hour in the future (broken feed clocks).
* **Duplicates:** two stories count as the same if their links match after normalization
  (`www.`, `http`/`https`, trailing slash, `#fragment` and tracking parameters such as
  `utm_*` and `fbclid` are ignored), or if their titles match ignoring case and punctuation.
  The newest copy is kept.
* **Selection:** newest first, at most **5** stories (`DIGEST_MAX_STORIES` or `--max-stories`).
* **Message:** plain text (no Markdown or HTML parsing) with each story's title, source,
  publication time (UTC) and link.

| Situation | Behaviour | Exit code |
|---|---|---|
| Some feeds fail | Logged as a warning; the digest uses the remaining feeds, and the footer says how many were unavailable | 0 |
| **All** feeds fail | `ERROR ... All N feeds failed; no digest was produced` with the reasons; nothing is sent | 2 |
| Feeds work, but nothing is recent | `INFO ... No stories published in the last 24h ...; skipping send.`; nothing is sent | 0 |
| Telegram rejects or can't be reached | Error logged with the token redacted | 1 |
| Telegram variables missing | Error naming the missing variable(s) | 3 |

## Telegram configuration

### 1. Create the Telegram bot
1. In Telegram, open **@BotFather** (check for the blue verified badge) and send `/newbot`.
2. Choose a display name and a username ending in `bot`.
3. BotFather replies with an **HTTP API token**. Treat it like a password. Never commit it,
   never paste it into a terminal command, issue or chat, and never put it in a screenshot.
   If it leaks, send `/revoke` to BotFather to get a new one.

### 2. Start a chat with the bot
Open `t.me/<your_bot_username>`, press **Start** and send any message, such as "hi". A bot
can't message you until you have done this. To send the digest to a group instead, add
the bot to the group and send a message there.

### 3. Store the token locally
```powershell
Copy-Item .env.example .env      # macOS/Linux: cp .env.example .env
```
Open `.env` in your editor and replace `<your-bot-token>`. `.env` is git-ignored, and real
environment variables always take priority over it.

### 4. Find your chat ID
```powershell
python -m notifier.get_chat_id
```
This reads the token from `.env`, asks Telegram for the bot's recent messages, and prints
lines like `TELEGRAM_CHAT_ID=123456789 (private: Your Name)`. It never prints the token.
Put that value in `.env`. Group chat IDs are negative numbers.

### 5. Send a real digest locally (optional)
```powershell
python -m news_digest
```

## GitHub Actions

### Secrets
In the repository, go to **Settings → Secrets and variables → Actions → New repository
secret** and add:

| Name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | the token from BotFather |
| `TELEGRAM_CHAT_ID` | the ID from `python -m notifier.get_chat_id` |

Workflows pass these to the scripts as environment variables only. GitHub masks secret
values in logs, and the scripts also remove the token from any error they print.

### Daily digest: [`daily-digest.yml`](.github/workflows/daily-digest.yml)
* **Schedule:** `cron: "0 5 * * *"`, which is **09:00 in Yerevan**. GitHub cron runs in
  UTC, and Asia/Yerevan is UTC+4 all year with no daylight saving.
* **Changing the time:** UTC hour = Yerevan hour − 4 (wrapping around midnight). Examples:
  08:30 Yerevan → `"30 4 * * *"`; 21:00 Yerevan → `"0 17 * * *"`; weekdays only at 09:00 →
  `"0 5 * * 1-5"`. Scheduled runs can start several minutes late, run only from the
  **default branch**, and are paused automatically after 60 days without repository activity.
* **Manual run:** **Actions → Daily AI news digest → Run workflow**. Tick **Preview only**
  to print the digest in the job log without sending it.

### Test result notifications (demo): [`ci-notify-demo.yml`](.github/workflows/ci-notify-demo.yml)
Go to **Actions → CI tests with Telegram summary (demo) → Run workflow** and pick a scenario:

| Scenario | What happens | Message |
|---|---|---|
| `success` | The real pytest suite runs and passes | `[DEMO] ✅ Tests passed` with counts |
| `test_failure` | A demo test fails one assertion on purpose | `[DEMO] ❌ Tests failed` with counts and the failed test names |
| `pipeline_failure` | The setup step fails before pytest starts | `[DEMO] 🛠 Pipeline failure: tests did not run` |

The workflow has two jobs:

1. **`tests`** installs dependencies, runs `pytest --junitxml=reports/junit.xml`, and
   uploads the report. **It has no Telegram secrets.** It exports the outcomes of its
   setup step and its test step.
2. **`notify`** (`needs: tests`, `if: always()`) downloads the report if one exists and runs
   `python -m notifier.ci_summary`. It checks out only this repository's notifier and never
   runs the code under test.

How the summary decides what happened:

* The **tests step ran**, and the report contains failures or errors → **Tests failed**. Up
  to 5 failed test names are listed.
* The **tests step failed but there is no readable report** → **Tests failed**, with the
  explicit note "No test report found; counts unavailable" (for example a crash or a
  collection error).
* The **setup step failed**, or the **job never started** → **Pipeline failure: tests did not
  run**, with no counts.
* Every message includes the repository, workflow, suite / job, branch, result, counts or a
  "missing report" note, and the run link.

**The run's outcome stays intact.** The red/green status of the run comes from the `tests`
job. The Telegram step has `continue-on-error: true`, so if Telegram fails, the run's status
doesn't change. The failure appears as a `Telegram delivery failed` warning annotation and
an error line in the `notify` log, with the token redacted.

### Merged pull request notifications: [`pr-merged-notify.yml`](.github/workflows/pr-merged-notify.yml)
This runs on `pull_request_target: closed`. The job runs only when the PR was **merged** and
its base is the **default branch**. A PR closed without merging skips the job, and the script
checks the same conditions again. The message includes the PR number and title, who merged
it, the author, the branch and the link.

Security design:

* `pull_request_target` uses the workflow and code from the default branch, so the job that
  holds secrets runs only reviewed code. The checkout has **no `ref:`**, so the PR's own
  code is never checked out or executed.
* The PR title, branch names and user names are read by Python from `$GITHUB_EVENT_PATH` and
  sent as **plain text**. None of them appear in `${{ }}` expressions inside `run:` scripts.
  `tests/test_workflows.py` enforces this for every workflow.
* All workflows use `permissions: contents: read` and `persist-credentials: false`.

## On-demand digest button (`python -m bot`)

Anyone who opens the bot in Telegram and presses **/start** gets a persistent
**📰 Get AI news digest** button. Pressing it (or sending `/digest`) sends the current digest
to that person's chat. It uses the same feeds and settings as the daily digest.

```powershell
python -m bot          # needs only TELEGRAM_BOT_TOKEN in .env; Ctrl+C to stop
```

* **Where it runs:** on this PC. A button press is an incoming message, so something must be
  online to receive it, and GitHub Actions can't stay online. The bot uses long polling, so
  no public URL, open port or router setup is needed. The scheduled daily digest still runs on
  GitHub Actions whether or not this PC is on.
* **Start automatically at Windows logon** (hidden, restarted if it crashes, logs in `bot.log`):
  `.\scripts\install-autostart.ps1`. To remove it: `.\scripts\install-autostart.ps1 -Uninstall`.
* **Limits:** one digest is built at most every 10 minutes and shared by everyone who asks
  in that time. Each chat can ask once every 30 seconds. Presses older than 10 minutes, sent
  while the bot was offline, are ignored rather than answered late.
* Run only **one** copy at a time. A second copy makes Telegram return `409 Conflict`.
* `python -m notifier.get_chat_id` reads the same message queue, so stop the bot before using it.

## Reusing the notifier in another repository (for example, a QA repo)

Files to copy:
```
notifier/            # stdlib only: telegram.py, config.py, ci_summary.py, github_events.py, get_chat_id.py
```
Secrets to add in the new repo: `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` (the same bot
can serve many repos).

Sending any text from a script or workflow step:
```yaml
- name: Notify
  continue-on-error: true
  env:
    TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
  run: python -m notifier.telegram --file message.txt     # or --text "...", or pipe via stdin
```
or from Python: `from notifier.telegram import send_message; send_message("text")`.

## Connecting a real test suite

1. In your test job, give the setup / install step `id: setup` and the test step `id: tests`,
   and expose them as outputs:
   ```yaml
   outputs:
     setup_outcome: ${{ steps.setup.outcome }}
     tests_outcome: ${{ steps.tests.outcome }}
   ```
2. Make the test runner write a **JUnit XML** report and upload it with
   `actions/upload-artifact` (`if: always()`). Most runners can do this:

   | Runner | Option |
   |---|---|
   | pytest | `--junitxml=reports/junit.xml` |
   | Jest | `jest-junit` reporter |
   | Playwright | `--reporter=junit` |
   | Maven / Gradle | Surefire / test task XML reports |
   | Postman / Newman | `-r junit` |

   Without a report, messages still say pass or fail and note that counts are unavailable.
3. Copy the `notify` job from `ci-notify-demo.yml`. Point `needs:` at your test job, set
   `CI_SUITE` and `CI_JOB`, and **remove `CI_DEMO` and `CI_SCENARIO`** so messages aren't
   labelled as a demo.
4. If the workflow also runs on `pull_request` from forks, secrets aren't available there, so
   the notify step only logs a configuration error. That's expected, and the test results
   are unaffected.

## Project layout

```
news_digest/          Phase 1: feeds.py (fetch/parse), digest.py (dedupe/select/format), build.py (shared pipeline), __main__.py (CLI)
bot/                  On-demand digest bot: app.py (button, cache, cooldown, polling), __main__.py (CLI)
scripts/              install-autostart.ps1 (Windows logon task for the bot)
notifier/             Shared Telegram delivery and the CI / GitHub event message builders
feeds.txt             Feed list
.github/workflows/    daily-digest.yml, ci-notify-demo.yml, pr-merged-notify.yml
tests/                pytest suite: fixtures/ holds RSS, Atom, JUnit and event JSON samples; demo/ holds the demo-only tests
```

## Exit codes (all CLIs)

`0` success, previewed, or intentionally skipped · `1` Telegram delivery error · `2` all
feeds failed (digest only) · `3` configuration error (missing variables, missing event file).
