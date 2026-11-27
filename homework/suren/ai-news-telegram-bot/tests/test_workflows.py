"""Static checks on the GitHub Actions workflows: triggers, permissions and secret hygiene."""
from pathlib import Path

import pytest
import yaml

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"


def load(name):
    data = yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))
    # PyYAML (YAML 1.1) parses the key `on:` as boolean True.
    data["on"] = data.pop(True, data.get("on"))
    return data


def all_steps(wf):
    for job in wf["jobs"].values():
        yield from job.get("steps", [])


@pytest.mark.parametrize("name", ["daily-digest.yml", "ci-notify-demo.yml", "pr-merged-notify.yml"])
def test_common_security_rules(name):
    wf = load(name)
    assert wf["permissions"] == {"contents": "read"}, "minimum permissions"
    for step in all_steps(wf):
        # No ${{ }} expressions inside shell scripts: values go through env: instead.
        assert "${{" not in step.get("run", ""), f"expression interpolated into shell in {name}: {step}"
        if step.get("uses", "").startswith("actions/checkout"):
            assert step.get("with", {}).get("persist-credentials") is False


def test_daily_digest_schedule_and_manual_trigger():
    wf = load("daily-digest.yml")
    assert wf["on"]["schedule"] == [{"cron": "0 5 * * *"}]  # 09:00 Asia/Yerevan (UTC+4)
    assert wf["on"]["workflow_dispatch"]["inputs"]["preview"]["type"] == "boolean"
    preview = next(s for s in all_steps(wf) if "--preview" in s.get("run", ""))
    assert "env" not in preview, "preview step must not receive Telegram secrets"


def test_ci_demo_isolates_secrets_and_preserves_outcome():
    wf = load("ci-notify-demo.yml")
    assert wf["on"]["workflow_dispatch"]["inputs"]["scenario"]["options"] == ["success", "test_failure", "pipeline_failure"]
    tests_job, notify_job = wf["jobs"]["tests"], wf["jobs"]["notify"]
    assert "secrets." not in yaml.safe_dump(tests_job), "the job running test code must not see secrets"
    assert notify_job["needs"] == "tests" and notify_job["if"] == "${{ always() }}"
    send = next(s for s in notify_job["steps"] if s.get("run") == "python -m notifier.ci_summary")
    assert send["continue-on-error"] is True
    assert send["env"]["CI_DEMO"] == "true"


def test_pr_workflow_never_runs_pr_code():
    text = (WORKFLOWS / "pr-merged-notify.yml").read_text(encoding="utf-8")
    wf = load("pr-merged-notify.yml")
    assert wf["on"] == {"pull_request_target": {"types": ["closed"]}}
    job = wf["jobs"]["notify-merged"]
    assert "github.event.pull_request.merged == true" in job["if"]
    assert "github.event.repository.default_branch" in job["if"]
    checkout = next(s for s in job["steps"] if s.get("uses", "").startswith("actions/checkout"))
    assert "ref" not in checkout.get("with", {}), "must not check out the PR head"
    for forbidden in ("pull_request.title", "head.ref", "head_ref", "head.sha", "pull_request.body"):
        assert forbidden not in text
