# Rain in My Head

Personal listening history from Last.fm (scrobbled from Spotify), stored in SQLite and explored in two dashboards. Formerly `spotify-music-analysis`. See [Renamed from spotify-music-analysis](#renamed-from-spotify-music-analysis).

- `data/raw/lastfm/YYYY-MM.jsonl` holds every scrobble. It's the source of truth, committed to git and appended to by GitHub Actions every 6 hours.
- `data/listening.db` is a SQLite database rebuilt from the raw files. It's gitignored.

## Setup

```sh
brew install uv
cp .env.example .env        # add your LASTFM_API_KEY and LASTFM_USER
uv sync
```

If "hide recent listening" is enabled on your Last.fm profile, turn it off. The API key alone can't read hidden history.

## Usage

```sh
uv run rain-in-my-head fetch      # first run backfills your whole account, then only new scrobbles
uv run rain-in-my-head build      # load raw JSONL into SQLite (safe to rerun)
uv run rain-in-my-head enrich     # Last.fm durations, listener counts and genre tags; resumable, --limit N
uv run rain-in-my-head stats      # counts, enrichment coverage, suspicious scrobble bursts
uv run streamlit run dashboard/app.py
```

The first `enrich` makes about one call per unique track and two per unique artist, at roughly 2 per second in practice. For about 76k tracks and 24k artists that is around 15 hours, so use `--limit` or leave it running overnight. It's safe to Ctrl-C and rerun. Later runs only look up new items.

## Two dashboards

There are two dashboards over the same database, kept side by side to compare them. They show the same numbers because both use the functions in `src/rain_in_my_head/` (`overview.py`, `genre.py`, `sql_examples.py`, `schema_info.py`, `playlist.py`). The Schema page's card layout (`data/schema_layout.json`) is shared too, so a card moved in one app is moved in the other. The browser-tab icon is shared as well: both apps use `web/public/favicon.svg`.

| | Streamlit | TypeScript |
|---|---|---|
| Code | `dashboard/` | `web/` (Vite + React) and its JSON API, `src/rain_in_my_head/api.py` |
| Run | `uv run streamlit run dashboard/app.py` | `cd web && npm install && npm run build`, then `uv run rain-in-my-head serve` |
| Open | http://localhost:8501 | http://localhost:8000 |
| Pages | Overview, Genre, SQL, Schema, Playlists | The same pages, laid out as the Figma prototype: Dashboards (Overview, with New artists, Genre and Artist under it), Playlist Generator, and Analyst (SQL and Schema on one page) |
| Navigation | Sidebar, with the Overview's filters in it | Top bar and breadcrumbs, with the filters on the page |

Both can run at the same time. `uv sync` installs what both need (the `dashboard` and `web` groups). The TypeScript app also needs Node 22 or newer.

To work on the TypeScript app with hot reload, run `uv run rain-in-my-head serve --dev` (API only) and `npm run dev` in `web/`, then open http://localhost:5173.

[docs/streamlit-vs-typescript.md](docs/streamlit-vs-typescript.md) records how building each page went in each app.

The TypeScript app follows the Figma prototype (`specs/005-prototype-redesign`), so its addresses differ from Streamlit's: `/dashboards`, `/dashboards/new-artists`, `/dashboards/genre`, `/dashboards/artist`, `/playlists` and `/analyst`. The old `/genre`, `/artist`, `/sql` and `/schema` addresses redirect. The home page (`/`) is the prototype's landing page: the Rain Girl artwork with flickering rain, where clicking the lightning bolt opens **Storm** (`/storm`): full-window rain, with a Thunder switch that turns on rain and thunder sounds (made in the browser, no audio files) and lightning. Storm always opens silent. **About** (`/about`) has a photo beside About Me and About This App. The photo is `web/public/about/photo.jpg`, and until it's added the page shows an empty frame. **Contact Me** (`/contact`) lists Email, LinkedIn, GitHub and Last.fm, with Send email and Download CV. The CV is `web/public/contact/cv.pdf`; replace that file to update it. Pages from the prototype that aren't built yet show a **Coming soon** card that links to their GitHub issue: the listening-slot drill-down (#30), mainstream vs. niche artists (#12), the AI (#32) and SQL (#31) playlist types.

## Filter by period

On the **Overview**, click a bar in the "Scrobbles per month" chart (or the week, year or hours version) to show just that period. Every other figure and chart on the page then shows only that period, and the KPI changes compare it with the period of the same length just before it. The bar chart keeps every period, with the clicked bar highlighted, so you can click another one straight away.

Inside a clicked month or week, the "New artists" and genre charts plot per day. Inside a clicked year, they plot per month. The "New artists in …" table lists the clicked period's new artists (see [New artists and the Artist page](#new-artists-and-the-artist-page)). Clicking a genre chart opens the Genre page for the clicked period.

To see the whole range again, click **Show whole range** or the chart's background. Changing the sidebar range or time grain also clears the selection. "#1 per year" always covers all years.

## Genre drill-down

On the **Overview**, click any of the genre charts to open the **Genre** page for that genre and date range. It lists the artists in the genre by your play count, most played first. Click an artist to see the songs you've played by them, also most played first. Artists and songs show album art.

You can also open **Genre** from the sidebar and pick any genre from the dropdown. Opened that way, it covers all time.

- The genre needs `enrich` to have run. An artist belongs to one genre, their top Last.fm tag.
- Album art is the cover Last.fm saved with each scrobble, so it needs no extra API calls. An artist's picture is the cover they appear with most. Last.fm's grey "no image" placeholder is hidden.

## New artists and the Artist page

On the **Overview**, under the "New artists per …" chart, the **New artists in …** table lists the artists you heard for the first time ever in the latest month the sidebar range reaches, most played first. If you've clicked a bar in the over-time chart, it lists that period's new artists instead.

Click anywhere on an artist's row to open their **Artist** page. It shows their cover, how many times you played them in that period and in all, and every song of theirs you played in the period, most played first. The page has its own address (`/artist?artist=…&start=…&end=…`), so it can be bookmarked; without `start` and `end` it covers all time. It isn't in the menu. **Overview** at the top goes back.

Both dashboards have the list and the page, with the same numbers (`src/rain_in_my_head/artist.py`). Missing album art shows a music-note placeholder, `web/public/no-art.svg`, shared by both apps.

## Scheduled sync (GitHub Actions)

1. Push this repo to a **private** GitHub repository. It contains your listening history.
2. Add the repo secrets `LASTFM_API_KEY` and `LASTFM_USER` (Settings → Secrets and variables → Actions).
3. Run the "Sync scrobbles" workflow once by hand from the Actions tab. After that it runs every 6 hours.
4. Locally: `git pull && uv run rain-in-my-head build && uv run rain-in-my-head enrich` to refresh the database.

## Renamed from spotify-music-analysis

The project was called `spotify-music-analysis`, with a package and command called `listening`. It is now `rain-in-my-head` everywhere: the repository, the `rain-in-my-head` command and the `src/rain_in_my_head/` package. The database is still `data/listening.db`, and the `LISTENING_DB` and `LISTENING_RAW_DIR` settings keep their names, so no data moves.

One-off steps on a machine with an existing clone:

1. `git pull`, then `uv sync`. This removes the old `listening` command and installs `rain-in-my-head`.
2. Check the remote: `git remote -v` should show `ItsAlwaysRaining/rain-in-my-head`. If it doesn't, run `git remote set-url origin https://github.com/ItsAlwaysRaining/rain-in-my-head.git`. GitHub redirects the old URL either way.
3. Optionally move the folder to match. Close any Claude Code session in it first. Claude's project memory is stored under a folder named after the clone's path, so move that too:

   ```sh
   cd ~/Documents/claude_projects
   mv spotify-music-analysis rain-in-my-head
   mv ~/.claude/projects/-Users-oliver-Documents-claude-projects-spotify-music-analysis \
      ~/.claude/projects/-Users-oliver-Documents-claude-projects-rain-in-my-head
   cd rain-in-my-head && uv sync   # .venv records the old path
   ```

4. Optionally rename the Spotify app at developer.spotify.com/dashboard → your app → **Settings** → **Edit**. Spotify identifies the app by its client ID, so `.env` and the saved login don't change.

## Design

Every page of the TypeScript app is designed in Figma before it's built.

- [Rain in My Head: Design process](https://www.figma.com/design/1rbbEne7pW8oA2JCNmjhrm) (Figma). Pages: 0 Cover, 1 Research, 2 Wireframes, 3 Prototype, 4 Visual design and 5 States. Its Color and Spacing variables and text styles mirror `web/src/theme.css`, so a token change goes in both places.
- [Design reference](https://claude.ai/artifact/SYxFoSaCHYddYzBtnAKT1M): the palette, type, spacing, writing rules and interaction states on one page.

The Figma file is private while the project is in progress and will be made public when it's finished. The About page links to it too.

## Notes

- Minutes listened are estimated from track durations. Plays with an unknown duration count as 3.5 minutes.
- Track names are normalized so that "Song - Remastered 2011" and "Song (feat. X)" count as "Song". Live versions stay separate.
- Genres are each artist's top Last.fm tag, with junk tags like "seen live" filtered out.
- Local-time columns (hour, weekday) use the timezone of the machine running the query.

## Spotify playlists

Turn a time slot into a Spotify playlist of the tracks that are **distinctive** to it. For each track, the ranking compares the share of its plays that fall in the slot with the slot's share of all your plays (lift), shrunk toward average for tracks with few plays.

One-time setup (Spotify requires the app owner to have **Premium**):

1. Go to developer.spotify.com/dashboard → **Create app**. Use any name. Add the redirect URI `http://127.0.0.1:8888/callback` (Spotify rejects `localhost`) and tick **Web API**.
2. Copy the **Client ID** into `.env` as `SPOTIFY_CLIENT_ID=...`. No client secret is needed (PKCE login).
3. Run `uv run rain-in-my-head spotify-login` and approve in the browser. The token is saved to `data/.spotify_token.json`, which is gitignored.

Then use the **Playlists** page in the dashboard, or the CLI:

```sh
uv run rain-in-my-head playlist --days fri --hours 17-19 --dry-run        # preview the ranking
uv run rain-in-my-head playlist --days fri --hours 17-19                  # create "Fridays 5pm–7pm"
uv run rain-in-my-head playlist --days weekends --hours 22-2 --since 2024-01-01 --size 30 --min-plays 2

# songs first heard in a given year: most played that year (default) or most played since (--rank-by ever)
uv run rain-in-my-head discoveries --year 2019 --dry-run
uv run rain-in-my-head discoveries --year 2019 --rank-by ever --chronological

# songs you binged (8+ plays within 7 days by default), oldest binge first; --dry-run lists every binge with dates
uv run rain-in-my-head binges --dry-run
uv run rain-in-my-head binges --since 2023 --min-plays 10 --order newest   # or --order biggest
```

Hours are local time, and the end hour is exclusive. Playlists are private by default. Spotify matches are cached in the `spotify_matches` table, so each track is only searched once.
