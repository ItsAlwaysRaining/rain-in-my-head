# Quickstart: validate New Artists and the Artist page

## Prerequisites

- `data/listening.db` built (`uv run listening build`).
- Google Chrome installed (Playwright drives it with `channel="chrome"`; nothing is added to the
  project).

## Run

```sh
uv run streamlit run dashboard/app.py --server.headless true
```

## Scenarios (headless Chrome, plus SQLite cross-checks)

1. **Default list (US1, FR-001–003)**: open `/` with no period selected. The table is titled
   "New artists in <latest month>". Compare its artists and plays with:

   ```sql
   WITH firsts AS (SELECT artist_key, MIN(played_local) AS first_play FROM v_plays GROUP BY artist_key)
   SELECT p.artist_key, COUNT(*) FROM v_plays p JOIN firsts f USING (artist_key)
   WHERE date(f.first_play) BETWEEN :month_start AND :range_end
     AND date(p.played_local) BETWEEN :month_start AND :range_end
   GROUP BY 1 ORDER BY 2 DESC;
   ```

2. **Selected period (US1)**: click the "Mar 2026" bar; the title becomes "New artists in Mar 2026"
   and the rows match the query above for March.
3. **Open an artist (US2, FR-004)**: click an artist's name; then from the list again, click another
   artist's album art. Each opens `/artist?artist=…&start=2026-03-01&end=2026-03-31`.
4. **Artist page (US2, FR-005–007)**: header shows cover, name and "N plays in Mar 2026 · M all
   time"; songs sorted by plays; songs' plays sum to N; N and M match `SELECT COUNT(*) FROM v_plays
   WHERE artist_key = :a [AND date(played_local) BETWEEN …]`.
5. **Placeholder (US3, FR-008)**: an artist or song with no art shows the placeholder image, not a
   blank cell.
6. **Way back (US3, FR-009)**: the "Overview" link opens the Overview.
7. **Edge cases**: `/artist` with no params and `/artist?artist=nobody` show the message and link.
8. **Regression**: the Genre page still lists artists and songs with art after the helper move.

AppTest through `dashboard/app.py` (Overview, `/artist`, `/genre`) is run first as a smoke test.
