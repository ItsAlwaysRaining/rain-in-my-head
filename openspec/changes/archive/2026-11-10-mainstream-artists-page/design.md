# Design

## Context

The Overview's "Mainstream vs. niche" chart is built in `web/src/charts/overview.ts` from `data.listener_buckets`, which `/api/overview` builds in `src/rain_in_my_head/api.py` with `ov.listener_buckets(df)` (`src/rain_in_my_head/overview.py`). The bar click already navigates to `/dashboards/mainstream?bucket=&start=&end=`. The route renders the `Mainstream` placeholder in `web/src/pages/Placeholders.tsx`. The band thresholds are `LISTENER_BUCKETS` and `LISTENER_LABELS` in `overview.py`. See proposal.md for motivation and specs/mainstream-artists/spec.md for requirements.

The Overview's `top` lists were moved to rows and keyed by `artist_key` in #62 (`overview.py` `top_lists`). This change follows that pattern.

## Goals / Non-Goals

**Goals:**
- The page loads on its own, without the whole Overview payload.
- Band membership and the share match the chart exactly.
- Rows use the same `DataTable` as the Genre and New artists pages.

**Non-Goals:**
- A band picker on the page. Going between bands is done from the Overview.
- Any change to the Streamlit dashboard.
- Any change to the chart's thresholds or labels.

## Decisions

**1. A new `GET /api/mainstream` endpoint, not a field on `/api/overview`.** The Overview payload already does a lot of work. A separate endpoint lets the page load one band's artists directly from a link, and it can be cached and tested on its own. *Alternative considered:* add the artist list to `/api/overview` for every band. Rejected: it adds rows to every Overview load that nobody sees.

**2. Group by `artist_key`, not by display name.** Same reason as #62: a row's play count then matches the Artist page, which sums by key. The name is the first spelling seen.

**3. The band of an artist comes from its listener count, using `pd.cut` with the same `LISTENER_BUCKETS` and `LISTENER_LABELS`.** Reusing the chart's own constants keeps the two in step. The listener count is taken from the artist's first non-null `artist_listeners` value in the range.

**4. The share uses the same denominator as the chart.** The chart divides by the plays with a known listener count (`known` in `listener_buckets`). The page does too, so the share equals the bar.

**5. The page uses the Overview's range.** It reads `start` and `end` from the address. If they are missing, it uses all time (`data_bounds`). The Overview always sends both.

**6. Access uses the existing `mainstream` key.** `API_ACCESS` gets `("GET", "/api/mainstream"): frozenset({"mainstream"})`, so the rule matches the page. `check_routes()` refuses to start if the route is missing from the table.

**7. Band names come from the URL, validated against the five labels.** An unknown band returns 422 from the API and shows a notice on the page. This keeps the route from answering for arbitrary text.

## Risks / Trade-offs

- **An artist's listener count can differ between rows** → Taking the first non-null value gives one number per artist, which matches what the chart's bucketing sees per play only if the count is stable. Mitigation: check in the unit test that a stable count gives one band; note any case that differs in the PR.
- **A long artist list in one band** → The `5M+` band may hold many rows. Mitigation: `DataTable` with `maxHeight`, as the Genre page does.
- **Chart and page drift if thresholds change** → Mitigation: both read the same constants in `overview.py`.

## Migration Plan

No data migration. Deploy the API and web change together: the page calls the new route. Rollback is reverting the PR; the Overview's link already exists and the old placeholder page has no data calls.

## Open Questions

None.
