#!/usr/bin/env bash
# Pre-commit / pre-PR grep gate for toolshop-automation.
#
# Reports only lines YOU ADDED, so existing debt is never dumped back at you.
#
#   bash scripts/claude-hooks/review-diff.sh              # vs main (committed + uncommitted + untracked)
#   bash scripts/claude-hooks/review-diff.sh --staged     # staged changes only
#   bash scripts/claude-hooks/review-diff.sh path/a.js …  # named files, whole file
#
# Exit 0 = clean or advisory only. Exit 1 = at least one BLOCK.

set -uo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT" || exit 1
. "$ROOT/scripts/claude-hooks/credentials-pattern.sh"

BASE_BRANCH=${BASE_BRANCH:-main}
MODE="range"
FILES=()
case "${1:-}" in
  --staged) MODE="staged" ;;
  "") ;;
  *) MODE="files"; FILES=("$@") ;;
esac

collect() { while IFS= read -r line; do [ -n "$line" ] && FILES+=("$line"); done; }

case "$MODE" in
  range)
    BASE=$(git merge-base "$BASE_BRANCH" HEAD 2>/dev/null) || { echo "Cannot resolve $BASE_BRANCH; use --staged or pass files." >&2; exit 1; }
    collect < <({ git diff --relative --name-only --diff-filter=d "$BASE" -- '*.js'; git ls-files --others --exclude-standard -- '*.js'; } | sort -u)
    ;;
  staged)
    collect < <(git diff --relative --cached --name-only --diff-filter=d -- '*.js')
    ;;
esac

if [ ${#FILES[@]} -eq 0 ]; then echo "review-diff: no changed .js files."; exit 0; fi

BLOCK=0
ADVISE=0

added_lines() {
  local f=$1
  if [ "$MODE" = "files" ] || ! git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    grep -n "" "$f" 2>/dev/null
    return
  fi
  local range
  if [ "$MODE" = "staged" ]; then range=(--cached); else range=("$BASE"); fi
  git diff -U0 "${range[@]}" -- "$f" | awk '
    /^@@/ { split($3, a, ","); ln = a[1]; sub(/^\+/, "", ln); next }
    /^\+\+\+/ { next }
    /^\+/ { print ln ":" substr($0, 2); ln++; next }
  '
}

report() { # level, file, "lineno:content", message
  local level=$1 file=$2 hit=$3 msg=$4
  local txt
  txt=$(echo "${hit#*:}" | sed 's/^[[:space:]]*//' | cut -c1-110)
  printf '  %-6s %s:%s\n         %s\n         > %s\n' "$level" "$file" "${hit%%:*}" "$msg" "$txt"
  if [ "$level" = "BLOCK" ]; then BLOCK=$((BLOCK + 1)); else ADVISE=$((ADVISE + 1)); fi
}

scan() { # file, regex, level, message
  local f=$1 re=$2 level=$3 msg=$4
  while IFS= read -r hit; do
    [ -n "$hit" ] && report "$level" "$f" "$hit" "$msg"
  done < <(added_lines "$f" | grep -E -- "$re" || true)
}

echo "review-diff: ${#FILES[@]} changed .js file(s)"
echo

for f in "${FILES[@]}"; do
  [ -f "$f" ] || continue
  case "$f" in node_modules/*|scripts/*|playwright.config.js) continue ;; esac

  scan "$f" 'waitForTimeout\(' BLOCK "Fixed wait. Wait on the API response or a web-first assertion (automation-stabilization §1-2)."
  scan "$f" '\.only\(' BLOCK "Exclusive test. Never commit .only."
  scan "$f" 'retries:[[:space:]]*([4-9]|[1-9][0-9])' BLOCK "retries above the cap of 3."
  scan "$f" 'force:[[:space:]]*true' ADVISE "Force action. Exhaust automation-stabilization §3 first; if kept, justify it in the PR description."

  if [ "$f" != "support/selectors.js" ]; then
    scan "$f" '\.(locator|\$|\$\$|\$eval|\$\$eval)\((["'"'"'`])' BLOCK "Raw selector string. Register it in support/selectors.js (rules/selectors.md)."
  fi
  case "$f" in
    support/PlaywrightMethods.js|support/selectors.js) ;;
    *) scan "$f" 'getBy(TestId|Role|Text|Label|Placeholder)\((["'"'"'`])' BLOCK "Inline locator. Selectors live in support/selectors.js (rules/selectors.md)." ;;
  esac

  case "$f" in
    tests/*.spec.js)
      scan "$f" '(^[0-9]+:|[^.])expect\(|expect\.poll' BLOCK "Assertion in a spec. Move it into an assert_* method on the module object (rules/assertions.md)."
      scan "$f" 'page\.goto\(' BLOCK "page.goto in a spec. Use an open_* module-object method."
      scan "$f" "$CREDENTIALS_PATTERN" BLOCK "Hardcoded account or password. Read it from support/users.js."
      while IFS= read -r hit; do
        [ -n "$hit" ] && report BLOCK "$f" "$hit" "Test title longer than 85 characters."
      done < <(added_lines "$f" | awk -F'"' '/test\("/ { if (length($2) > 85) print }' || true)
      while IFS= read -r hit; do
        [ -z "$hit" ] && continue
        ln=${hit%%:*}
        if ! sed -n "$((ln - 1))p" "$f" | grep -qE 'https?://'; then
          report BLOCK "$f" "$hit" "Skipped test with no issue URL comment directly above it."
        fi
      done < <(added_lines "$f" | grep -E '(test|test\.describe)\.(skip|fixme)\(' || true)
      if ! grep -qE "tag: \"@(smoke|regression)\"" "$f"; then
        report ADVISE "$f" "1:describe" "No @smoke / @regression tag on the describe — the spec will not be picked up by tag-filtered runs."
      fi
      ;;
  esac

  while IFS= read -r hit; do
    [ -z "$hit" ] && continue
    case "$hit" in *"http://"*|*"https://"*) continue ;; esac
    report ADVISE "$f" "$hit" "Comment in the diff. Code explains itself through method names (automation-code-style §3)."
  done < <(added_lines "$f" | grep -E '^[0-9]+:[[:space:]]*(//|/\*|\*[^/])' || true)

  while IFS= read -r hit; do
    [ -n "$hit" ] && report ADVISE "$f" "$hit" "Looks like a camelCase method. Methods are snake_case (automation-code-style §2)."
  done < <(added_lines "$f" | grep -E '^[0-9]+:[[:space:]]{2}(static[[:space:]]+)?(async[[:space:]]+)?[a-z]+[A-Z][a-zA-Z0-9]*[[:space:]]*\([^)]*\)[[:space:]]*\{' || true)
done

echo
if [ "$BLOCK" -gt 0 ]; then
  echo "review-diff: $BLOCK blocking, $ADVISE advisory. Fix the blocking items; justify or remove the advisory ones."
  exit 1
fi
if [ "$ADVISE" -gt 0 ]; then
  echo "review-diff: clean of blocking issues, $ADVISE advisory — justify each in the PR description."
  exit 0
fi
echo "review-diff: clean."
exit 0
