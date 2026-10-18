"""Ad-hoc SQL against the listening database (read-only)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from rain_in_my_head import config
from rain_in_my_head import sql_examples as sq
from rain_in_my_head.sql_examples import EXAMPLES

st.title("SQL")


@st.cache_data
def schema(db_mtime: float) -> pd.DataFrame:
    return sq.schema(config.DB_PATH)


if not config.DB_PATH.exists():
    st.info("No database yet. Run `uv run rain-in-my-head build` first.")
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
        result = sq.run_readonly(config.DB_PATH, sql)
    except Exception as e:  # show SQL errors inline rather than crashing the page
        st.error(str(e))
    else:
        st.caption(f"{len(result):,} rows")
        st.dataframe(result, hide_index=True, width="stretch")
        st.download_button("Download CSV", result.to_csv(index=False), "query.csv", "text/csv")
