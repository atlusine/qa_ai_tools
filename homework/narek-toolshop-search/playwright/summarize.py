"""Summarize a Playwright JSON report: one line per test plus totals.

Usage: python3 summarize.py results.json
With --repeat-each, a test is listed once with its pass count (e.g. 2/2).
"""
import json
import re
import sys
from collections import OrderedDict

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def walk(suite, out):
    for spec in suite.get("specs", []):
        for t in spec["tests"]:
            row = out.setdefault(spec["title"], {"runs": 0, "passed": 0, "skipped": False, "error": ""})
            for r in t["results"]:
                row["runs"] += 1
                if r["status"] == "passed":
                    row["passed"] += 1
                elif r["status"] == "skipped":
                    row["skipped"] = True
                elif not row["error"]:
                    msg = ANSI.sub("", (r.get("error") or {}).get("message", ""))
                    row["error"] = " ".join(msg.split())[:200]
    for child in suite.get("suites", []):
        walk(child, out)


def main(path):
    data = json.load(open(path))
    rows = OrderedDict()
    for s in data["suites"]:
        walk(s, rows)
    total = {"PASS": 0, "FAIL": 0, "FLAKY": 0, "SKIP": 0}
    for title, r in rows.items():
        if r["skipped"]:
            status = "SKIP"
        elif r["passed"] == r["runs"]:
            status = "PASS"
        elif r["passed"] == 0:
            status = "FAIL"
        else:
            status = "FLAKY"
        total[status] += 1
        print(f"{status:5} {r['passed']}/{r['runs']}  {title}" + (f"  :: {r['error']}" if r["error"] else ""))
    print("TOTAL", total)


if __name__ == "__main__":
    main(sys.argv[1])
