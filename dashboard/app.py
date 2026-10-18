"""Dashboard entry point. Run: uv run streamlit run dashboard/app.py"""

from pathlib import Path

import streamlit as st

# The tab icon is shared with the TypeScript app (web/index.html links the same file)
FAVICON = Path(__file__).resolve().parent.parent / "web" / "public" / "favicon.svg"

st.set_page_config(page_title="Rain in My Head", page_icon=str(FAVICON), layout="wide")
st.navigation([
    st.Page("views/overview.py", title="Overview", icon=":material/bar_chart:", default=True),
    st.Page("views/genre.py", title="Genre", icon=":material/category:", url_path="genre"),
    st.Page("views/sql.py", title="SQL", icon=":material/database:", url_path="sql"),
    st.Page("views/schema.py", title="Schema", icon=":material/schema:", url_path="schema"),
    st.Page("views/playlists.py", title="Playlists", icon=":material/queue_music:", url_path="playlists"),
]).run()
