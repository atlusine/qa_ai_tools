#!/usr/bin/env bash
# SessionStart hook. Prints the facts that are true right now and cannot be
# read off the files: branch, target URL, whether the app is reachable, and
# whether dependencies and the browser are installed.

set -uo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT" || exit 0

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
echo "Branch: $branch"
case "$branch" in
  main|master) echo "  ⚠ On $branch. Create a branch before committing test changes (e.g. tests/cart-coupon)." ;;
esac

env_value() {
  [ -f .env ] || return 0
  sed -nE "s/^[[:space:]]*$1[[:space:]]*=[[:space:]]*\"?([^\"]*)\"?[[:space:]]*$/\1/p" .env | tail -n 1
}

base_url=${BASE_URL:-$(env_value BASE_URL)}
base_url=${base_url:-https://practicesoftwaretesting.com}
echo "App under test: $base_url"

if command -v curl >/dev/null 2>&1; then
  code=$(curl -s -o /dev/null -m 8 -w '%{http_code}' "$base_url" 2>/dev/null || echo "000")
  case "$code" in
    2*|3*) echo "  Reachable (HTTP $code)." ;;
    *) echo "  ⚠ Not reachable (HTTP $code). A red run now is an environment problem, not a test or product bug." ;;
  esac
fi

[ -d node_modules/@playwright/test ] || echo "⚠ Dependencies missing — run: npm install && npx playwright install chromium"
[ -f .env ] || echo "Note: no .env — defaults from support/environment.js and support/users.js apply (copy .env.example to change them)."
exit 0
