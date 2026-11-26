"""Demo-only tests used by .github/workflows/ci-notify-demo.yml.

They pass in normal runs. The demo workflow sets DEMO_SCENARIO=test_failure to make one
assertion fail on purpose, so the Telegram summary for a failed test run can be shown.
"""
import os

import pytest


def test_demo_scenario_gate():
    scenario = os.environ.get("DEMO_SCENARIO", "success")
    assert scenario != "test_failure", "Simulated assertion failure (demo scenario: test_failure)"


@pytest.mark.skip(reason="demo: shows how skipped tests are counted in the Telegram summary")
def test_demo_skipped_example():
    pass
