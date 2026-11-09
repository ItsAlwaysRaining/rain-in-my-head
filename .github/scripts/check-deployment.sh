#!/usr/bin/env bash
# Asks a deployment two questions before it is allowed to serve visitors (openspec/specs/production-deploy):
#   1. /api/health says the app is up.
#   2. A route no visitor may open (an unknown path), asked with no login, is refused with login_required.
# Retries for two minutes. Prints status codes and a verdict only: no body, header or cookie reaches the log.
# Needs VERCEL_CLI (the pinned package name) and VERCEL_TOKEN in the environment.
set -u
url="${1:?usage: check-deployment.sh <deployment url>}"
err="$(mktemp)"

# Prints "<status code> <body with spaces and newlines removed>". Extra arguments after `--` go to curl.
ask() {
  local out
  out="$(npx --yes "$VERCEL_CLI" curl "$1" --deployment "$url" -- -sS -m 20 -w '\n%{http_code}' 2>>"$err")" || true
  local code="${out##*$'\n'}"
  local body="${out%$'\n'*}"
  printf '%s %s' "$code" "$(printf '%s' "$body" | tr -d ' \n')"
}

for attempt in $(seq 1 12); do
  health="$(ask /api/health)"
  locked="$(ask /api/probe-not-a-route)"
  health_code="${health%% *}"
  locked_code="${locked%% *}"
  echo "attempt $attempt: /api/health -> $health_code, /api/probe-not-a-route with no login -> $locked_code"
  if [ "$health_code" = 200 ] && [ "${health#* }" = '{"ok":true}' ] \
     && [ "$locked_code" = 403 ] && printf '%s' "${locked#* }" | grep -q 'login_required'; then
    echo "Both checks passed"
    exit 0
  fi
  sleep 10
done

echo "The deployment did not pass: health must be 200 with ok true, and the locked route must be 403 login_required."
echo "The last lines the vercel command wrote to stderr:"
tail -n 5 "$err"
exit 1
