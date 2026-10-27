"""Helpers used by more than one Streamlit page (constitution VI: shared, not copied).

Pages import this as `shared`: Streamlit puts dashboard/, the folder of app.py, on the import path.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from rain_in_my_head import config

ROW_HEIGHT = 56  # tall enough for a 64px Last.fm thumbnail


def require_db(title: str | None = None) -> float:
    """Stop the page with a hint if there's no database yet, under `title` if given.

    Returns the database's modification time, which the pages use as their cache key."""
    if not config.DB_PATH.exists():
        if title:
            st.title(title)
        st.info(config.NO_DATABASE)
        st.stop()
    return config.DB_PATH.stat().st_mtime


def fit_height(rows: int, most: int) -> int:
    """A table height that shows every row (plus the header), up to `most` pixels."""
    return min(most, 38 + ROW_HEIGHT * rows)


def thumb_table(df: pd.DataFrame, labels: dict[str, str], height: int, key: str | None = None):
    """A table of `df`'s `thumb` image, the `labels` columns (column -> header) and `plays`.

    With a `key`, a click selects a row; read it with `clicked_row`."""
    selectable = {}
    if key is not None:
        # Cell selection makes clicking anywhere in a row pick it, not just its checkbox.
        selectable = {"on_select": "rerun", "selection_mode": ["single-row", "single-cell"], "key": key}
    return st.dataframe(
        df[["thumb", *labels, "plays"]],
        column_config={
            "thumb": st.column_config.ImageColumn("", width="small"),
            **labels,
            "plays": st.column_config.NumberColumn("Plays", format="%d"),
        },
        hide_index=True,
        row_height=ROW_HEIGHT,
        height=height,
        **selectable,
    )


def clicked_row(table) -> int | None:
    """The row picked in a `thumb_table` with a key, or None."""
    rows = table.selection.rows or [row for row, _ in table.selection.cells]
    return rows[0] if rows else None
