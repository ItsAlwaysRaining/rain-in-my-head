# Rain in My Head

Personal listening history from Last.fm (scrobbled from Spotify), stored in SQLite and explored in two dashboards. Formerly `spotify-music-analysis`. See [Renamed from spotify-music-analysis](#renamed-from-spotify-music-analysis).

- `data/raw/lastfm/YYYY-MM.jsonl` holds every scrobble. It's the source of truth, committed to git and appended to by GitHub Actions every 6 hours.
- `data/cache/tracks.jsonl` and `artists.jsonl` hold every Last.fm lookup (durations, listener counts, genre tags). They're committed and append-only too: a redone lookup is a new line, and the last line for a key wins.
- `data/listening.db` is a SQLite database rebuilt from the raw files plus the cache. It's gitignored.

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
uv run rain-in-my-head build      # load raw JSONL and the lookup cache into SQLite (safe to rerun)
uv run rain-in-my-head enrich     # Last.fm durations, listener counts and genre tags; resumable, --limit N
uv run rain-in-my-head stats      # counts, enrichment coverage, suspicious scrobble bursts
uv run streamlit run dashboard/app.py
```

On a fresh clone, `build` restores all enrichment from `data/cache/` without calling Last.fm, so `enrich` only has new items to look up. A plain `enrich` updates your local database only. The scheduled sync runs `enrich --write-cache`, which also appends each lookup to `data/cache/`. It's the only routine writer, so `git pull` never conflicts with local runs.

Without a cache, `enrich` makes about one call per unique track and two per unique artist, at roughly 2 per second. For 76k tracks and 24k artists that's around 15 hours. It's safe to Ctrl-C and rerun. `uv run rain-in-my-head export-cache` seeded `data/cache/` from a fully enriched database. It's a one-time command and refuses to run again unless given `--append`.

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

[docs/streamlit-vs-typescript.md](docs/streamlit-vs-typescript.md) explains why the TypeScript app exists (design control over layout, style and interaction) and logs how building each page went in each app.

The TypeScript app follows the Figma prototype (`specs/005-prototype-redesign`), so its addresses differ from Streamlit's: `/dashboards`, `/dashboards/new-artists`, `/dashboards/genre`, `/dashboards/artist`, `/playlists` and `/analyst`. The old `/genre`, `/artist`, `/sql` and `/schema` addresses redirect. The home page (`/`) is the prototype's landing page: the Rain Girl artwork with flickering rain, where clicking the lightning bolt opens **Storm** (`/storm`): full-window rain, with a Thunder switch that turns on rain and thunder sounds (made in the browser, no audio files) and lightning. Storm always opens silent. **About** (`/about`) has a photo beside About Me and About This App. The photo is `web/public/about/photo.jpg`, and until it's added the page shows an empty frame. **Contact Me** (`/contact`) lists Email, LinkedIn, GitHub and Last.fm, with Send email and Download CV. The CV is `web/public/contact/cv.pdf`; replace that file to update it. Pages from the prototype that aren't built yet show a **Coming soon** card that links to their GitHub issue: the listening-slot drill-down (#30), mainstream vs. niche artists (#12), the AI (#32) and SQL (#31) playlist types. The AI playlist (#32) is in the top menu (**AI**, `/ai`) as well as the Playlist Generator's AI tab.

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
3. Run the "Sync scrobbles" workflow once by hand from the Actions tab. After that it runs every 6 hours: it fetches new scrobbles, looks up up to 100 new tracks and 100 new artists, and commits both to `data/`.
4. Locally: `git pull && uv run rain-in-my-head build` to refresh the database, including the sync's lookups.

## Two-year copy for the hosted site

```sh
uv run rain-in-my-head publish      # data/public.db: the last 730 days of plays, minus the newest 7
LISTENING_HOSTED=1 LISTENING_DB=data/public.db uv run rain-in-my-head serve   # preview the hosted site
```

- **What `publish` keeps:** only the plays in the window, plus the tracks, artists and tags they use. Spotify matches are dropped. It only reads `data/listening.db`, and `public.db` is gitignored. `--window-days` and `--lag-days` change the window.
- **What `LISTENING_HOSTED=1` does:**
  - opens the database immutable, so nothing is written, locked or journaled
  - hides the API docs
  - turns visitors away with **"This DJ doesn't take requests."** That covers typed SQL, creating playlists, saving the schema layout, AI, and any other request that isn't a read. The playlist form and its track preview are reads, so they work.
- **The Analyst page on the hosted site** offers only the pre-defined queries: pick one, read its SQL, run it.
- **Locally**, without the setting, everything works as before, including free-form SQL.
- **Only the TypeScript dashboard is hosted.** Streamlit stays local.

## Hosting infrastructure (OpenTofu)

Everything hosted is declared in `infra/`:
- **Vercel:** the site, with previews that need a Vercel login.
- **Neon:** visitor data, with `prod` and `dev` branches.
- **GitHub:** the Actions values the workflows read.

Change hosting only here, through a pull request, never in the dashboards. The state file `infra/terraform.tfstate` is committed, but it's encrypted with your passphrase.

**First apply** (once, from your Mac): follow `specs/010-infrastructure/quickstart.md`. It reads each token with `read -s`, so nothing is echoed or saved to your shell history.

**Making a change:**
1. Open a PR that touches `infra/`. The **Infrastructure** workflow checks it and posts the plan as a comment.
2. Nothing is applied on merge. To apply, go to **Actions → Infrastructure → Run workflow** and pick the PR's branch. It applies, then commits the updated encrypted state to that branch. (GitHub only shows **Run workflow** once `infra.yml` is on `main`, so the very first CI apply happens after the infrastructure PR is merged, from a throwaway branch such as `chore/first-ci-apply`. It refuses `main`.)
3. Merge the PR.

Every Monday, a drift check opens an issue called "Infrastructure drift" if a dashboard setting no longer matches the code.

**Custom domain.** The site's address is `rain.storyandstructure.studio` (the `site_domain` variable in `infra/variables.tf`). OpenTofu attaches it to the Vercel project. The name is registered and renewed each year at Spaceship (auto-renew is on), but its nameservers point at Cloudflare, so the DNS lives at Cloudflare. You add one record by hand there after the apply:
1. In Vercel, open the project's **Settings → Domains** and read the value it shows for the domain. Use that value, not one from an old guide.
2. At Cloudflare, open the domain's **DNS → Records**. Delete any record for the `rain` host (such as a parking page), and leave records you didn't make, especially email ones (MX, TXT). Add a **CNAME** with name `rain` (just the word) and the value from step 1. Set **Proxy status** to **DNS only** (grey cloud) and TTL to Auto. Vercel has to see the record itself to issue the https certificate, so don't turn the orange proxy on.
3. Check it has spread (a few minutes, sometimes an hour). It should print a Vercel name and IP addresses: `dig +short rain.storyandstructure.studio`

If the nameservers ever go back to Spaceship's, add the record there instead. In Spaceship, the domain's **Nameservers & DNS** page shows where they point.

Once the site is deployed (see "Production" below), the address serves it over https. The `.vercel.app` address keeps working as a backup, and the bare `storyandstructure.studio` is not attached.

**Renewing tokens.** The Vercel, Neon and GitHub tokens last 90 days. When one expires, plans fail and the drift check fails. Create a new token with the same name, then update the matching secret with `gh secret set VERCEL_API_TOKEN` (or `NEON_API_KEY`, or `GH_INFRA_TOKEN`).

**Lost passphrase.** The state can't be decrypted. Choose a new passphrase, delete `infra/terraform.tfstate`, then `tofu import` each resource by its ID: the Vercel project, then the Neon project, branch, endpoint, role and database. The IDs are in each dashboard. Passwords made by `random_password` will be regenerated, so the next apply rotates them.

**Neon's sign-up project.** If Neon made you create a project when you signed up (for example `scratch`), delete it by hand once. It isn't managed here.

**Database roles.** OpenTofu makes the owner roles. The website's app role (`rain_app`) is created by `viewer init` (below), because roles made through Neon's API are superusers.

## Previews and CI checks

Every pull request from this repository gets its own copy of the hosted site on Vercel, built by `.github/workflows/deploy.yml`. A preview uses the Neon `dev` branch, never `prod`. Deploying to the live address is in "Production" below.

**Opening a preview**
1. Open the pull request. The `github-actions` bot posts one comment headed "Preview" with a `*.vercel.app` address and the commit it was built from. Later pushes edit that comment, so there is only ever one.
2. Open the address while you're logged in to your Vercel team. Anyone else is sent to Vercel's sign-in page, because preview protection is switched on in `infra/`.
3. The site then asks for an invite code, as on the live site.

**Making a test code** (run on your Mac; `dev` is the default branch):

```sh
uv run rain-in-my-head viewer add Sam      # prints the code once; add --tier trusted to open Analyst and Storm
uv run rain-in-my-head viewer revoke Sam   # when you're done
```

Logging in on the preview records your session in the `dev` database, so it shows on the **Visitors** page (choose `dev`) and in `uv run rain-in-my-head viewer usage`.

**What the preview deploy checks, in order.** It builds the full database, then the two-year copy, and stops if the oldest play is more than 738 days old (the 730-day window plus the 7-day lag is 737, plus a day of margin so rounding never fails a run). It builds `web/`, then lists the files in the function bundle and stops before deploying if `data/raw`, `data/cache`, `infra`, `.claude`, `.specify`, `.env` or any `data/listening.db` file is in it. Pull requests from forks and from Dependabot get no preview. The first request after a quiet spell can be slower while Vercel starts the function.

**CI checks.** `.github/workflows/ci.yml` runs four separate checks on every pull request, none using a repository secret, so one red result never hides another:
- **Hosted smoke test**: `tests/test_hosted_smoke.py` loads `api/index.py` (the file Vercel runs) in hosted mode on the two-year copy, with the login lookup replaced. It checks health, a locked route, a forged cookie, typed SQL refused, creating a playlist refused (the form data and preview answer), and a guest's access. Run it yourself after `build` and `publish`: `uv run --no-default-groups --group web --with pytest --with httpx pytest tests`
- **Frontend build**: `npm ci && npm run build` in `web/`.
- **Secret scan**: gitleaks, with `.gitleaks.toml`. Every rule stays on, and each allowed false alarm says why. Run it yourself with `gitleaks git .`
- **Security lint**: Ruff's security rules only (`[tool.ruff.lint]` in `pyproject.toml`). Run it with `uvx ruff@0.17.3 check src api tests`. Where the rule is a false alarm, the line carries a `# noqa` with its reason.

## Production

The same workflow, `.github/workflows/deploy.yml`, deploys the live site at `https://rain.storyandstructure.studio`, on the Neon `prod` branch. Three things start it, all on `main`:
- a pull request is merged,
- 03:00 UTC every night (the nightly sync's pushes don't start workflows, so this run is what puts new plays on the site),
- you start it by hand: `gh workflow run deploy.yml --ref main`. Runs started on another branch are skipped.

**What it does, in order.** The same build and bundle checks as a preview. Then it **stages** the build (`vercel deploy --prod --skip-domain`): it exists, but visitors still get the old version. Then it checks the staged build: `/api/health` must answer `{"ok":true}`, and a locked route (`/api/genre`) asked with no login must answer 403 `login_required`. Only if both pass does `vercel promote` make it the live site. Previews run the same check on their own address. The log shows status codes only.

**A red run** means the check failed or a step before it did. Visitors never saw that build: the live address still serves the last good one. Open the run and read the "Check the deployment answers" step. Fix the cause and push, or run it again by hand.

**Promote an older deployment by hand** (for example to go back after a bad change that passed the check): `npx vercel@64.7.0 promote <deployment-url>` from the repository root, with `VERCEL_TOKEN` set. Deployment addresses are listed in the Vercel project under **Deployments**.

Production runs one at a time and never cut each other off. Two merges in a row deploy the newer one.

## Visitors and invite codes

The hosted site has no public pages except the landing page and the login page. Each person gets their own invite code, and you manage them from your Mac. On your Mac the dashboard needs no login, and nothing here applies.

**One-time setup, per Neon branch** (`dev` first):
1. Put these in `.env` (names are in `.env.example`; never paste the values anywhere else): `VIEWERS_OWNER_URL_DEV` and `VIEWERS_APP_URL_DEV`, from `tofu output -raw dev_owner_url` and `dev_app_url` in `infra/`. Add `VIEWERS_OWNER_URL_PROD` and `VIEWERS_APP_URL_PROD` the same way when you're ready for prod.
2. `uv run rain-in-my-head viewer init` makes the tables and the site's database role. It's safe to run again. Add `--env prod` for production.

**Commands** (all take `--env dev|prod`, default `dev`, and print `[dev]` or `[prod]` first):

| Command | What it does |
|---|---|
| `viewer add NAME [--tier guest\|trusted]` | Invites someone and prints their code **once**. Send it to them yourself. |
| `viewer list` | Shows everyone: tier, extra pages, status, created and last login. |
| `viewer revoke NAME` | Ends their code and logs them out on every device, within seconds. |
| `viewer grant NAME [--page KEY] [--remove-page KEY] [--tier guest\|trusted]` | Gives or takes back a page, or changes the tier. Applies on their next click. |

**What each tier opens.** A guest opens the six dashboard pages (Overview, New artists, Genre, Artist, When you listen, Mainstream vs. niche), Playlist Generator, AI, About and Contact Me. Every section shows in the top bar for everyone; the ones a person can't open are marked with a padlock. The AI page is only a Coming soon card, so no AI runs on the hosted site. A trusted visitor also opens Analyst (pre-defined queries and the schema map, never free-form SQL) and Storm. Page keys for `grant`: `overview`, `new-artists`, `genre`, `artist`, `slot`, `mainstream`, `playlists`, `analyst`, `ai`, `storm`, `about`, `contact`. On the hosted site the Playlist Generator shows the form and the track preview, but Create on Spotify answers "This DJ doesn't take requests." for everyone.

**What is stored.** A person's name, the hash of their code (never the code), and when they last logged in. A guessing limit uses a daily-changing scrambled form of the visitor's address, never the address. If a code is lost, revoke it and add the person again.

**Trying the hosted site on your Mac** (against the dev branch): `uv run rain-in-my-head publish`, then set `LISTENING_HOSTED=1`, `LISTENING_DB=data/public.db`, `DATABASE_URL` (the `VIEWERS_APP_URL_DEV` value) and `SESSION_SECRET` (any random string) and run `uv run rain-in-my-head serve`. The full checklist is `specs/011-viewer-access/quickstart.md`.

## Usage and limits

The hosted site records what each invited person does, so you can see how it's used and spot trouble before the free plans run out. On your Mac nothing is recorded and nothing is limited.

**What is recorded** (in the visitor database, with each person's name): the pages they open, the features they use (a pre-defined query by name, a genre's song list), and about how long they stay on each page. Never what they type into a filter or search, and never an IP address or a code. The login page says all of this in plain words. Records older than 12 months are deleted every night.

**The limit.** A person can ask for 30 heavy requests a minute and 1,000 a day (a pre-defined query or a genre's song list). Past that they see "You're going a bit fast. Try again in N seconds." (or that today's limit is reached), and nobody else is affected. The numbers are `HEAVY_PER_MINUTE` and `HEAVY_PER_DAY` at the top of `src/rain_in_my_head/usage.py`. The browser's own page-view reports are capped separately at 120 a minute, quietly.

**Seeing it** (on your Mac only, never on the hosted site):
- The **Visitors** page in the top bar (choose the live site or dev, and a range). Click a person to see their latest records.
- `uv run rain-in-my-head viewer usage [--range 7d|30d|12m] [--person NAME] [--env dev|prod]` shows the same numbers. The bottom section shows this month's recorded requests and the visitor database's size against the free limits. Vercel's processing time appears only on Vercel's own dashboard.
- Time on a page is an estimate sent by the visitor's browser. Days and months are UTC.

**The nightly copy.** `.github/workflows/analytics.yml` runs every night at 02:43 UTC. It deletes records older than 12 months (`viewer prune`), writes `usage_events.csv` and `viewers.csv` (`viewer export DIR`, no codes or hashes), and replaces the private `analytics` branch with **one** commit holding them, only if they changed. Older copies leave the branch, so the 12-month promise holds there too. `main` is never touched. Run it by hand from Actions → Analytics export; choosing `dev` writes the branch `analytics-dev` instead. GitHub can keep an unreferenced commit fetchable by its hash for a while after the branch moves on; the repository is private.

**After pulling this change**, run `uv run rain-in-my-head viewer init` once for each database (`--env prod` for production). It adds the `usage_events` table and is safe to run again. Until it has run, recording is quietly dropped and heavy requests are refused with "try again in a minute".

The full checklist is `specs/012-usage-tracking/quickstart.md`.

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
