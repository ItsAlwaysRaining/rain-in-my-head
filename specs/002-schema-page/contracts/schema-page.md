# Contract: Schema Page

## Menu and address

- Menu entry "Schema", icon `:material/schema:`, after "SQL". Address `/schema`.

## What the page shows

1. Title "Schema", one line saying what the map is and how to move cards.
2. Toolbar: zoom out, zoom level, zoom in, "Fit to screen", "Show how views are built" (off),
   "Reset layout" (click twice within 3 seconds to confirm), and a save status line.
3. The map: one card per object, link lines, and a legend for the four data sources.
4. No database: `st.info("No database yet. Run `uv run listening build` first.")` and nothing else.
   A database with no tables: `st.info("The database has no tables yet. Run `uv run listening build` first.")`.

## Card

- Header (the whole header is the drag handle and is keyboard-focusable): plain-English title (or
  the real name if there is no note), real name in monospace, data source, row count (tables only).
- Description, or "No description yet".
- One row per column: name, type, tags (ID, LINK, optional), meaning or "No description yet".

## Component data (Python → browser)

```json
{
  "objects": [{"name": "scrobbles", "kind": "table", "title": "Plays", "source": "history",
               "description": "…", "rows": 218142,
               "columns": [{"name": "played_at", "type": "INTEGER", "key": true,
                            "required": true, "link": false, "meaning": "…"}]}],
  "links": [{"from": ["scrobbles", "track_key"], "to": ["tracks", "track_key"], "label": "many plays → 1 track"}],
  "lineage": [["scrobbles", "v_plays"]],
  "positions": {"scrobbles": {"x": 40, "y": 40}},
  "defaults": {"scrobbles": {"x": 40, "y": 40}}
}
```

`positions` holds every object (saved, else default, else free slot). `defaults` is what reset
returns to.

## Component trigger (browser → Python)

- `layout`: `{"positions": {name: {"x": int, "y": int}}}`, sent once when a drag ends, 600 ms after
  the last arrow-key move, and on reset. Python validates it and writes the layout file.
