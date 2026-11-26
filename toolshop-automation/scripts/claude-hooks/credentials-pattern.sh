# Sourced by validate-edit.sh and review-diff.sh. Sets CREDENTIALS_PATTERN, an
# ERE matching the demo-account domain and, when known, the password from
# USER_PASSWORD (environment first, then .env), so no password lives in the repo.

credentials_password=${USER_PASSWORD:-}
if [ -z "$credentials_password" ] && [ -f "$ROOT/.env" ]; then
  credentials_password=$(sed -n 's/^[[:space:]]*USER_PASSWORD[[:space:]]*=[[:space:]]*["'"'"']\{0,1\}\([^"'"'"']*\)["'"'"']\{0,1\}[[:space:]]*$/\1/p' "$ROOT/.env" | tail -1)
fi

CREDENTIALS_PATTERN='@practicesoftwaretesting\.com'
if [ -n "$credentials_password" ]; then
  CREDENTIALS_PATTERN="$CREDENTIALS_PATTERN|$(printf '%s' "$credentials_password" | sed 's/[][\.*^$+?(){}|/]/\\&/g')"
fi
unset credentials_password
