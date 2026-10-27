# Quickstart: Verify the Prototype Redesign

## Run

```sh
uv run rain-in-my-head serve --dev      # API on :8000
cd web && npm install && npm run dev    # app on :5173
```

In a worktree without its own database, start the API with `LISTENING_DB=<path to data/listening.db>` set.

## Checks

1. `cd web && npm run build`. Typecheck and build pass.
2. **Shell**: open each top-bar link. The right item is highlighted and the breadcrumb matches [contracts/routes.md](contracts/routes.md). The cloud logo goes home.
3. **Redirects**: `/sql`, `/schema`, `/genre?genre=pop`, `/artist?artist=…` land on their new pages with the query string kept.
4. **Dashboards**: with Last 12 months and Month, write down the five KPIs. Compare them with the old app (`git stash` or `main`) and with a direct query, for example:
   `sqlite3 data/listening.db "SELECT COUNT(*) FROM v_plays WHERE played_local >= date('now','-12 months')"`.
   Click a bar, a genre chip, a genre line, a "New artists per month" point, a heatmap square and a mainstream bar. Each opens the right page.
5. **New artists**: change the month. The list updates. Click a row and the Artist page opens. "Back to Dashboards" restores the filters.
6. **Playlist Generator**: Time Slot with Friday 17–19 gives the same first ten tracks as `main`. AI shows Coming Soon and links to #32. SQL shows the placeholder and links to #31.
7. **Analyst**: run "Top artists this year", sort a column, download the CSV. Expand the schema card, drag a card and reload. The card stays where it was moved.
8. **Placeholders**: `/`, `/storm`, `/dashboards/slot`, `/dashboards/mainstream`, `/about` and `/contact` each show the Coming Soon visual and a working issue link.
9. **Narrow window (390px)**: no horizontal scroll, and cards stack.
10. **Reduced motion** (DevTools → Rendering → emulate): the Coming Soon rain doesn't animate.
