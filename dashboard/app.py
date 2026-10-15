"""Dashboard entry point. Run: uv run streamlit run dashboard/app.py"""

import streamlit as st

st.set_page_config(page_title="Listening", page_icon=":material/graphic_eq:", layout="wide")
st.navigation([
    st.Page("views/overview.py", title="Overview", icon=":material/bar_chart:", default=True),
    st.Page("views/genre.py", title="Genre", icon=":material/category:", url_path="genre"),
    st.Page("views/sql.py", title="SQL", icon=":material/database:", url_path="sql"),
    st.Page("views/schema.py", title="Schema", icon=":material/schema:", url_path="schema"),
    st.Page("views/playlists.py", title="Playlists", icon=":material/queue_music:", url_path="playlists"),
]).run()
