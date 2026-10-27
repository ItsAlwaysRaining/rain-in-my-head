"""Schema: the listening database as a map of table cards you can drag around. The layout is saved
next to the database in schema_layout.json (gitignored)."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from shared import require_db

from rain_in_my_head import config
from rain_in_my_head import schema_info as si

LAYOUT_PATH = si.layout_path(config.DB_PATH)
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


@st.cache_data
def read_schema(db_mtime: float) -> list[dict]:
    return si.read_schema(config.DB_PATH)


def build_data(schema: list[dict], saved: dict[str, dict]) -> dict:
    return {**si.build_data(schema, saved), "status": st.session_state.get("schema_status", "")}


mtime = require_db()
st.caption(
    "Every table and view in `listening.db`. Drag a card by its header to move it; "
    "the layout is saved for next time. Hover over a card to see what it links to."
)

schema = read_schema(mtime)
if not schema:
    st.info("The database has no tables yet. Run `uv run rain-in-my-head build` first.")
    st.stop()
names = {o["name"] for o in schema}


def _on_layout() -> None:
    # Runs before the rerun, so the status below reaches the page in the same run.
    layout = st.session_state["schema_map"].get("layout") or {}
    try:
        si.save_layout(LAYOUT_PATH, layout.get("positions") or {}, names)
        st.session_state["schema_status"] = "Layout saved"
    except OSError as e:
        st.session_state["schema_status"] = f"Couldn't save the layout: {e.strerror}"


_schema_map()(key="schema_map", data=build_data(schema, si.load_layout(LAYOUT_PATH)), on_layout_change=_on_layout)
