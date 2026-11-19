# Brainstorm: Rain in My Head

Created: 2026-11-18
Last updated: 2026-11-18

**Phase:** 2 · **Confidence:** Medium (direction chosen by the founder; not yet researched)

## Correction from the founder
Rain in My Head doesn't play music. It **builds playlists and writes them to Spotify**. People listen in Spotify as usual.

## Variations considered
| # | Variation | Exciting | Risk | Chosen |
|---|---|---|---|---|
| 1 | "Why this song" playlists: each track shows why it was picked | Answers the black-box complaint; hard for Spotify to copy | Explanations must be short enough to scan | ✅ |
| 2 | Rediscovery: forgotten favorites, past eras | Small scope; the existing data supports it | Overlaps with Calliope and Nostalgeist | ✅ |
| 3 | Taste time-machine: see taste change over the years, then turn any era into a playlist | Very visual for the portfolio | Could drift into stats.fm territory | ✅ |
| 4 | You set the rules: playlist recipes with visible dials | Ties to the "control" pain | Complicated for non-technical users | ✅ |
| 5 | Two doors: a listener mode and a power-user mode | Fits the mixed audience | Doubles the design work | ❌ (not chosen, but the mixed audience from intake still applies) |

## Refined idea
**Explore your whole listening history, find an era or pattern, set the rules, and send an explained playlist to Spotify.**
- Time-machine (3) is where you **discover**.
- Rediscovery (2) gives you **ready-made starting points**.
- Rules (4) give you **control**.
- "Why this song" (1) gives you **trust**, and it travels with the playlist (for example, in the playlist description).

## Red flags / yellow flags
- 🔴 **Writing to Spotify needs the Spotify Web API.** Development mode allows only a few users per app. The [February 2026 changes](https://techcrunch.com/2026/02/06/spotify-changes-developer-mode-api-to-require-premium-accounts-limits-test-users/) reportedly require the developer to have Premium. [Data, medium confidence: from community sources]
  - **Works for the self-host model:** each person who forks the repo registers their own Spotify developer app, and they're its only user. This adds a setup step that non-technical users will struggle with. It's a real UX problem to design around, and good material for the case study.
- 🟡 Four chosen variations is a lot of scope. Phase 6 needs to rank them, and the time-machine is the one most likely to be cut or simplified.
- 🟡 Spotify playlist descriptions are short (about 300 characters †). Per-track "why" text needs another home, such as the app itself or a shareable link.

**Next:** Phase 2.5, research depth.
