# Contract: Artist page

## Address

`/artist?artist=<artist_key>&start=<YYYY-MM-DD>&end=<YYYY-MM-DD>`

| Parameter | Required | Meaning |
|---|---|---|
| `artist` | yes | normalized artist key (lowercased, as stored in `scrobbles.artist_key`) |
| `start`, `end` | no | inclusive local-date period; if either is missing, all time |

Not listed in the page menu. Opened from the Overview's "New artists" table.

## What it shows

1. A link "Overview" back to the Overview.
2. Header: large cover (period's most common art, else all-time, else placeholder), the artist's
   name, and "N plays in {period} · M all time". `{period}` is the month name (e.g. "Mar 2026") when
   start/end span exactly one calendar month, the year when they span one calendar year, otherwise
   "d Mon YYYY – d Mon YYYY"; "all time" when no period is given (then only "M plays").
3. Songs table: art (or placeholder), song, album, plays in the period; sorted by plays, highest
   first.

## Errors

- `artist` missing, or no plays for it at all: an info message and the "Overview" link; no table.
- Plays exist but none in the period: the header (with "0 plays in …") and a note instead of the
  table.
