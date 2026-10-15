# Design

## Context

`dashboard/views/overview.py` reads the sidebar range into `start`/`end`, then builds `df` (plays in range) and `prev` (the previous period of the same length). Every section below reads `df`, `start`, `end` or `freq`/`grain`. The over-time chart is drawn after the KPIs, from `df`.

Streamlit reruns the whole script on each interaction. A chart with `on_select="rerun"` and a `key` stores its selection in `st.session_state[key]`, and that state can be read at the top of the next rerun, before the chart is drawn.

## Goals / Non-Goals

**Goals:** one place where the selected period narrows `start`/`end`, so every existing section follows it without being changed one by one.

**Non-Goals:** keeping the selection in the URL or across page changes; selecting several periods at once.

## Decisions

- **Narrow `start`/`end` early.** Build the over-time table from the sidebar range first, read the selection from session state, then reassign `start`/`end` and rebuild `df`/`span`/`prev`. The KPIs, deltas, caption and Genre links then pick up the period with no further changes. *Alternative:* filter each section separately. Rejected, because it touches every section and is easy to miss one.
- **Select by the bar's label.** The selection is on the `period` field (the bar's label, such as "Mar 2026"), which is looked up in the over-time table to get the period's start date. If the label isn't in the table (after a change of range or grain), the selection is ignored. *Alternative:* select on the timestamp. Rejected, because Vega-Lite returns temporal values as epoch milliseconds in local time, which is fiddly to map back.
- **Period end.** The period ends at its start plus one week, month or year, minus a day. It is clamped to the sidebar range so that partial periods at the edges stay inside it.
- **Inner grain.** `inner_grain` is "Day" for Week/Month selections and "Month" for Year; it equals `grain` with no selection. The new-artists and genre charts use it; the over-time chart keeps `grain`.
- **Clearing.** The chart's key includes a counter in session state. "Show whole range" increments it, so the next run draws a fresh chart with no selection. Clicking the chart background clears the selection natively, through Vega-Lite's point selection.
- **Highlight.** The bar color is set by a condition on the selection: iris when selected (or when nothing is selected), a dark iris step from the existing `IRIS_RAMP` otherwise.

## Risks / Trade-offs

- [Selection state shape could change across Streamlit versions] → read it defensively (`.get` with defaults), and verify in a real browser.
- [Daily genre shares are noisy for small months] → acceptable for a drill-down; the per-day tooltips show the play counts.
