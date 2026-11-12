## Context

`Genre.tsx` reads `genre`, `start`, `end` from the URL; `/api/genre` (`api.py:_genre_view`) defaults to All time. The Overview already has preset chips (`PRESETS`, `ChipGroup`, Custom popup) and `overview.resolve_range`, plus `overview.genre_shares` for the per-step share of tagged plays. Chart colours live in `web/src/charts/config.ts` (`GENRE_COLORS`, index 4 = Moss `#2FA36B`).

## Goals / Non-Goals

**Goals:** range chips identical to the Overview; one area chart in the genre's colour with a peak label; Overview → Genre keeps the same chip.

**Non-Goals:** grain toggle on the Genre page; changing the artists/songs tables; Streamlit `dashboard/views/genre.py` (web only, matching other recent Figma-gap changes).

## Decisions

1. **Reuse, don't copy, the range logic.** `/api/genre` takes `preset` and calls `overview.resolve_range`, returning `range` (`start`, `end`, `base_start`, `base_end`, `data_first`, `data_last`) like `/api/overview`. Dates without a preset are treated as `custom`; nothing at all is `all` (keeps old links and today's default).
2. **Extract the chips + Custom popup into a shared `RangePicker` component** in `components/`, used by both Overview and Genre. Avoids two copies of the popup. Overview behaviour must not change.
3. **Share series from `overview.genre_shares`.** Load the range's tagged plays once, call `genre_shares(df, grain, n=…)`, filter to the chosen genre. Grain: week if the range is ≤ 92 days, else month (same rule as the Overview's inner grain — reuse that helper if one exists). The response gets `share: {color_index: int | null, points: [{start, share, plays}]}`; `color_index` is the genre's rank in the top 6, else null.
4. **Colour on the client:** `GENRE_COLORS[color_index] ?? RAIN`. Only palette constants, no new hex values.
5. **Chart** in new `web/src/charts/genre.ts`: Vega-Lite area (fill at ~0.35 opacity, line on top) + a text layer filtered to the max point (`argmax` via window transform), percent axis.

## Risks / Trade-offs

- Extracting `RangePicker` touches the Overview → run the Overview tests and check it in the browser.
- Indie colour depends on rank, so it can differ by range (Moss in Figma's example). Accepted: it always matches the Overview for the same range.
- Figma 263:2051 not yet read in detail; layout (chip row position, chart height) is checked against it during apply.
