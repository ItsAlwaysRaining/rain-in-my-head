# Data Model: Schema Page

No database change. The page reads the schema and keeps one small file.

## Read from the database (live)

| Item | Source | Fields |
|---|---|---|
| Object | `SELECT name, type FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%'` | `name`, `kind` (`table` or `view`) |
| Column | `PRAGMA table_info('<name>')` | `name`, `type` (empty for some view columns), `required` (`notnull = 1`), `key` (`pk > 0`) |
| Row count | `SELECT COUNT(*) FROM "<name>"` (tables only) | `rows` |

## Written by hand (`dashboard/schema_notes.py`)

| Item | Fields |
|---|---|
| Table note | `title` (plain-English name), `source` (`history`, `details`, `spotify`, `view`), `description`, `columns` (`{column: meaning}`) |
| Link | `from` (`table`, `column`), `to` (`table`, `column`), `label` (e.g. "many plays → 1 track") |
| Lineage | `(view, reads_from)` pairs |
| Default position | `{name: (x, y)}` in map pixels |

A column is marked as a link when it appears in the `from` side of a link. Notes for tables or
columns that are not in the database are skipped.

## Layout file (`data/schema_layout.json`)

```json
{"positions": {"scrobbles": {"x": 40, "y": 40}, "tracks": {"x": 500, "y": 40}}}
```

- Written whole on every finished move or reset.
- Read rules: a missing, unreadable or invalid file means "no saved layout". Entries for unknown
  names, or whose `x`/`y` are not finite numbers, are dropped. Positions are clamped into the map.
- Object without a saved or default position: placed in the first free slot of a grid below the
  default layout.
