# Intake Brief: Rain in My Head

Created: 2026-11-18
Last updated: 2026-11-18

**Phase:** 1 (Intake) · **Mode:** Full (adapted for a portfolio project) · **Confidence:** High (founder-stated)

## The idea
Rain in My Head is an open-source app for exploring your personal listening history. It's built on Last.fm scrobbles stored in SQLite and has two dashboards. The design goal is to make playlists that come from your whole listening history, show why each track was chosen, and keep your data under your control. This would replace opaque algorithmic and AI playlists.

## Purpose
- A UX portfolio piece. It runs the full research and design process as if the product were for everyone.
- It won't be hosted for other people. The repo is public on GitHub, so anyone can fork it and host it themselves.
- There's no revenue goal and no hosting spend. A few real users would be a bonus.
- **Local first (added 2026-11-18):** the real product runs locally, and Claude helps with setup. The hosted web app and its harder setup exist only for the portfolio.
- **Future:** import from other listening apps that have free developer APIs. Each source would have docs for running the import locally with Claude.

## Users
- **Primary problem:** people who are tired of AI and algorithmic playlists that don't reflect their long-term taste.
- **Mixed audience:** some features are for technical users (self-hosting, SQL and schema pages, CLI) and some are for non-technical listeners (dashboards and playlists).

## Problem framing (after fact-check)
- [Data] Spotify's Prompted Playlist (beta, Premium, only in some countries) *does* use your full history. Saying "Spotify only uses recent months" is out of date.
- [Data] Discovery Mode lets labels pay for algorithmic reach, and critics call it payola.
- **Defensible framing:** "I can't see or control why I get these songs, and my listening data isn't mine."

## Competitors (first pass, grouped by the job they do)
Items marked † come from Claude's own knowledge, not live search. They get verified in Phase 3.

### 1. Listening stats apps (show what you played)
| Name | What it is | Gap vs. Rain in My Head |
|---|---|---|
| [stats.fm](https://apps.apple.com/app/1526912392) | Spotify and Apple Music stats app, freemium | Shows numbers but no explanation of why, and your data sits on their servers |
| [Last.fm](https://www.last.fm) | Scrobbler for any service since 2002, freemium | Dated interface and weak recommendations |
| [Raygum](https://raygum.com/last-fm-alternative) | Diary-style "why I listened" log | Spotify-only and opt-in |
| [Free Your Music Stats](https://freeyourmusic.com/blog/spotify-stats-apps) | Stats across 9 services | Focused on transferring playlists between services |
| Receiptify †, Obscurify †, Volt.fm † | Free web toys that turn your stats into a shareable image | Novelty only; limited to Spotify's short time windows |

### 2. Spotify's built-in features (the default to compete with)
| Name | What it is | Gap vs. Rain in My Head |
|---|---|---|
| [Prompted Playlist](https://newsroom.spotify.com/2026-01-22/prompted-playlists-expansion/) | Makes a playlist from a text prompt, using your full history | Premium-only, only in some countries, and a black box |
| [Taste Profile](https://www.musicbusinessworldwide.com/spotify-to-let-users-edit-the-algorithm-behind-their-personalized-recommendations-with-taste-profile) | Lets you see and edit what the algorithm thinks you like | You can exclude tracks but can't see why something was picked |
| Discover Weekly / Daylist / DJ † | Algorithmic playlists | [Discovery Mode criticism](https://www.digitalmusicnews.com/2023/03/13/discovery-mode-spotify-pushback/) undermines trust |
| Wrapped † | Yearly recap | Once a year, and you can't explore it |
| Apple Music Replay †, YouTube Music Recap † | The same idea on other platforms | Tied to one service |

### 3. Open playlist engines built on listening history (closest match)
| Name | What it is | Gap vs. Rain in My Head |
|---|---|---|
| [ListenBrainz + Troi](https://troi.readthedocs.io/) | Open, nonprofit; Weekly Jams and Weekly Exploration playlists | Needs MusicBrainz tagging; interface aimed at technical users |
| [Calliope](https://discourse.beets.io/t/calliope-antisocial-music-recommendations/1532) | Command-line tool: "forgotten songs" and "new discoveries" from Last.fm | Command line only |
| [Nostalgeist](https://github.com/tchandler/Nostalgeist) | Builds a playlist from a random past week of your Last.fm history | Does one thing only |
| [Lastgen](https://github.com/felipefrr/Lastgen) | Turns your Last.fm profile into a Spotify playlist | Hobby project |
| [MusicBee playlist plugin](https://getmusicbee.com/addons/plugins/22/playlist-generator) | Last.fm-based smart playlists | Windows and local files only |

### 4. Self-hosted stats dashboards (closest technical match)
| Name | What it is | Gap vs. Rain in My Head |
|---|---|---|
| [Maloja](https://selfhostyourself.com/services/maloja) | Self-hosted database of your plays with charts | No playlists; needs a server |
| [Koito](https://selfhostyourself.com/services/koito) | Newer ListenBrainz-compatible scrobbler with a better interface | New and small |
| [YourSpotify](https://selfhostyourself.com/alternative-to/stats-for-spotify) | Self-hosted Spotify dashboard | Hit by [Spotify API limits](https://developer.spotify.com/blog/2025-04-15-updating-the-criteria-for-web-api-extended-access) |
| [multi-scrobbler](https://foxxmd.github.io/multi-scrobbler/docs/installation) | Collects plays from many services and forwards them | Plumbing only, no interface |

### 5. Other ways people solve this (indirect alternatives)
- Hand-curated playlists, which take a lot of time
- Friends and Blend playlists †
- Music blogs, Album of the Year, and Rate Your Music †
- Radio, or [Every Noise at Once](https://techcrunch.com/2024/02/12/every-noise-shut-down-spotify-layoffs), the genre map that was shut down in Spotify's 2024 layoffs

### What the list shows
- Groups 3 and 4 already do the core idea for technical users. The case-study angle is **UX**: making transparent, history-based playlists usable by someone who isn't technical.
- No one combines "explain why each track was chosen" with "you own the data." [Assumption] Treat this as a hypothesis for now, not a confirmed gap.

## Constraints and decisions
- Customer interviews: **deferred** (they become validation experiment #1).
- Financial projections: **skipped**. A short "why this isn't a business" note replaces Phase 7.
- Spotify API platform risk: avoid it by using Last.fm and user-uploaded Spotify exports.

## Red flags / yellow flags
- 🟡 Strong incumbents (stats.fm, Last.fm, ListenBrainz) and open tools (Troi, Maloja, Koito) already cover parts of this.
- 🟡 A mixed technical and non-technical audience risks a split UX. The case study should say clearly who each surface is for.

**Next:** Phase 2 brainstorm.
