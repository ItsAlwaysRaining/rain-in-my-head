# Quickstart: verify the Schema page

Run the dashboard: `uv run streamlit run dashboard/app.py --server.headless true --server.port 8599`.
Drive it with headless Chrome (`uv run --no-project --with playwright python <script>`,
`channel="chrome"`). Move `data/schema_layout.json` aside first and put it back afterwards.

## Scenario 1: menu and cards (US1)

1. Open `/`. The sidebar menu shows "Schema" after "SQL". Click it; the address is `/schema`.
2. Count the cards: 7 (5 tables, 2 views).
3. Cross-check in SQLite: every name from `sqlite_master` has a card, every column from
   `PRAGMA table_info` is listed on it, and each table's row count equals `SELECT COUNT(*)`.

## Scenario 2: links, hover and lineage (US1)

1. Five link lines are drawn, each with its label.
2. Hover over the Plays card: its two links and the `track_key`/`artist_key` rows highlight.
3. Tick "Show how views are built": five dashed lines appear. Untick: they go.

## Scenario 3: drag and keep (US2)

1. Drag the Plays card's header 300 px right and 100 px down. The card and its lines move.
2. `data/schema_layout.json` now exists and gives Plays a position 300/100 px (divided by zoom) from
   where it was.
3. Focus the Track details header and press ArrowDown twice; after a moment the file shows it 40 px lower.
4. Stop and restart the server. Open `/schema` in a fresh browser context: both cards are where they
   were left.
5. Click "Reset layout" once (button asks to confirm), then again: cards return to the default
   layout, and the file holds the defaults.

## Scenario 4: stays current (US3)

1. Copy the database to a temp folder with Python's `sqlite3` `Connection.backup()` (the `sqlite3`
   CLI's `.backup` fails when the source is opened `-readonly`), then in the copy run
   `ALTER TABLE tracks ADD COLUMN bpm REAL; CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT);`.
2. Start the dashboard with `LISTENING_DB=<copy>`. `bpm` appears on Track details with
   "No description yet"; a "notes" card appears with "No description yet", "0 rows", not covering
   another card.
3. Write a layout file naming a table `gone` and with Plays at `{"x": 99999, "y": -5}`. Reload: no
   error, and Plays sits inside the map's edges.

## Scenario 5: edge cases

1. Write `not json` to the layout file and reload: default layout, no error.
2. Start with `LISTENING_DB` pointing at a missing file: the page shows the "No database yet" message.
3. `git status` does not list `data/schema_layout.json`.
