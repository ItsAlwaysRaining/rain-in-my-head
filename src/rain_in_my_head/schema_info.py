"""Data for the Schema page, shared by the Streamlit view (dashboard/views/schema.py) and the API.

Every table and view with its columns, the hand-written notes, links and lineage, and the card
layout. The layout is saved next to the database in schema_layout.json (gitignored) and is shared
by both dashboards; the last save wins.
"""

from __future__ import annotations

import json
import math
import os
import tempfile
from contextlib import closing
from pathlib import Path

from rain_in_my_head import schema_notes as notes
from rain_in_my_head.build import connect_readonly

MAP_W, MAP_H = 1880, 2400
CARD_W = 300
GRID_X = [40, 500, 960, 1420]  # columns for tables with no default position


def layout_path(db_path: Path) -> Path:
    return db_path.parent / "schema_layout.json"


def _quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def read_schema(db_path: Path) -> list[dict]:
    """Tables and views with their columns, and row counts for tables."""
    with closing(connect_readonly(db_path)) as conn:
        objects = conn.execute(
            "SELECT name, type FROM sqlite_master"
            " WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        schema = []
        for name, kind in objects:
            columns = [
                {"name": c[1], "type": c[2] or "", "required": bool(c[3]), "key": c[5] > 0}
                for c in conn.execute(f"PRAGMA table_info({_quote(name)})")
            ]
            rows = conn.execute(f"SELECT COUNT(*) FROM {_quote(name)}").fetchone()[0] if kind == "table" else None  # noqa: S608 the name is quoted by _quote
            schema.append({"name": name, "kind": kind, "columns": columns, "rows": rows})
    return schema


def _is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _clamp(x: float, y: float) -> dict:
    return {"x": int(min(max(0, x), MAP_W - CARD_W)), "y": int(min(max(0, y), MAP_H - 120))}


def load_layout(path: Path) -> dict[str, dict]:
    """Saved positions; anything missing or malformed counts as not saved."""
    try:
        raw = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}
    positions = raw.get("positions") if isinstance(raw, dict) else None
    if not isinstance(positions, dict):
        return {}
    return {
        name: _clamp(p["x"], p["y"])
        for name, p in positions.items()
        if isinstance(p, dict) and _is_num(p.get("x")) and _is_num(p.get("y"))
    }


def save_layout(path: Path, positions: dict, names: set[str]) -> None:
    clean = {
        name: _clamp(p["x"], p["y"])
        for name, p in positions.items()
        if name in names and isinstance(p, dict) and _is_num(p.get("x")) and _is_num(p.get("y"))
    }
    # Write to a temp file and rename, so an interrupted save never leaves half a file.
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".schema_layout.", suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump({"positions": clean}, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def default_positions(names: list[str]) -> dict[str, dict]:
    """Defaults from the notes; anything else goes in the first free grid slot below them."""
    positions = {n: _clamp(*notes.DEFAULT_POSITIONS[n]) for n in names if n in notes.DEFAULT_POSITIONS}
    taken = {(p["x"], p["y"]) for p in positions.values()}
    slots = ((x, 1420 + row * 480) for row in range(100) for x in GRID_X)
    for name in names:
        if name not in positions:
            slot = next(s for s in slots if s not in taken)
            positions[name] = _clamp(*slot)
    return positions


def build_data(schema: list[dict], saved: dict[str, dict]) -> dict:
    """What the map draws: objects in note order, links and lineage that exist, and positions."""
    columns = {o["name"]: {c["name"] for c in o["columns"]} for o in schema}

    def exists(table: str, column: str) -> bool:
        return column in columns.get(table, ())

    links = [link for link in notes.LINKS if exists(*link["from"]) and exists(*link["to"])]
    link_columns = {link["from"] for link in links}
    order = list(notes.DEFAULT_POSITIONS)
    schema = sorted(schema, key=lambda o: (order.index(o["name"]) if o["name"] in order else len(order), o["name"]))

    objects = []
    for o in schema:
        note = notes.TABLES.get(o["name"], {})
        meanings = note.get("columns", {})
        objects.append({
            "name": o["name"],
            "kind": o["kind"],
            "title": note.get("title", o["name"]),
            "source": note.get("source", "view" if o["kind"] == "view" else None),
            "description": note.get("description"),
            "rows": o["rows"],
            "columns": [
                {**c, "link": (o["name"], c["name"]) in link_columns, "meaning": meanings.get(c["name"])}
                for c in o["columns"]
            ],
        })

    names = [o["name"] for o in objects]
    defaults = default_positions(names)
    return {
        "objects": objects,
        "links": [{"from": list(l["from"]), "to": list(l["to"]), "label": l["label"]} for l in links],
        "lineage": [list(pair) for pair in notes.LINEAGE if pair[0] in columns and pair[1] in columns],
        "positions": {n: saved.get(n, defaults[n]) for n in names},
        "defaults": defaults,
        "size": {"w": MAP_W, "h": MAP_H},
    }
