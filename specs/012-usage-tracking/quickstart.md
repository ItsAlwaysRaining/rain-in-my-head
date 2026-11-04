# Quickstart: check usage tracking and the limit

> **Superseded in part (2026-11-04):** the nightly export to the `analytics` branch was removed so the repository can be public (see `openspec/changes/make-repo-public`, or `openspec/specs/usage-retention` once archived). Visitor data now stays only in the visitor database. The nightly job only deletes records older than 12 months (`.github/workflows/prune.yml`). Anything below about the `analytics` branch, `analytics.yml` or the private copy is history.

Run on the `feature/usage-tracking` branch, against the Neon **dev** branch only. Never put a connection string in chat. Values live in `.env`, which is gitignored. Contracts: [api.md](contracts/api.md), [cli.md](contracts/cli.md). Tables: [data-model.md](data-model.md).

## 0. One-time setup (dev)

1. `.env` already holds `VIEWERS_OWNER_URL_DEV`, `VIEWERS_APP_URL_DEV` and `SESSION_SECRET` from phase 4. Nothing new goes in it.
2. Add the new table and grants: `uv run rain-in-my-head viewer init`. Expect `[dev] ready: 5 tables, role rain_app`.
3. Add two test people:

   ```bash
   uv run rain-in-my-head viewer add Sam            # copy the code somewhere safe
   uv run rain-in-my-head viewer add Robin --tier trusted
   ```

4. Start the site in hosted mode, as in phase 4:

   ```bash
   uv run rain-in-my-head publish        # if data/public.db is old
   LISTENING_HOSTED=1 LISTENING_DB=data/public.db DATABASE_URL="$VIEWERS_APP_URL_DEV" uv run rain-in-my-head serve
   ```

To read the stored records directly, use `viewer usage --person NAME` (it lists the raw rows). `psql` also works if you have it (`brew install libpq`): `psql "$VIEWERS_OWNER_URL_DEV"`.

## 1. Recording (story 1, SC-001)

In a real browser (headless Chrome is fine):

1. Open `http://localhost:8000/dashboards/genre` and log in as Sam.
2. Open Genre, Overview and Artist, in that order, and wait 20 seconds on Artist. Move the mouse now and then.
3. Pick a genre and open two artists' song lists.
4. Go to About.

Check: `uv run rain-in-my-head viewer usage --person Sam` shows 4 `view` rows (genre, overview, artist, about), 2 `feature` rows (`genre-songs`), and `time` rows with about 20 seconds on Artist. Cross-check once with a direct count (constitution III):

```sql
select kind, count(*) from usage_events e join viewers v on v.id = e.viewer_id where v.name = 'Sam' group by kind;
```

Also check:
- A page opened and left within 3 seconds is stored, and a reload within 5 seconds adds no second `view`.
- Leave a tab open and idle for 2 minutes: its `seconds` stops growing after about 60 seconds of no input.
- Open the landing page and the login page without logging in: no rows.
- If only the recording fails (for example the `usage_events` table is missing), pages still load and the report is silently dropped. With the whole visitor database unreachable, the site can't check anyone's session, so every locked page and heavy request answers "try again in a minute" (the phase 4 behaviour). Check both: `POST /api/events` with a failing store answers 204, and a wrong `DATABASE_URL` answers 503.

## 2. The limit (story 3, SC-002, SC-003)

Log in with `curl` to get a cookie, then send heavy requests in a loop:

```bash
curl -s -c /tmp/sam.cookie -H 'content-type: application/json' -d '{"code":"SAMS-CODE"}' localhost:8000/api/login
for i in $(seq 1 31); do
  curl -s -o /dev/null -w '%{http_code} ' -b /tmp/sam.cookie 'localhost:8000/api/genre/songs?artist_key=KEY&genre=GENRE'
done; echo
```

Use real values for `artist_key` and `genre` from the Genre page's network tab. Expect 30 answers of `200` and then `429`. The `429` body has `rate_limited`, a message with the seconds to wait, and a `Retry-After` header. Then:
- Log in as Robin in another browser and use the site normally: no limit message.
- Wait for the stated seconds, repeat one request: `200`, with no new login.
- Run `viewer usage --person Sam`: exactly one `limit` row, even though many refusals were sent.
- Send a typed-SQL `POST /api/sql` as Robin (`{"sql":"select 1"}`) 40 times: all `403`, no `feature` rows, no `limit` rows.
- Try the daily limit by lowering `HEAVY_PER_DAY` for a run to 5 (a temporary local edit, not committed): the sixth request returns the "today's limit" message.

## 3. Browser notice and layout (stories 1, 3, 4)

