"""Ad-hoc SQL against the listening database (read-only)."""

from __future__ import annotations

import sqlite3

import pandas as pd
import streamlit as st

from rain_in_my_head import config

st.title("SQL")

EXAMPLES = {
    "Top artists this year": """SELECT artist_name, COUNT(*) AS plays, ROUND(SUM(est_minutes) / 60, 1) AS hours
FROM v_plays
WHERE year = CAST(strftime('%Y', 'now') AS INTEGER)
GROUP BY artist_name
ORDER BY plays DESC
LIMIT 25""",
    "Most-played track each year": """SELECT year, artist_name, track_name, plays FROM (
  SELECT year, artist_name, track_name, COUNT(*) AS plays,
         ROW_NUMBER() OVER (PARTITION BY year ORDER BY COUNT(*) DESC) AS rn
  FROM v_plays GROUP BY year, track_key
) WHERE rn = 1 ORDER BY year""",
    "Biggest listening days": """SELECT date(played_local) AS day, COUNT(*) AS plays
FROM v_plays GROUP BY day ORDER BY plays DESC LIMIT 20""",
    "Artists I've stopped listening to": """SELECT artist_name, COUNT(*) AS plays, MAX(date(played_local)) AS last_played
FROM v_plays GROUP BY artist_key
HAVING plays >= 100 AND last_played < date('now', '-2 years')
ORDER BY plays DESC""",
    "First play of my top 50 artists": """SELECT artist_name, MIN(date(played_local)) AS first_play, COUNT(*) AS plays
FROM v_plays GROUP BY artist_key ORDER BY plays DESC LIMIT 50""",
    "Plays by genre": """SELECT COALESCE(primary_genre, '(untagged)') AS genre, COUNT(*) AS plays
FROM v_plays GROUP BY genre ORDER BY plays DESC LIMIT 30""",
}


@st.cache_data
def schema(db_mtime: float) -> pd.DataFrame:
    with _connect() as conn:
        objects = conn.execute(
            "SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') ORDER BY type DESC, name"
        ).fetchall()
        rows = []
        for name, kind in objects:
            for col in conn.execute(f"PRAGMA table_info('{name}')"):
                rows.append({"object": f"{name} ({kind})", "column": col[1], "type": col[2]})
    return pd.DataFrame(rows)


def _connect() -> sqlite3.Connection:
    # Read-only, so a stray UPDATE/DELETE can't damage the database.
    return sqlite3.connect(f"file:{config.DB_PATH}?mode=ro", uri=True)


if not config.DB_PATH.exists():
    st.info("No database yet. Run `uv run listening build` first.")
    st.stop()

with st.expander("Tables and columns — start with `v_plays` (one row per play, everything joined)"):
    st.dataframe(schema(config.DB_PATH.stat().st_mtime), hide_index=True, width="stretch", height=350)

example = st.selectbox("Examples", list(EXAMPLES), index=None, placeholder="Load an example query…")
if example and st.session_state.get("loaded_example") != example:
    st.session_state["sql"] = EXAMPLES[example]
    st.session_state["loaded_example"] = example

sql = st.text_area("Query", key="sql", height=200, placeholder="SELECT * FROM v_plays ORDER BY played_at DESC LIMIT 20")

if st.button("Run", type="primary") and sql.strip():
    try:
        with _connect() as conn:
            result = pd.read_sql(sql, conn)
    except Exception as e:  # show SQL errors inline rather than crashing the page
        st.error(str(e))
    else:
        st.caption(f"{len(result):,} rows")
        st.dataframe(result, hide_index=True, width="stretch")
        st.download_button("Download CSV", result.to_csv(index=False), "query.csv", "text/csv")
