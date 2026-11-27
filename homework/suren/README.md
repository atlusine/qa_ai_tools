# Suren: homework

My work for the *AI in QA: End to End* course. Everything in this folder is mine.
Changes I make elsewhere in the repo, such as new skills under `plugins/`, are
listed under [Contributions outside this folder](#contributions-outside-this-folder).

GitHub: [@surenarzanyan511-blip](https://github.com/surenarzanyan511-blip)

## Homework

| # | Assignment | Folder | Branch |
|---|------------|--------|--------|
| 1 | Telegram AI news bot: daily digest, CI result and PR-merged notifications, on-demand button | [`ai-news-telegram-bot/`](ai-news-telegram-bot/) | `homework/suren-telegram-ai-news` |
| 2 | QA roles plugin: tester agents built on a shared `qa-core` skill (structure only) | [`suren-qa-roles/`](suren-qa-roles/) | `homework/suren-qa-roles` |

## Contributions outside this folder

None yet.

## Conventions

- Each assignment gets its own subfolder here: `homework/suren/<assignment>/`.
- Each assignment is developed on its own branch, `homework/suren-<topic>`, and
  merged through a pull request.
- No secrets are committed. Each project has an `.env.example`; the real `.env`
  stays on my machine and is git-ignored.

## Notes on the Telegram bot

- Tests: `cd homework/suren/ai-news-telegram-bot`, then
  `pip install -r requirements-dev.txt` and `python -m pytest`
  (79 passed, 1 skipped on purpose to demo skipped-test counting). All tests use
  fixtures and mocks: no network, no Telegram.
- The workflows in `ai-news-telegram-bot/.github/workflows/` are kept for review.
  GitHub only runs workflows from the repository root, so they don't run in this
  repo. They run in the bot's own repository, where the Telegram secrets live.
