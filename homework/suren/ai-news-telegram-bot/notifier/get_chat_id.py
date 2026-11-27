"""Print the chat IDs that have recently messaged your bot.

1. Put TELEGRAM_BOT_TOKEN in your local .env file (never on the command line).
2. Open your bot in Telegram, press Start and send it any message.
3. Run:  python -m notifier.get_chat_id
4. Copy the printed chat ID into TELEGRAM_CHAT_ID.

The token is never printed. Only chat IDs and chat names are shown.
"""
from __future__ import annotations

import os
import sys

from notifier.config import TOKEN_VAR, TelegramConfig, ensure_utf8_output, load_dotenv
from notifier.telegram import TelegramError, call_api


def main() -> int:
    ensure_utf8_output()
    load_dotenv()
    token = os.environ.get(TOKEN_VAR, "").strip()
    if not token or token.startswith("<"):
        print(f"{TOKEN_VAR} is not set. Add it to your .env file (see .env.example).", file=sys.stderr)
        return 3
    try:
        body = call_api(TelegramConfig(token=token, chat_id=""), "getUpdates", {"limit": 50})
    except TelegramError as exc:
        print(f"Could not read updates: {exc}", file=sys.stderr)
        return 1

    chats: dict[int, str] = {}
    for update in body.get("result", []):
        message = update.get("message") or update.get("channel_post") or update.get("my_chat_member") or {}
        chat = message.get("chat") or {}
        if "id" in chat:
            name = chat.get("title") or " ".join(filter(None, [chat.get("first_name"), chat.get("last_name")])) or chat.get("username", "")
            chats[chat["id"]] = f"{chat.get('type', '?')}: {name}"
    if not chats:
        print("No chats found. Open your bot in Telegram, press Start, send it a message, then run this again.")
        return 0
    print("Chats that recently messaged the bot:")
    for chat_id, label in chats.items():
        print(f"  TELEGRAM_CHAT_ID={chat_id}   ({label})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
