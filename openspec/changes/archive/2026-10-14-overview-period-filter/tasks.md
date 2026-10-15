# Tasks

## 1. Narrow the page to a selected period

- [x] 1.1 In `dashboard/views/overview.py`, build the over-time table from the sidebar range before the KPIs. Verify the page renders unchanged with no selection (AppTest through `dashboard/app.py`, no exceptions).
- [x] 1.2 Read the over-time chart's selection from session state, map its `period` label to the period's start and end (clamped to the sidebar range), and rebuild `start`/`end`/`df`/`span`/`prev`. Ignore labels that aren't in the table. Verify by clicking a bar in headless Chrome: the caption shows the period's dates, and the Scrobbles KPI matches a `sqlite3` count for the same local dates.
- [x] 1.3 Add the click selection to the over-time chart, with the selected bar highlighted and others dimmed. Verify in headless Chrome that clicking a bar changes the KPIs and caption, and that clicking another bar switches to it.

## 2. Finer grain and clearing

- [x] 2.1 Use a day grain (week/month selected) or a month grain (year selected) for the "New artists" and genre charts, with matching titles, captions and tooltips. Verify in headless Chrome that "New artists per day" appears after clicking a month, and that a year shows months.
- [x] 2.2 Show the caption naming the selected period and a "Show whole range" button that resets the chart's key. Verify in headless Chrome that the button restores all bars and the sidebar range's KPIs, and that a change of time grain drops the selection.
- [x] 2.3 Verify in headless Chrome that clicking a genre chart with a month selected opens the Genre page with that month's `start`/`end`.
- [x] 2.4 Add a "Filter by period" note to `README.md` covering the click, the finer grain and how to clear. Verify the README matches the behaviour checked in 2.1–2.2.
