# Listening analytics

Personal listening history from Last.fm (scrobbled from Spotify), stored in SQLite and explored in a Streamlit dashboard.

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
uv run listening fetch      # first run backfills your whole account, then only new scrobbles
uv run listening build      # load raw JSONL into SQLite (safe to rerun)
uv run listening enrich     # Last.fm durations, listener counts and genre tags; resumable, --limit N
uv run listening stats      # counts, enrichment coverage, suspicious scrobble bursts
uv run streamlit run dashboard/app.py
```

The first `enrich` makes about one call per unique track and two per unique artist, at roughly 2 per second in practice. For about 76k tracks and 24k artists that is around 15 hours, so use `--limit` or leave it running overnight. It's safe to Ctrl-C and rerun. Later runs only look up new items.

## Filter by period

On the **Overview**, click a bar in the "Scrobbles per month" chart (or the week, year or hours version) to show just that period. Every other figure and chart on the page then shows only that period, and the KPI changes compare it with the period of the same length just before it. The bar chart keeps every period, with the clicked bar highlighted, so you can click another one straight away.

Inside a clicked month or week, the "New artists" and genre charts plot per day. Inside a clicked year, they plot per month. Clicking a genre chart opens the Genre page for the clicked period.

To see the whole range again, click **Show whole range** or the chart's background. Changing the sidebar range or time grain also clears the selection. "#1 per year" always covers all years.

## Genre drill-down

On the **Overview**, click any of the genre charts to open the **Genre** page for that genre and date range. It lists the artists in the genre by your play count, most played first. Click an artist to see the songs you've played by them, also most played first. Artists and songs show album art.

You can also open **Genre** from the sidebar and pick any genre from the dropdown. Opened that way, it covers all time.

- The genre needs `enrich` to have run. An artist belongs to one genre, their top Last.fm tag.
- Album art is the cover Last.fm saved with each scrobble, so it needs no extra API calls. An artist's picture is the cover they appear with most. Last.fm's grey "no image" placeholder is hidden.

## Scheduled sync (GitHub Actions)

1. Push this repo to a **private** GitHub repository. It contains your listening history.
2. Add the repo secrets `LASTFM_API_KEY` and `LASTFM_USER` (Settings → Secrets and variables → Actions).
3. Run the "Sync scrobbles" workflow once by hand from the Actions tab. After that it runs every 6 hours.
4. Locally: `git pull && uv run listening build && uv run listening enrich` to refresh the database.

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
3. Run `uv run listening spotify-login` and approve in the browser. The token is saved to `data/.spotify_token.json`, which is gitignored.

Then use the **Playlists** page in the dashboard, or the CLI:

```sh
uv run listening playlist --days fri --hours 17-19 --dry-run        # preview the ranking
uv run listening playlist --days fri --hours 17-19                  # create "Fridays 5pm–7pm"
uv run listening playlist --days weekends --hours 22-2 --since 2024-01-01 --size 30 --min-plays 2

# songs first heard in a given year: most played that year (default) or most played since (--rank-by ever)
uv run listening discoveries --year 2019 --dry-run
uv run listening discoveries --year 2019 --rank-by ever --chronological

# songs you binged (8+ plays within 7 days by default), oldest binge first; --dry-run lists every binge with dates
uv run listening binges --dry-run
uv run listening binges --since 2023 --min-plays 10 --order newest   # or --order biggest
```

Hours are local time, and the end hour is exclusive. Playlists are private by default. Spotify matches are cached in the `spotify_matches` table, so each track is only searched once.
