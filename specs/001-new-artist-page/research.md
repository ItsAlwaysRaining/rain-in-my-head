# Research: New Artists and Artist Page

No NEEDS CLARIFICATION items were left in the Technical Context. These are the decisions that needed
checking.

## Where shared helpers live

- **Decision**: a new `dashboard/lastfm_art.py`, imported by pages as `from lastfm_art import ...`.
- **Rationale**: Streamlit adds the entry script's folder (`dashboard/`) to `sys.path`. Checked with
  a throwaway app: a page under `views/` imported a module beside `app.py` without errors.
- **Alternatives considered**: `src/listening/` (would make the CLI package carry dashboard-only
  code); a `views/_common.py` (Streamlit treats files in `views/` as page candidates, which is
  confusing).

## Hiding the artist page from the menu

- **Decision**: `st.Page("views/artist.py", url_path="artist", visibility="hidden")`, opened with
  `st.switch_page(..., query_params=...)`.
- **Rationale**: Streamlit 1.65's `st.Page` supports `visibility`. Checked with the throwaway app:
  `switch_page` reached a hidden page and its query parameters arrived.
- **Alternatives considered**: a visible page with an artist picker (the spec says not in the menu).

## Placeholder image

- **Decision**: a small inline SVG data URI (music note in `#9995E4` on `#202030`, the theme's iris
  and iris-surface), used by the image columns and the large cover.
- **Rationale**: no external file or request (Principle V), matches the dark theme (Principle VI).
  Streamlit's image column accepts data URLs, which needs confirming in the browser.
- **Alternatives considered**: Last.fm's grey-star image (that is exactly what the spec treats as
  "missing"); a blank cell (fails SC-003).

## Which period and which plays

- **Decision**: the list's period is the selected over-time period (already narrowed into
  `start`/`end` on the Overview), otherwise `max(start, first of end's month)` to `end`. "New" uses
  `artist_first_play`, which the Overview already computes over all data. The plays shown are the
  artist's plays within the period.
- **Rationale**: matches FR-002 and the owner's choice; reuses existing columns.

## Clicking a row

- **Decision**: `st.dataframe(..., on_select="rerun", selection_mode=["single-row", "single-cell"])`,
  then `st.switch_page` on a selection, the same pattern as the Genre page's artist table.
- **Rationale**: cell selection makes a click anywhere on the row count (the bug fixed in PR #2).
