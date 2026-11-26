"""Configuration helpers shared by every notifier entry point."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

TOKEN_VAR = "TELEGRAM_BOT_TOKEN"
CHAT_ID_VAR = "TELEGRAM_CHAT_ID"


class ConfigError(Exception):
    """Required configuration is missing or invalid. Never contains secret values."""


def load_dotenv(path: str | os.PathLike = ".env") -> None:
    """Load KEY=VALUE pairs from a local .env file.

    Real environment variables always win, so GitHub Actions secrets are never
    overridden by a stray file. Missing file is not an error.
    """
    p = Path(path)
    if not p.is_file():
        return
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key:
            os.environ.setdefault(key, value)


def _is_set(value: str) -> bool:
    # Treat the .env.example placeholders ("<your-bot-token>") as unset.
    return bool(value) and not (value.startswith("<") and value.endswith(">"))


@dataclass(frozen=True)
class TelegramConfig:
    token: str = field(repr=False)  # repr=False keeps the token out of logs/tracebacks
    chat_id: str


def get_telegram_config(env: Mapping[str, str] | None = None) -> TelegramConfig:
    env = os.environ if env is None else env
    token = env.get(TOKEN_VAR, "").strip()
    chat_id = env.get(CHAT_ID_VAR, "").strip()
    missing = [name for name, value in ((TOKEN_VAR, token), (CHAT_ID_VAR, chat_id)) if not _is_set(value)]
    if missing:
        raise ConfigError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Set them in a local .env file (see .env.example) or as GitHub Actions secrets."
        )
    return TelegramConfig(token=token, chat_id=chat_id)


def get_bot_token(env: Mapping[str, str] | None = None) -> str:
    """Token only: the interactive bot replies to whichever chat wrote to it, so no chat ID is needed."""
    env = os.environ if env is None else env
    token = env.get(TOKEN_VAR, "").strip()
    if not _is_set(token):
        raise ConfigError(
            f"Missing required environment variable: {TOKEN_VAR}. "
            "Set it in a local .env file (see .env.example)."
        )
    return token


def ensure_utf8_output() -> None:
    """Avoid UnicodeEncodeError when printing emoji to a Windows console or pipe."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass
