#!/usr/bin/env bash
# PostToolUse hook (Write|Edit). Checks the lines just added to a spec, module
# object, flow or support file against the binding rules, and feeds any hit
# back to Claude (exit 2). Silent when clean.

set -uo pipefail

payload=$(cat)
if command -v jq >/dev/null 2>&1; then
  file=$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null)
else
  file=$(printf '%s' "$payload" | python3 -c 'import json,sys; d=json.load(sys.stdin).get("tool_input",{}); print(d.get("file_path") or d.get("path") or "")' 2>/dev/null)
fi

[ -z "${file:-}" ] && exit 0
case "$file" in *.js) ;; *) exit 0 ;; esac

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
case "$file" in
  "$ROOT"/*) rel=${file#"$ROOT"/} ;;
  *) exit 0 ;;
esac
case "$rel" in
  tests/*|module_object/*|flows/*|support/*) ;;
  *) exit 0 ;;
esac
cd "$ROOT" || exit 0
. "$ROOT/scripts/claude-hooks/credentials-pattern.sh"

added=$(git diff -U0 HEAD -- "$rel" 2>/dev/null | awk '
  /^@@/ { split($3, a, ","); ln = a[1]; sub(/^\+/, "", ln); next }
  /^\+\+\+/ { next }
  /^\+/ { print ln ":" substr($0, 2); ln++; next }
')
if [ -z "$added" ] && ! git ls-files --error-unmatch "$rel" >/dev/null 2>&1; then
  added=$(grep -n "" "$rel" 2>/dev/null)
fi
[ -z "$added" ] && exit 0

findings=""
check() { # regex, message
  local hits
  hits=$(printf '%s\n' "$added" | grep -E -- "$1" | head -3)
  [ -z "$hits" ] && return 0
  while IFS= read -r h; do
    findings="${findings}  $rel:${h%%:*} — $2
"
  done <<< "$hits"
}

check 'waitForTimeout\('                        "fixed wait. Wait on the API response or a web-first assertion instead (automation-stabilization §1-2)."
check '\.only\('                                ".only() must never be committed (forbidOnly also fails CI)."
check 'retries:[[:space:]]*([4-9]|[1-9][0-9])'   "retries above the cap of 3 (rules/testing-standards.md)."
check '(force:[[:space:]]*true)'                 "force click/fill. Bypasses actionability checks and hides product bugs (automation-stabilization §3)."

if [ "$rel" != "support/selectors.js" ]; then
  check '\.(locator|\$|\$\$|\$eval|\$\$eval)\((["'"'"'`])' "raw selector string. Register it in support/selectors.js and resolve it with PlaywrightMethods.get_element (rules/selectors.md)."
  check 'getBy(TestId|Role|Text|Label|Placeholder)\((["'"'"'`])' "inline locator. Selectors live in support/selectors.js (rules/selectors.md). Allowed only inside support/PlaywrightMethods.js."
fi

case "$rel" in
  tests/*)
    check '(^|[^.])expect\(|expect\.poll'           "assertion in a spec. Move it into an assert_* method on the module object (rules/assertions.md)."
    check 'page\.goto\('                             "page.goto in a spec. Use an open_* module-object method (it uses domcontentloaded; the default load event never fires on this app)."
    check "$CREDENTIALS_PATTERN"                     "hardcoded account or password. Read it from support/users.js (rules/testing-standards.md)."
    check '(test|it)\("[^"]{86,}"'                   "test title longer than 85 characters (rules/testing-standards.md)."
    ;;
esac

[ "$rel" = "support/PlaywrightMethods.js" ] && findings=$(printf '%s' "$findings" | grep -v 'inline locator' || true)

[ -z "$findings" ] && exit 0
{
  echo "Rule violations in the lines just written:"
  echo ""
  printf '%s\n' "$findings"
  echo ""
  echo "Fix these before moving on. Full gate: bash scripts/claude-hooks/review-diff.sh"
} >&2
exit 2
