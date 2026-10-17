"""Schema: the listening database as a map of table cards you can drag around. The layout is saved
next to the database in schema_layout.json (gitignored)."""

from __future__ import annotations

import json
import math
import os
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

import streamlit as st

import schema_notes as notes
from rain_in_my_head import config

LAYOUT_PATH = config.DB_PATH.parent / "schema_layout.json"
MAP_W, MAP_H = 1880, 2400
CARD_W = 300
GRID_X = [40, 500, 960, 1420]  # columns for tables with no default position
ASSETS = Path(__file__).resolve().parent.parent / "schema_map"

st.title("Schema")


@st.cache_resource
def _schema_map():
    # Registered once per server: re-registering on every rerun logs a duplicate-name warning.
    return st.components.v2.component(
        "schema_map",
        css=(ASSETS / "map.css").read_text(),
        js=(ASSETS / "map.js").read_text(),
    )


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(f"file:{config.DB_PATH}?mode=ro", uri=True)


def _quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


@st.cache_data
def read_schema(db_mtime: float) -> list[dict]:
    """Tables and views with their columns, and row counts for tables."""
    with closing(_connect()) as conn:
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
            rows = conn.execute(f"SELECT COUNT(*) FROM {_quote(name)}").fetchone()[0] if kind == "table" else None
            schema.append({"name": name, "kind": kind, "columns": columns, "rows": rows})
    return schema


def _is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _clamp(x: float, y: float) -> dict:
    return {"x": int(min(max(0, x), MAP_W - CARD_W)), "y": int(min(max(0, y), MAP_H - 120))}


def load_layout() -> dict[str, dict]:
    """Saved positions; anything missing or malformed counts as not saved."""
    try:
        raw = json.loads(LAYOUT_PATH.read_text())
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


def save_layout(positions: dict, names: set[str]) -> None:
    clean = {
        name: _clamp(p["x"], p["y"])
        for name, p in positions.items()
        if name in names and isinstance(p, dict) and _is_num(p.get("x")) and _is_num(p.get("y"))
    }
    # Write to a temp file and rename, so an interrupted save never leaves half a file.
    fd, tmp = tempfile.mkstemp(dir=LAYOUT_PATH.parent, prefix=".schema_layout.", suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump({"positions": clean}, f, indent=2, sort_keys=True)
    os.replace(tmp, LAYOUT_PATH)


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
        "status": st.session_state.get("schema_status", ""),
    }


if not config.DB_PATH.exists():
    st.info("No database yet. Run `uv run rain-in-my-head build` first.")
    st.stop()

st.caption(
    "Every table and view in `listening.db`. Drag a card by its header to move it; "
    "the layout is saved for next time. Hover over a card to see what it links to."
)

schema = read_schema(config.DB_PATH.stat().st_mtime)
if not schema:
    st.info("The database has no tables yet. Run `uv run rain-in-my-head build` first.")
    st.stop()
names = {o["name"] for o in schema}


def _on_layout() -> None:
    # Runs before the rerun, so the status below reaches the page in the same run.
    layout = st.session_state["schema_map"].get("layout") or {}
    try:
        save_layout(layout.get("positions") or {}, names)
        st.session_state["schema_status"] = "Layout saved"
    except OSError as e:
        st.session_state["schema_status"] = f"Couldn't save the layout: {e.strerror}"


_schema_map()(key="schema_map", data=build_data(schema, load_layout()), on_layout_change=_on_layout)