1. In the same browser session, hit the limit from the Genre page by clicking through artists quickly. Expect a plain notice on the page with the seconds to wait, not a blank screen or a technical error. The wait text matches the `Retry-After` header.
2. Open the login page. Expect the notice to say pages, features and time on site are recorded against your name, that records are kept 12 months, and that no IP address is stored.
3. Flood `POST /api/events` with 150 `open` reports in a minute from Sam's cookie. Expect `204` every time, and no more than 120 new rows.

## 4. The owner's report (story 2, SC-007, SC-008)

1. On the Mac, with the app running normally (`uv run rain-in-my-head serve`, no hosted mode), open `http://localhost:8000/visitors`. Expect Sam and Robin with visits, time, top pages, features and limit hits.
2. Switch the range between 7 days, 30 days and 12 months, and between dev and prod (prod shows an empty or short list until it has visitors).
3. Run `uv run rain-in-my-head viewer usage`. Expect the same numbers as the page (SC-008).
4. Remove `VIEWERS_OWNER_URL_PROD` for a moment and choose prod. Expect a message naming the variable, not an error page.
5. In hosted mode, with Robin's cookie, `curl -b ... localhost:8000/api/visitors`. Expect `403` "This DJ doesn't take requests." Do it with Sam's cookie and with no cookie too. Then run `viewer grant Robin --page visitors`. Expect an "unknown page" error (SC-007).
6. Open the hosted-mode page `/visitors` in the browser as Robin. Expect the "not available to you" page, and no Visitors link in the navigation.

## 5. Retention (story 4, SC-006)

```sql
insert into usage_events (viewer_id, kind, page, at)
select id, 'view', 'about', now() - interval '13 months' from viewers where name = 'Sam';
insert into usage_events (viewer_id, kind, page, at)
select id, 'view', 'about', now() - interval '11 months' from viewers where name = 'Sam';
```

Run `uv run rain-in-my-head viewer prune`. Expect `deleted 1 usage records older than 12 months`. The 11-month row is still there. People and sessions are unchanged (compare `viewer list` before and after).

## 6. Privacy sweep (SC-005)

```bash
mkdir -p /tmp/usage-export && uv run rain-in-my-head viewer export /tmp/usage-export
grep -E -c '([0-9]{1,3}\.){3}[0-9]{1,3}|([0-9a-fA-F]{1,4}:){3,7}[0-9a-fA-F]{1,4}|::1' /tmp/usage-export/*.csv   # expect 0 and 0 (a time like 22:45:17 has too few colons to match)
grep -c -i 'code_hash\|session' /tmp/usage-export/*.csv                                        # expect 0 and 0
```

Also search the stored text in the live tables for the same patterns, and check that none of Sam's or Robin's codes appear in either file. Run the export twice and compare: the two outputs must be byte-identical (`diff -r`).

## 7. The nightly job (story 5, SC-010)

Before the merge (the workflow can only run from the default branch, so first check its pieces by hand):

1. Run `viewer export` as in step 6, then walk through the workflow's git steps in a scratch clone: make an orphan commit holding the two files, push it to a test branch of a throwaway local bare repo, change one row, repeat, and check the branch ends with one commit.

After the merge:

1. Actions → analytics → **Run workflow**, choose `dev`. Expect a green run, and the branch `analytics-dev` holding one commit with two files.
2. Run it again with no change in the database. Expect a green run and no new commit.
3. Add one usage record and run it again. Expect one commit on the branch (not two), and the previous commit gone from its history.
4. Check `main` is unchanged by all of this (`git log main -1`).
5. Make the run fail on purpose (temporarily blank the dev secret in a fork, or run it with a wrong env) and check the run shows red while the site still works.

## 8. Local mode unchanged (SC-009)

`uv run rain-in-my-head serve` without hosted mode: every page opens with no login, `GET /api/me` returns `{"local": true}`, a click through every page stores nothing (compare the row count before and after), and heavy routes never answer `429`. Re-run the checks from phase 4's quickstart sections 3 and 6.

## 9. Free plans (SC-011)

Open the Visitors page's free-plan section. Check it names no paid plan, shows the database size next to its free limit, and says Vercel's processing time is on Vercel's dashboard. Confirm the limits in `usage.py` against the Neon and Vercel pricing pages on the day (research R7).

## 10. After the merge

Run `uv run rain-in-my-head viewer init --env prod` once, to add the table and grants to prod. Expect `[prod] ready: 5 tables, role rain_app`. Until then the prod site would fail its recording queries and refuse heavy requests.

## 11. Report in the PR

List what was checked in a real browser, which numbers were cross-checked against a direct query, and what was not checked: Vercel's real processing time, and a nightly run on the real schedule.
