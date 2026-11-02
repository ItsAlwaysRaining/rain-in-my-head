# Data Model: Usage tracking and a fair-use limit

All of this lives in the visitor database (Neon), next to the four tables from [phase 4](../011-viewer-access/data-model.md). Nothing here touches `data/listening.db` or `data/public.db`, so the Analyst page can't reach it.

## `usage_events` (new)

One row per thing a person did. Written by the hosted site's role; read by the owner's role; deleted only by the owner's role (`viewer prune`).

| Column | Type | Notes |
|---|---|---|
| `id` | bigint, generated | Primary key. Not exported. |
| `viewer_id` | bigint | References `viewers.id`, `on delete cascade` like the other tables. People are never deleted, only revoked, so history stays (FR-023). |
| `kind` | text | `view`, `time`, `feature` or `limit`. A check constraint allows only these. |
| `page` | text, null | The page key (`genre`, `analyst`, ...), from the same list as `access.PAGES`. Set for all four kinds. |
| `feature` | text, null | For `feature`: `query` (a pre-defined query run) or `genre-songs` (a genre's song list). For `limit`: `minute` or `day`. |
| `detail` | text, null | For a `feature` of `query`: the pre-defined query's name. Otherwise null. Never anything the visitor typed. |
| `visit` | text, null | The browser's random id for one page visit, joining an `open` view to its `time` row. 8 to 32 letters and digits. |
| `seconds` | integer, null | For `time`: seconds on the page, 0 to 1800. |
| `at` | timestamptz | `default now()`. Set by the database, never by the browser. |

**Indexes**
- `usage_events_viewer_kind_at (viewer_id, kind, at desc)`: serves the limit counts, the report, and the 5-second view check.
- `usage_events_at (at)`: serves `viewer prune`.

**Grants**
- `rain_app` (the hosted site): `INSERT`, and `SELECT` on `viewer_id`, `kind`, `page`, `at` only. Those are the columns the limit and the dedupe checks read. No `UPDATE`, no `DELETE`.
- The owner role owns the table and does everything else.

## Rules

- **Who is recorded**: only a logged-in person. A request refused for any reason leaves no row (FR-004). The one exception is a `limit` row, which records the refusal itself (FR-012).
- **`view`**: written when the browser reports `open`. Dropped if the same person opened the same page less than 5 seconds ago. The page key must be one the person can open (`access.pages_for`).
- **`time`**: written when the browser reports `leave`. `seconds` is clamped to 0 to 1800. A `leave` with an unknown `visit` is still stored, because the open report may have been lost.
- **`feature`**: written together with the limit check (see [research R1](research.md#r1-one-table-for-every-record-and-the-limit-counted-from-it)). `page` is the page that makes the request (`analyst` for a query, `genre` for song lists).
- **`limit`**: written when a heavy request is refused, unless the person has a `limit` row from the last minute. `feature` says which limit (`minute` or `day`).
- **Browser-report cap**: more than 120 `view` and `time` rows in a minute for one person are dropped before they are written. This produces no row (FR-030).
- **No IP, no code**: no column can hold one, and nothing in the code writes a request header or a cookie into a row.
- **Retention**: `viewer prune` deletes rows with `at` older than 12 months.
- **Dev and prod**: separate Neon branches, so separate tables (FR-029).

## State and limits

```text
heavy request ──► refused by tier/other rule ──► 403, no row
      │
      ▼
 count last minute < 30 and today < 1000 ?
      │ yes                          │ no
      ▼                              ▼
 feature row written          429 with the wait
 request runs                 limit row written (at most one per minute)
```

The counts are rolling: the minute counts rows from the last 60 seconds, and the day counts rows since 00:00 UTC.

## What the report reads

These are shapes the owner sees, not stored tables.

| Report part | Built from |
|---|---|
| Per person: last login, visits, time on site, top pages, features, limit hits | `viewers.last_login_at`, and counts and sums over `usage_events` in the chosen range (7 days, 30 days or 12 months) |
| One person's recent activity | their `usage_events` rows, newest first |
| Free-plan figures | this UTC month's `view`, `feature` and `limit` counts, the sum of `seconds` on `genre` and `analyst`, and `pg_database_size(current_database())` |

## What the export contains

| File | Columns |
|---|---|
| `usage_events.csv` | `viewer`, `kind`, `page`, `feature`, `detail`, `visit`, `seconds`, `at` (viewer is the person's name, rows ordered by `at` then `id`) |
| `viewers.csv` | `name`, `tier`, `status`, `pages`, `created_at`, `revoked_at`, `last_login_at` |

Neither file has a code, a code hash, a session or an address.
