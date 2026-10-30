# Quickstart: check invite codes and locked pages

Run on the `feature/viewer-access` branch, against the Neon **dev** branch only. Never put a connection string in chat. Each value goes into `.env`, which is gitignored.

## 0. One-time setup

1. **Expose the app URLs**: the branch adds `dev_app_url` and `prod_app_url` outputs. Apply once, from **Actions → Infrastructure → Run workflow**, choosing `feature/viewer-access`. It changes no resources. The bot commits the state to the branch, so `git pull` afterwards.
2. **Fill `.env`** (names are in `.env.example`) from the Terminal, so values never show on screen:

   ```bash
   cd infra
   printf 'VIEWERS_OWNER_URL_DEV=%s\n' "$(tofu output -raw dev_owner_url)" >> ../.env
   printf 'VIEWERS_APP_URL_DEV=%s\n'   "$(tofu output -raw dev_app_url)"   >> ../.env
   printf 'SESSION_SECRET=%s\n' "$(openssl rand -hex 32)" >> ../.env   # local testing only
   ```

   It needs `TF_VAR_state_passphrase` loaded first, as in the phase 3 quickstart.
3. **Make the tables and the app role**: `uv run rain-in-my-head viewer init`. Expect `[dev] ready: 4 tables, role rain_app`.

## 1. Owner commands (story 1)

```bash
uv run rain-in-my-head viewer add Sam            # prints a code once
uv run rain-in-my-head viewer add Robin --tier trusted
uv run rain-in-my-head viewer list
```

Check: both people are listed, with the right tiers. Then confirm the code isn't stored. Start the next line with a space, so your shell doesn't save the code in its history:

```bash
 printf %s 'xxxxxxxxxxxxxxxx' | shasum -a 256     # the code from `viewer add Sam`, without dashes
psql "$VIEWERS_OWNER_URL_DEV" -c "select name from viewers where code_hash = '<the hash>'"   # expect Sam
```

Cross-check once (constitution III): the query returns Sam, and a search of every text column in the four tables for the code itself finds nothing.

## 2. Hosted-mode run

```bash
uv run rain-in-my-head publish        # if data/public.db is old
LISTENING_HOSTED=1 LISTENING_DB=data/public.db DATABASE_URL="$VIEWERS_APP_URL_DEV" uv run rain-in-my-head serve
```

## 3. Locked routes with no code (story 2, SC-002)

```bash
for p in overview genre artist sql/meta schema health me; do
  printf '%-10s ' $p; curl -s -o /dev/null -w '%{http_code}\n' localhost:8000/api/$p
done
```

Expect `403` for everything except `health` and `me` (`200`). Check that `POST /api/sql` with `{"sql":"select 1"}` is `403`, and that the app's startup check passes (the server started).

## 4. Browser run (headless Chrome, story 2 and 3, SC-003, SC-004, SC-007)

1. Open `http://localhost:8000/dashboards/genre`. Expect the login page.
2. Enter a wrong code. Expect "That code didn't work."
3. Enter Sam's code. Expect the dashboards, and Genre loads with data. The top bar shows no Analyst link.
4. Type `/analyst`. Expect the "not available to you" page. In the browser's network tab, `POST /api/sql` is `403`.
5. In the Terminal: `viewer revoke Sam`. Within 5 seconds, click any dashboard link. Expect the login page. The same code now gives "That code didn't work."
6. Log in as Robin. Expect the Analyst link. Pick a pre-defined query and see its results. There's no query box.
7. Add a guest called Kim and log in as Kim. Run `viewer grant Kim --page analyst`, then click any link. Expect the Analyst link. Run `viewer grant Kim --remove-page analyst`, click again, and expect it gone.
8. Press Log out. Expect the login page, and the old cookie rejected.
9. In the browser's cookie view, check `session` is `HttpOnly` and `Secure`.

## 5. Guessing (story 4, SC-006)

Send 6 wrong codes in a minute with `curl`. Expect the sixth to return `429`. Send 20 and expect `423` for a correct code too. A correct code from a different `x-forwarded-for` value still works. Then:

```bash
psql "$VIEWERS_OWNER_URL_DEV" -c "select source_key from login_attempts;"
```

Check each key is 64 hex characters, with no dotted address anywhere (SC-005).

## 6. Local mode unchanged (SC-008)

`uv run rain-in-my-head serve` without hosted mode: every page opens with no login, and `GET /api/me` returns `{"local": true}`.

## 7. Report in the PR

List what was checked and what wasn't, per constitution III. State clearly that the production Neon branch wasn't touched.
