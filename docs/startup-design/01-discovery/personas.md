# User Personas: Rain in My Head

Created: 2026-11-18
Last updated: 2026-11-18

**Phase:** 3 · **Type:** Proto-personas (built from secondary research in [target-audience.md](target-audience.md) and [raw/wave3-4-customers-distribution.md](raw/wave3-4-customers-distribution.md); not yet checked in interviews) · **Confidence:** Medium

## At a glance
| # | Persona | Technical? | Main job | Role in design |
|---|---|---|---|---|
| 1 | Maya, the Long-Time Listener | No | Rediscover music I already loved | **Primary for UX** |
| 2 | Dev, the Self-Hoster | Yes | Own and query my listening data | **Primary for adoption** |
| 3 | Rosa, the Era Chaser | No | Take me back to a time in my life | Secondary |
| 4 | Sam, the Trust-Broken Skeptic | Somewhat | Tell me why a song is here | Secondary |
| 5 | Theo, the Last.fm Lifer | Somewhat | Do something with 15 years of scrobbles | Secondary |

---

## 1. Maya, the Long-Time Listener (primary for UX)
**34 · marketing manager · Spotify Premium since 2013**

> "Spotify seems to think I only want to listen to maybe 20 songs."

- **Context:** Listens 3+ hours a day at work and on walks. Has never opened a terminal.
- **Goals:** Playlists that feel like *her*. Hear the songs she loved five years ago.
- **Frustrations:** Stuck in a loop on DJ and Daily Mix. Discover Weekly brings back songs she skipped.
- **Behaviors:** Saves songs but rarely builds playlists. Shares Wrapped every December.
- **What she needs from us:** A setup she can finish without help. Playlists with a plain-language reason on each track.
- **Design implication:** The default UI is built for Maya. Power features stay behind it.

## 2. Dev, the Self-Hoster (primary for adoption)
**29 · backend developer · runs a home server**

> "If it's my data, I want it in a database I can query."

- **Context:** Active in r/selfhosted and r/lastfm. Already runs Maloja or Koito in Docker.
- **Goals:** Plays stored in SQLite, SQL access, and playlist rules he can edit.
- **Frustrations:** Spotify API limits broke YourSpotify. Most tools are charts only, with no playlists.
- **Behaviors:** Reads the schema before the README. Sets things up for his partner (often a Maya).
- **What he needs from us:** Clear schema docs, a CLI, and a way to run it locally with no cloud.
- **Design implication:** Dev brings the product to Maya. The docs and schema pages are his front door.

## 3. Rosa, the Era Chaser (secondary)
**41 · teacher · parent of two**

> "I want the music from the summer I moved to Lisbon."

- **Context:** Listening dropped off after having kids. Has Last.fm history from her 20s.
- **Goals:** Relive a specific year, trip, or relationship through its music.
- **Frustrations:** Streaming apps only know who she is *now*. Old favorites are buried.
- **Behaviors:** Searches "songs from 2009" on YouTube. Loves Wrapped but wishes she could look back further.
- **What she needs from us:** A "time machine": pick a date range and get its playlist.
- **Design implication:** Time-based browsing and era playlists should be one tap from the home screen.

## 4. Sam, the Trust-Broken Skeptic (secondary)
**37 · freelance designer · independent music fan**

> "This has completely broken my trust. I used to feel like recommendations were made for me."

- **Context:** Followed the AI-generated song threads and the Discovery Mode payola debate.
- **Goals:** Recommendations he can trust are not paid placement or AI slop.
- **Frustrations:** No explanation for why a song appears. Suspects labels pay for reach.
- **Behaviors:** Reads Rate Your Music and music blogs. Has thought about leaving Spotify.
- **What he needs from us:** A visible "why this track" on every pick, with the data behind it.
- **Design implication:** The explanation is a core feature, not a tooltip. It is the main reason Sam switches.

## 5. Theo, the Last.fm Lifer (secondary)
**45 · IT support · scrobbling since 2007**

> "I've got 200,000 scrobbles and nothing useful to do with them."

- **Context:** Uses Last.fm daily. Can follow setup steps but doesn't write code.
- **Goals:** Deep stats, forgotten favorites, and playlists from his whole history.
- **Frustrations:** Last.fm's interface feels dated and its recommendations are weak.
- **Behaviors:** Checks weekly charts. Has tried stats.fm, Calliope, or Nostalgeist.
- **What he needs from us:** A one-click Last.fm import and dashboards that go further than Last.fm's own.
- **Design implication:** Theo is the easiest first user. The Last.fm import must be painless and fast.

---

## How the personas connect
- **Maya** and **Rosa** set the bar for simplicity.
- **Sam** sets the bar for transparency.
- **Dev** and **Theo** set the bar for data depth, and they bring the product to the others.

## Red flags / yellow flags
- 🟡 All five are proto-personas from secondary research. Validate them in interviews (validation experiment #1).
- 🟡 Names, ages, and jobs are illustrative, not data. Quotes for Maya and Sam come from the research; check each at its link before using it in the case study. The other quotes are written to fit the persona.
