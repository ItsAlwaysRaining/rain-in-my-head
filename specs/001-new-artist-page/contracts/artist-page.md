# Contract: Artist page

## Address (both dashboards)

`/artist?artist=<artist_key>&start=<YYYY-MM-DD>&end=<YYYY-MM-DD>`

| Parameter | Required | Meaning |
|---|---|---|
| `artist` | yes | normalized artist key (lowercased, as stored in `scrobbles.artist_key`) |
| `start`, `end` | no | inclusive local-date period; if either is missing, all time |

Not listed in the page menu. Opened from the Overview's "New artists" table. Streamlit serves it at
`:8501/artist`, the TypeScript app at `:8000/artist` (and `:5173/artist` in dev).

## What it shows

1. A link "Overview" back to the Overview.
2. Header: large cover (period's most common art, else all-time, else placeholder), the artist's
   name, and "N plays in {period} · M all time", with `{period}` from `period_label`. With no
   period: "M plays · all time".
3. Songs table: art (or placeholder), song, album, plays in the period; sorted by plays, highest
   first.

## Errors

- `artist` missing, or no plays for it at all: an info message and the "Overview" link; no table.
- Plays exist but none in the period: the header (with "0 plays in …") and a note instead of the
  table.

## API (TypeScript app)

### `GET /api/overview` (existing) gains `new_artist_list`

Present when the response isn't empty:

```json
"new_artist_list": {
  "label": "Oct 2026", "start": "2026-10-01", "end": "2026-10-18",
  "artists": [{"artist_key": "…", "name": "…", "thumb": "https://…/64s/…" , "plays": 12}]
}
```

`thumb` is null when the artist has no art.

### `GET /api/artist?artist&start&end` (new)

- No `artist`, or no plays for it: `200 {"found": false}`.
- Otherwise:

```json
{
  "found": true, "artist_key": "…", "name": "…", "cover": "https://…/300x300/…" ,
  "period": {"start": "2026-03-01", "end": "2026-03-31", "label": "Mar 2026"},
  "period_plays": 37, "all_time_plays": 52,
  "songs": [{"track_key": "…", "name": "…", "album": "…", "thumb": "…", "plays": 9}]
}
```

`period` is null when `start` or `end` is missing (all time). `cover` and `thumb` are null when
there's no art.
