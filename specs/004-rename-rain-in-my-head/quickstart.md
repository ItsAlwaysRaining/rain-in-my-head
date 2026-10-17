# Quickstart: verify the rename

## Before the change (on `main`)

1. With `data/listening.db` built, open the Streamlit Overview (`uv run streamlit run dashboard/app.py`)
   and the TypeScript Overview (`uv run listening serve`, after `npm run build` in `web/`). Note the
   KPIs for "All time" and one year.

## On the branch

2. `uv sync`, then `uv run rain-in-my-head --help` shows `usage: rain-in-my-head`, and
   `uv run listening --help` fails.
3. Run each command from [contracts/cli.md](contracts/cli.md): `stats`, `build` (no data lost, row
   counts same as `stats` before), `enrich --limit 1`, `fetch`, `playlist --days fri --hours 17-19 --dry-run`.
   `spotify-login` is not re-run; the dry run and the Playlists page show the token still works.
4. `uv run --no-default-groups rain-in-my-head fetch` works in a clean environment
   (`uv venv /tmp/… && UV_PROJECT_ENVIRONMENT=… uv run --no-default-groups …`), as the workflow runs it.
5. Restart Streamlit and `rain-in-my-head serve`; in headless Chrome:
   - both tab titles read "Rain in My Head", and both Overview headings too;
   - the Overview KPIs equal step 1's for the same periods, and one matches
     `sqlite3 data/listening.db "SELECT COUNT(*) FROM scrobbles"`;
   - Genre, SQL, Schema and Playlists pages open without errors;
   - with `LISTENING_DB=/nonexistent`, the "No database yet" messages quote `uv run rain-in-my-head`.
6. `cd web && npx tsc --noEmit && npm run build` is clean.
7. `git grep -n -i -E "listening|spotify-music-analysis"`: every remaining match is in the kept or
   historical lists in [data-model.md](data-model.md). `git diff main --stat -- data/raw` is empty.

## After merge (Claude, then the owner)

8. Claude: rename the repo, set the description, update the remote (research §6). `git remote -v`
   shows `rain-in-my-head`; `git fetch` works; github.com/ItsAlwaysRaining/spotify-music-analysis
   redirects.
9. Next scheduled sync (or a manual "Sync scrobbles" run): succeeds.
10. Owner: move the folder and memory folder, `uv sync` (research §7); a new Claude session in the
    new folder recalls the "Data sources" memory.
11. Owner: rename the Spotify app (research §8); a playlist dry run still works.
12. Merge `main` into `feature/new-artist-page` and update spec 001's paths there.
