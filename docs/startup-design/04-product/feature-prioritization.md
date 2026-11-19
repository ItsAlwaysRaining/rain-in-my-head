# Feature Prioritization: Rain in My Head

Created: 2026-11-18
Last updated: 2026-11-18

**Phase:** 6 · **Method:** RICE (Reach out of 10 users, Impact 0.25 to 3, Confidence %, Effort in person-weeks)

Rescored 2026-11-18 after finding that most features already exist (see [existing-features.md](existing-features.md)). Effort now counts only the work left.

| Feature | Status | Reach | Impact | Confidence | Effort | RICE | MoSCoW | Size |
|---|---|---|---|---|---|---|---|---|
| Rename playlist types and rules (Old obsessions, Your [year] finds, Time slots, Rules, Dig deeper) | ✅ Built | 10 | 2 | 90% | 0.25 | 72 | Must | XS |
| Forgotten favorites ("not played in *N* months") | 🆕 | 10 | 3 | 80% | 0.25 | 96 | Must | S |
| "Why this song" sentence per track | 🆕 (data exists) | 10 | 3 | 70% | 0.5 | 42 | Must | S |
| Send to Spotify | ✅ Built | 10 | 3 | 100% | 0 | — | Must | — |
| Preview (check that tracks can be removed) | ✅ Built | 10 | 2 | 80% | 0.1 | 160 | Must | XS |
| Local, Claude-assisted setup docs | Runs locally today | 10 | 3 | 70% | 0.5 | 42 | Must | S |
| Time machine: "Make a playlist from this period" button | ✅ Built: add link | 7 | 2 | 70% | 0.25 | 39 | Should | XS |
| Hosted guided setup flow (portfolio only) | Design only | 3 | 2 | 60% | 2 | 1.8 | Could | L |
| Shareable "why" page | 🆕 | 4 | 1 | 50% | 1 | 2 | Could | M |
| M3U / JSPF export | 🆕 | 3 | 1 | 80% | 0.5 | 4.8 | Could | S |

## Future: more listening sources (added 2026-11-18)
Import history from other listening apps that have a free developer API. Each source gets a doc in the repo that Claude follows to set up the import and run it locally, the same way the core setup works.

| Candidate source | Free API? (Claude's knowledge, unverified) | Notes |
|---|---|---|
| ListenBrainz | Yes, open | Easiest; already compatible with Last.fm data |
| Spotify extended streaming history | Not an API: a GDPR file export | Fills in history from before Last.fm tracking |
| Deezer | Yes | Has a listening-history endpoint |
| Apple Music | No: needs the $99/year developer program | Recently played only, not full history |
| YouTube Music | No official API | Google Takeout export is the fallback |
| Tidal | Developer API, but limited | Check whether history is available |

Priority: **Could**, after the MVP. Many services already reach Last.fm through scrobbling, so check the overlap first.

## Dependencies
The playlist engine, preview, and Spotify write are already in place. Forgotten favorites and "why this song" both plug into the existing preview. The time-machine button only links to the existing generator.

## Build order (updated 2026-11-18)
1. Rename the playlist types and rewrite the rule labels (branding only).
2. Add the forgotten favorites rule.
3. Add the "why this song" sentence to the preview and the Spotify description.
4. Add "Make a playlist from this period" to the time machine.
5. Write the local, Claude-assisted setup docs.
6. Portfolio only: design the hosted guided setup flow.
