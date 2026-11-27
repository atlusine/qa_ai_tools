#!/usr/bin/env bash
# PreToolUse hook (Bash). When Claude runs `git commit`, lints the .js files
# that will be committed with ESLint and blocks the commit (exit 2) on errors.
# Any other Bash command passes straight through.

set -uo pipefail

payload=$(cat)
if command -v jq >/dev/null 2>&1; then
  cmd=$(printf '%s' "$payload" | jq -r '.tool_input.command // empty' 2>/dev/null)
else
  cmd=$(printf '%s' "$payload" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' 2>/dev/null)
fi

printf '%s' "${cmd:-}" | grep -qE '(^|[;&|[:space:]])git([[:space:]]+-[^[:space:]]+([[:space:]]+[^-][^[:space:]]*)?)*[[:space:]]+commit([[:space:]]|$)' || exit 0

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT" || exit 0

files=$(git diff --cached --relative --name-only --diff-filter=d -- '*.js' '*.mjs' '*.cjs')
if printf '%s' "$cmd" | grep -qE 'commit([^;&|]*[[:space:]])(-a|--all|-[a-zA-Z]*a[a-zA-Z]*)([[:space:]]|$)'; then
  files=$(printf '%s\n%s\n' "$files" "$(git diff --relative --name-only --diff-filter=d -- '*.js' '*.mjs' '*.cjs')")
fi
files=$(printf '%s\n' "$files" | sed '/^$/d' | sort -u)
[ -z "$files" ] && exit 0

if [ ! -x node_modules/.bin/eslint ]; then
  echo "ESLint is not installed — run: npm install (commit blocked until lint can run)." >&2
  exit 2
fi

mapfile -t list <<< "$files"
if output=$(node_modules/.bin/eslint --no-warn-ignored "${list[@]}" 2>&1); then
  [ -n "$output" ] && printf '%s\n' "$output" >&2
  exit 0
fi

{
  echo "ESLint failed on the files being committed — commit blocked:"
  echo ""
  printf '%s\n' "$output"
  echo ""
  echo "Fix these (or run: npm run lint:fix), re-stage, then commit again."
} >&2
exit 2
