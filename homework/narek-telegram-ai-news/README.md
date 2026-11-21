# Telegram bot: daily AI news

Homework, practice task 04. A small script that reads AI news RSS feeds,
picks the 5 newest stories and sends them to a Telegram chat.

Python 3 standard library only, nothing to install.

## Setup

1. In Telegram, open @BotFather, send `/newbot` and copy the bot token.
2. Copy `.env.example` to `.env` and paste the token after `TELEGRAM_BOT_TOKEN=`.
   `.env` is in `.gitignore`. Never commit it.
3. Send your bot any message, then run:
   ```bash
   python3 ai_news_bot.py --get-chat-id
   ```
   Put the number in `.env` after `TELEGRAM_CHAT_ID=`.

## Run

```bash
python3 ai_news_bot.py --dry-run   # print the message, send nothing
python3 ai_news_bot.py             # send to Telegram
```

## Schedule daily (cron, macOS/Linux)

`crontab -e`, then add (every day at 09:00):

```
0 9 * * * cd /path/to/narek-telegram-ai-news && /usr/bin/python3 ai_news_bot.py >> bot.log 2>&1
```

Cron only runs while the computer is awake. For a cloud schedule, use a
scheduled GitHub Action with the token and chat ID stored as repo secrets.

## QA notes

- **Dry run first**: check the output without side effects (no message sent).
- **Test the scheduler, not just the script**: a one-off cron entry with
  `--dry-run` proved cron can run it (paths, environment).
- **One broken feed doesn't stop the run**: a failing feed (e.g. HTTP 429)
  is logged as a warning and the other feeds are still used.
- **Secrets stay out of logs**: Telegram errors never print the request URL,
  because it contains the token.
