"""Send a Telegram message when a pull request is merged into the default branch.

Reads the event payload JSON that GitHub Actions writes to $GITHUB_EVENT_PATH. Event data
(PR title, branch names, user names) is only ever read here as data and sent as plain text.
It is never interpolated into a shell command.

    python -m notifier.github_events [--preview] [--event-file path/to/event.json]

Events that are not "merged into the default branch" (e.g. closed without merging) are
logged and skipped with exit code 0.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from typing import Any

from notifier.config import ensure_utf8_output, load_dotenv
from notifier.telegram import EXIT_CONFIG_ERROR, deliver

log = logging.getLogger("notifier.github_events")


def build_pr_merged_message(event: dict[str, Any]) -> tuple[str | None, str]:
    """Return (message, reason). message is None when nothing should be sent."""
    pr = event.get("pull_request")
    if not isinstance(pr, dict):
        return None, "event is not a pull_request event"
    number = pr.get("number", "?")
    if event.get("action") != "closed":
        return None, f"PR #{number}: action is '{event.get('action')}', not 'closed'"
    if not pr.get("merged"):
        return None, f"PR #{number} was closed without merging"

    repo = event.get("repository") or {}
    default_branch = repo.get("default_branch")
    base = (pr.get("base") or {}).get("ref", "")
    if default_branch and base != default_branch:
        return None, f"PR #{number} was merged into '{base}', not the default branch '{default_branch}'"

    merged_by = (pr.get("merged_by") or {}).get("login") or "unknown"
    author = (pr.get("user") or {}).get("login")
    head = (pr.get("head") or {}).get("ref")
    lines = [
        f"🔀 PR merged into {base or 'default branch'}",
        "",
        f"#{number}: {pr.get('title') or '(no title)'}",
        f"Merged by: {merged_by}",
    ]
    if author and author != merged_by:
        lines.append(f"Author: {author}")
    if head:
        lines.append(f"Branch: {head} → {base}")
    lines.append(f"Repository: {repo.get('full_name', 'n/a')}")
    lines.append(f"Link: {pr.get('html_url', 'n/a')}")
    return "\n".join(lines), f"PR #{number} merged into {base}"


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_output()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(prog="python -m notifier.github_events")
    parser.add_argument("--event-file", default=os.environ.get("GITHUB_EVENT_PATH"),
                        help="event JSON (default: $GITHUB_EVENT_PATH)")
    parser.add_argument("--preview", action="store_true", help="print the message instead of sending it")
    args = parser.parse_args(argv)
    if not args.event_file:
        log.error("No event file: pass --event-file or run inside GitHub Actions (GITHUB_EVENT_PATH)")
        return EXIT_CONFIG_ERROR
    try:
        with open(args.event_file, encoding="utf-8") as fh:
            event = json.load(fh)
    except (OSError, ValueError) as exc:
        log.error("Could not read event file: %s", exc)
        return EXIT_CONFIG_ERROR

    message, reason = build_pr_merged_message(event)
    if message is None:
        log.info("Skipping notification: %s", reason)
        return 0
    load_dotenv()
    log.info("Notifying: %s", reason)
    return deliver(message, args.preview)


if __name__ == "__main__":
    sys.exit(main())
