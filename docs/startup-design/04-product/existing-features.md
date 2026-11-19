# Existing Features: Rain in My Head

Created: 2026-11-18
Last updated: 2026-11-18

**Phase:** 6 · **Source:** the current repo (`src/rain_in_my_head/playlist.py`, `spotify.py`, and the dashboards)

Most of the planned product already exists. This page describes each feature that's already built, the product name it should go by, and the work left to reposition it.

## Already built

### Write to Spotify
- **What it does:** matches your tracks on Spotify and creates the playlist (`create_on_spotify()` in `playlist.py`). It already uses the endpoints that still work in Spotify's development mode: `POST /me/playlists` to create and `POST /playlists/{id}/items` to add tracks (`spotify.py`).
- **Name:** Send to Spotify
- **Work left:** none.

### Preview before sending
- **What it does:** the Playlists page shows the track list and its columns (plays, dates) before you create anything.
- **Name:** Preview
- **Work left:** none to small. Check whether you can remove a track before sending.

### Old obsessions (currently "Binges")
- **What it does:** `binges()` finds runs where you played a track at least *N* times within *D* days (default: 8 plays in 7 days), across any year range. These are the songs you were once hooked on.
- **Name:** Old obsessions
- **Work left:** rename only.

### Your [year] finds (currently "Discoveries")
- **What it does:** `discoveries()` lists tracks you first heard in a given year. It ranks them either by "most played that year" (what you were into right after finding it) or "most played ever" (the finds that stuck with you).
- **Name:** Your [year] finds
- **Work left:** rename only.

### Time slots (currently "Slot")
- **What it does:** builds a playlist from the tracks that define a time of the week, such as Fridays 5–7 pm. The **When you listen** heatmap on the Overview opens the matching slot.
- **Name:** Your Friday evenings (named by the slot)
- **Work left:** rename only. This is a bonus feature that wasn't in the brainstorm.

### The time machine (currently the Overview, New Artists, Artist, and When you listen pages)
- **What it does:** clicking a bar in the monthly, weekly, or yearly chart filters the whole Overview to that period. New Artists lists who you first heard in it. The Artist page shows when you found each artist and how much you played them.
- **Name:** Time machine
- **Work left:** rename and link. Add a "Make a playlist from this period" button that opens the generator with those dates filled in.

### Rules (currently the playlist form's fields)
- **What it does:** every playlist type already has adjustable settings: minimum plays, window in days, year range, ranking, and size.
- **Name:** Rules
- **Work left:** rewrite the field labels in plain words, for example "Played at least 8 times in one week."

### SQL playlist (power users)
- **What it does:** builds a playlist from any read-only query that returns `artist` and `track` columns (up to 100 tracks). The Analyst page has SQL and the schema map.
- **Name:** Dig deeper
- **Work left:** rename the section only.

### Playlist descriptions
- **What it does:** each playlist gets an auto-written Spotify description (`discoveries_description()`, `binges_description()`).
- **Name:** part of "Why this song"
- **Work left:** see "New work" below.

## New work (small)
1. **Forgotten favorites:** add a "not played in the last *N* months" rule to Old obsessions and Your [year] finds. This is about one query.
2. **"Why this song" sentence per track:** turn the preview's existing columns into one sentence, such as "8 plays in one week, March 2016 · not played since 2019." The data already exists; only the wording is new.
3. **"Make a playlist from this period"** button on the time machine.
