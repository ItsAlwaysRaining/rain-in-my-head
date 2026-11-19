# Business Model: Rain in My Head

Created: 2026-11-18
Last updated: 2026-11-18

**Phase:** 4 · **Model:** Free, open source, self-hosted (portfolio project)

## How value flows
- **The founder gets** a portfolio case study that shows research, UX strategy, and shipped code.
- **Users get** the app for free. They run it **locally** on their own machine with their own Spotify app and Last.fm key, and Claude helps them set it up. The local version is where the real value is.
- **The hosted web app** exists only as a portfolio deliverable, to show how a hard setup can be designed.
- **Nobody pays anyone.** There's no hosting, no accounts, and no data held by the founder.

## Dependencies
| Dependency | Risk | Mitigation |
|---|---|---|
| Spotify Web API (playlist writes) | Further restrictions | Also export M3U files and ListenBrainz JSPF playlists |
| Last.fm API | Policy change | Raw history is already in git; also accept Spotify GDPR export files |
| User's Spotify Premium | Required for dev mode | State it up front in the setup flow |

## Scalability
It scales by forks, not servers. Each install serves one household (up to 5 Spotify users).

## Why this isn't a business (replaces Phase 7)
Spotify allows only 5 users per development-mode app, and extended access needs a business with 250K+ monthly active users. A hosted version therefore can't legally serve the public without becoming a funded company. Self-hosting is the only workable model, and it suits a portfolio piece.
