# Research: Schema Page

## R1. How to draw a draggable map inside Streamlit and get positions back

**Decision**: a Streamlit `st.components.v2` component, defined with inline `html`, `css` and `js`.
Python passes the schema, notes and saved positions as `data`; the JS calls
`setTriggerValue("layout", positions)` when a move finishes, and the page's
`on_layout_change` callback writes the file.

**Rationale**: `components.v2` is in the installed Streamlit 1.65 (checked:
`streamlit.components.v2.component(name, *, html, css, js, isolate_styles)`; the mount call takes
`key`, `data`, `default`, `width`, `height` and `on_<name>_change` callbacks). It needs no build
step or package, and it is two-way, unlike `st.components.v1.html`.

**Alternatives considered**:
- `components.v1.html`: one-way only, so positions could only live in the browser (rejected by the
  owner's choice of saving in `data/`).
- A v1 custom component with a React build: needs Node and a build step, against Principle IV.
- Altair or another chart with drag: no free dragging of rich HTML cards.

**To confirm while implementing (T004)**: whether the JS default function runs again on each rerun
(it must not reset a card mid-drag), and that a trigger value reaches the callback once per move.

## R2. Where the component's CSS and JS live

**Decision**: `dashboard/schema_map/map.css` and `map.js`, read with `Path.read_text()` and passed
inline.

**Rationale**: `components.v2` accepts file paths only for components installed as packages with
an `asset_dir`; this repo's dashboard is not a package. Separate files keep the page module short
and give editors syntax highlighting.

## R3. What is read live and what is written by hand

**Decision**:
- Live from SQLite: object names and kinds (`sqlite_master`), columns, types, "required" and
  "primary key" flags (`PRAGMA table_info`), and table row counts (`COUNT(*)`).
- By hand in `dashboard/schema_notes.py`: plain-English names and descriptions, data sources,
  column meanings, which columns link to which, view lineage, default positions.

**Rationale**: the database declares no foreign keys, so links cannot be read. The "can be blank"
and "identifies a row" marks come from `notnull` and `pk`, so they stay right as the schema changes.
A link or note naming a column that no longer exists is skipped, so stale notes cannot break the page.

## R4. Saving the layout

**Decision**: `data/schema_layout.json`, written to a temporary file and renamed, so a crash cannot
leave half a file. Read with validation: anything that is not a `{name: {x, y}}` map of numbers is
ignored. Added to `.gitignore`.

**Rationale**: the owner asked for the `data/` folder; the constitution requires nothing in `data/`
except `data/raw/` to be committed, and the current `.gitignore` does not cover `*.json` there.

## R5. Theme

**Decision**: colors from `.streamlit/config.toml`: page `#18181C`, card `#202030`, lines `#4C4C54`,
text `#E4E4EA` and muted `#AAAAB4`. Data sources use the chart colors: Last.fm history iris
`#7F77D6`, Last.fm details teal `#0E9A94`, Spotify coral `#CD6153`. Views get a dashed iris
`#9995E4` border.

**Rationale**: Principle VI; the chart colors were already checked for color-blind separation on
the dark page.

## R6. Performance

Measured on the real database: all `PRAGMA table_info` calls take under 1 ms; all five row counts
take about 170 ms uncached. Both are cached with `st.cache_data` keyed on the database file's
modification time, as `dashboard/views/sql.py` already does.
