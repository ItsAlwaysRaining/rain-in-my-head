# Proposal

## Why

Seeing what one month looked like (top artists, tracks, genres, when you listened) on the Overview means setting a custom date range by hand. The "Scrobbles per month" chart already shows every period, so clicking a bar should be the quick way in (#4).

## What Changes

- Clicking a bar in the Overview's over-time chart ("Scrobbles/Hours per week/month/year") selects that period. Every other figure and chart on the Overview then shows only that period: KPIs (with deltas against the previous period of the same length), Top lists, "When you listen", new artists, genre charts, the mainstream chart, loved tracks and data quality.
- The over-time chart keeps showing the whole sidebar range. The selected bar stays highlighted and the others are dimmed, so another period can be clicked straight away.
- Inside a selected month or week, the time-series charts (new artists, genre shares) plot per day. Inside a selected year, they plot per month.
- A caption names the selected period, next to a button that shows the whole range again. Clicking the chart background also clears the selection.
- Clicking a genre chart while a period is selected opens the Genre page for that period.
- "#1 per year" is unchanged. It always covers all data.

No new page, CLI command, data source, dependency or schema change. Only `dashboard/views/overview.py` changes.

## Capabilities

### New Capabilities
- `dashboard-overview`: the Overview page's date-range filtering, including selecting a period from the over-time chart. No Overview spec exists yet, so this one covers only the behaviour this change adds or touches.

### Modified Capabilities
None. There are no existing specs.

## Impact

- Code: `dashboard/views/overview.py`.
- Docs: `README.md` gets a short note on filtering by period.
- No changes to the database, CLI or other pages. The Genre page already reads `start`/`end` from the URL.
