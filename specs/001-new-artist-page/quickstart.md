# Quickstart: validate New Artists and the Artist page

## Prerequisites

- `data/listening.db` built (`uv run rain-in-my-head build`).
- Google Chrome installed (driven headless; nothing is added to the project).
- The TypeScript app built (`cd web && npm run build`).

## Run

```sh
uv run streamlit run dashboard/app.py --server.headless true   # :8501
uv run rain-in-my-head serve                                    # :8000
```

## Scenarios (headless Chrome in both apps, plus SQLite cross-checks)

Run each scenario on :8501 (Streamlit) and :8000 (TypeScript).

1. **Default list (US1, FR-001–003)**: open `/` with no period selected. The table is titled
   "New artists in <latest month>". Compare its artists and plays with:

   ```sql
   WITH firsts AS (SELECT artist_key, MIN(played_at) AS first FROM scrobbles
                   WHERE played_at >= 946684800 GROUP BY artist_key)
   SELECT s.artist_key, COUNT(*) FROM scrobbles s JOIN firsts f USING (artist_key)
   WHERE s.played_at >= 946684800
     AND date(f.first, 'unixepoch', 'localtime') BETWEEN :month_start AND :range_end
     AND date(s.played_at, 'unixepoch', 'localtime') BETWEEN :month_start AND :range_end
   GROUP BY 1 ORDER BY 2 DESC;
   ```

2. **Selected period (US1)**: click the "Mar 2026" bar; the title becomes "New artists in Mar 2026"
   and the rows match the query above for March.
3. **Open an artist (US2, FR-004)**: click an artist's name; then from the list again, click another
   artist's album art. Each opens `/artist?artist=…&start=2026-03-01&end=2026-03-31`.
4. **Artist page (US2, FR-005–007)**: header shows cover, name and "N plays in Mar 2026 · M all
   time"; songs sorted by plays; songs' plays sum to N; N and M match
   `SELECT COUNT(*) FROM scrobbles WHERE artist_key = :a AND played_at >= 946684800 [AND date(…) BETWEEN …]`.
5. **Placeholder (US3, FR-008)**: an artist or song with no art shows the placeholder image, not a
   blank cell.
6. **Way back (US3, FR-009)**: the "Overview" link opens the Overview.
7. **Edge cases**: `/artist` with no params and `/artist?artist=nobody` show the message and link;
   an artist with plays but none in the period shows "0 plays in …" and a note.
8. **Same numbers (FR-012, SC-005)**: for the default month and for March 2026, the list in both
   apps has the same artists and plays, and one artist's page has the same counts and songs.
9. **Regression**: the Genre page still lists artists and songs with art in both apps.

AppTest through `dashboard/app.py` (Overview, `/artist`, `/genre`) is run first as a smoke test, and
`npx tsc --noEmit` and `npm run build` before the TypeScript checks.
