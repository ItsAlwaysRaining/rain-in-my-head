# MVP Definition: Rain in My Head

Created: 2026-11-18
Last updated: 2026-11-18

**Phase:** 6 · Built on [../01-discovery/target-audience.md](../01-discovery/target-audience.md), [../01-discovery/competitor-landscape.md](../01-discovery/competitor-landscape.md), and [existing-features.md](existing-features.md)

## Core hypothesis
If a long-time listener gets a Spotify playlist of forgotten favorites with a specific reason for each track, they'll find it more "theirs" than Spotify's algorithmic playlists, and they'll make another one within a week.

## Key finding (updated 2026-11-18)
**Most of the MVP is already built.** The repo already previews playlists and writes them to Spotify with the working endpoints. It also has the Old obsessions, Your [year] finds, and Time slot playlist types, adjustable rules, a SQL playlist, and the time-machine dashboards. The MVP is mostly **renaming** plus **three small additions**. See [existing-features.md](existing-features.md).

## Must-have
| Feature | Status |
|---|---|
| Send to Spotify | ✅ Built |
| Preview before sending | ✅ Built (check that you can remove a track) |
| Old obsessions (rename "Binges") | ✅ Built: rename |
| Your [year] finds (rename "Discoveries") | ✅ Built: rename |
| Rules in plain words | ✅ Built: rewrite labels |
| **Forgotten favorites** ("not played in the last *N* months") | 🆕 Small: about one query |
| **"Why this song" sentence per track** | 🆕 Small: wording over existing data |
| Local, Claude-assisted setup | ✅ Runs locally today; setup docs to come. The hosted web app's guided setup is a portfolio deliverable only. |

## Nice to have
- Time machine: ✅ built; add a "Make a playlist from this period" button.
- Time slots (Your Friday evenings): ✅ built; rename.
- Dig deeper (SQL playlist and Analyst): ✅ built; rename.
- A shareable "why" page per playlist.
- Export as M3U or ListenBrainz JSPF.
- **Future:** import history from other listening apps with a free developer API. Each source comes with a doc for Claude to follow, so the import runs locally. See [feature-prioritization.md](feature-prioritization.md).

## Out of scope (MVP)
- Hosting for other people or user accounts (the hosted site is an invite-only portfolio demo).
- Discovering new music the user has never played.
- Mood or energy rules (Spotify no longer gives apps audio features).
- A mobile app.

## Success criteria
- Setup: 1 non-technical friend finishes local setup with Claude's help in under 20 minutes.
- Trust: at least 4 of 5 testers say the reasons are accurate and interesting.
- Repeat use: at least 3 of 5 make a second playlist within 7 days.
