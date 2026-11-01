# Contract: the `viewer` commands (additions)

Extends [phase 4's commands](../../011-viewer-access/contracts/cli.md). Run on the owner's Mac or, for `prune` and `export`, in the nightly workflow. Every command takes `--env dev|prod` (default `dev`) and prints `[dev]` or `[prod]` on its first line. They read the owner URL from `VIEWERS_OWNER_URL_DEV` or `VIEWERS_OWNER_URL_PROD`. A missing value ends the command with a message naming the variable, never its value.

| Command | What it does | Output |
|---|---|---|
| `viewer init` (changed) | As before, and also makes `usage_events`, its two indexes and the app role's grants. Safe to run again. | `[dev] ready: 5 tables, role rain_app` |
| `viewer usage [--range 7d\|30d\|12m] [--person NAME]` | Prints the Visitors report: one row per person, then the free-plan section. With `--person`, prints that person's latest 200 records instead. | Tables, with the same numbers as the Visitors page |
| `viewer prune` | Deletes `usage_events` rows older than 12 months. Deletes nothing else. | `[prod] deleted 132 usage records older than 12 months` |
| `viewer export DIR` | Writes `usage_events.csv` and `viewers.csv` into `DIR` (made if missing). Files are byte-identical when nothing changed. | `[prod] wrote 2 files: 1840 usage records, 9 people` |

## `viewer usage`

```text
[prod] usage, last 30 days (UTC)

name   tier     last login        visits  time     top pages               features            limit hits
Sam    guest    30 Oct 18:02       14     38m      genre 9, overview 3     genre-songs 21      0
Robin  trusted  31 Oct 09:40       31     1h 12m   analyst 18, genre 8     query 44, ...       2

free plan, November 2026 (UTC)
  recorded requests         412
  time on heavy pages       1h 27m
  visitor database          8.7 MB of <limit>
  Vercel processing time is shown only on Vercel's own dashboard.
```

Time is an estimate from the browser (spec assumption), and the output says so in its last line.

## `viewer export`

Columns are listed in [data-model.md](../data-model.md#what-the-export-contains). Rows are ordered by `at`, then by id, so an unchanged database gives identical files. No code, code hash, session or address is written.

## Errors

One plain line and exit code 1: an unknown name for `--person`, an unknown range, a missing owner URL (names the variable) and a database that can't be reached. `prune` and `export` never print a connection string.

## The nightly workflow

`.github/workflows/analytics.yml`, on a nightly schedule and by hand. It runs `viewer prune` and `viewer export` for prod, then replaces the `analytics` branch with one new commit holding the two files, only if they differ from the branch's current files. A manual run may choose `dev`, which writes the branch `analytics-dev` instead. It never writes to any other branch.
