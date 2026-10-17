# Data Model: Rename to rain-in-my-head

No database, schema or raw-file change. The "model" here is the set of names and where each form
is used.

## Name forms

| Form | Value | Used for |
|---|---|---|
| Repository / distribution / command | `rain-in-my-head` | GitHub repo, `pyproject.toml` `name`, `[project.scripts]`, `argparse` `prog`, README commands, workflow, User-Agent, `web/package.json` (`rain-in-my-head-web`) |
| Import name | `rain_in_my_head` | `src/rain_in_my_head/`, every `import`, uvicorn target `rain_in_my_head.api:app`, hatch `packages` |
| Display name | Rain in My Head | Browser tab titles, app headings, FastAPI title, README heading, constitution title, palette page |

## Kept as they are (FR-007, FR-009)

| Name | Why |
|---|---|
| `data/listening.db` | Describes the data; renaming means moving the owner's database |
| `LISTENING_DB`, `LISTENING_RAW_DIR` | Settings that point at that data; not set anywhere today |
| `data/raw/lastfm/`, `data/.spotify_token.json`, `data/schema_layout.json`, `.env` | No old name in them; must not change |
| `spotify.py`, `playlist.py`, Playlists page, `spotify_matches` | The real Spotify integration |
| "listening history", "listening days", etc. | Describe listening, not the app |

## Historical records (left as written)

- `specs/002-schema-page/` (all), `specs/003-typescript-dashboard/` done tasks T001–T025, its
  research, data model and plan
- `openspec/changes/archive/`
- Past entries in `docs/streamlit-vs-typescript.md` (the general intro is updated)
