# Competitor Landscape: Rain in My Head

Created: 2026-11-18
Last updated: 2026-11-18

**Phase:** 3 · **Confidence:** Medium · Full profiles: [raw/wave2-competitors.md](raw/wave2-competitors.md) · First-pass list: [../00-intake/brief.md](../00-intake/brief.md)

## Comparison matrix (closest competitors)
| Name | Product | Pricing | Target | Writes to Spotify | Full history | Explains picks | You own data | Key strength | Key weakness |
|---|---|---|---|---|---|---|---|---|---|
| Spotify Prompted Playlist | AI playlist from a text prompt | Premium (beta) | All Premium users | ✅ native | ✅ Spotify only | ✅ short generic notes | ❌ | Built in, no setup | Black box; Spotify-only history; trust problems |
| ListenBrainz + Troi | Open listening history and playlist engine | Free, nonprofit | Music nerds | ✅ export | ✅ incl. Last.fm import | ❌ (logic is in the code) | ✅ open data | "Top Missed" ≈ forgotten favorites | Interface aimed at technical users; no visible reasoning |
| stats.fm | Stats app | Freemium; Plus for lifetime stats | Mainstream fans | ❌ | ✅ with import | ❌ | ❌ | ~9M installs, polished | Only stats, no playlists |
| Last.fm | Scrobbler and stats | Freemium | Long-time trackers | ❌ | ✅ | ❌ | Partial (API) | Decades of multi-source history | Dated; weak recommendations |
| Nostalgeist / Last-Spot | Scripts that turn Last.fm history into Spotify playlists | Free, open source | Developers | ✅ | ✅ | ❌ | ✅ | Proves the idea works | No interface, no explanations |
| Smarter Playlists | Rule-based playlist builder | Free | Power users | ✅ | ❌ | ❌ | ❌ | Rules | Node editor, no history |
| YourSpotify / Maloja / Koito | Self-hosted stats dashboards | Free, open source | Self-hosters | ❌ | ✅ | ❌ | ✅ | 1K–4.6K GitHub stars | No playlists |
| Wrapped / Replay / Recap | Yearly recap | Free | Everyone | Partial | Annual | ❌ | ❌ | 300M+ reach | Once a year |

Unverified (couldn't be confirmed in searches): Calliope, Lastgen, the MusicBee playlist plugin, and Volt.fm.

## Positioning map
- **X axis:** opaque → transparent (explains picks)
- **Y axis:** platform-owned → user-owned data

Spotify sits at opaque / platform-owned. ListenBrainz sits at semi-transparent / user-owned. Scripts sit at opaque / user-owned. **Transparent and user-owned with a usable interface is empty.** [Opinion, medium confidence]

## Vulnerabilities to exploit
1. Spotify's notes are generic and tied to Spotify. Rain in My Head can use specific reasons from your own history, such as "140 plays in spring 2014, none since 2017."
2. ListenBrainz has the data but no visible reasoning and a technical interface.
3. The scripts prove there's demand but have no UX.

## Platform risk
Spotify could restrict playlist writes further. ListenBrainz could add visible explanations. Mitigation: keep the playlist logic independent of Spotify (also export M3U files and ListenBrainz JSPF playlists).

## Red flags / yellow flags
- 🔴 Spotify Prompted Playlist already does "explained picks from full history" for Premium users. The difference is depth and ownership, not the feature itself.
- 🟡 The gap is narrow. ListenBrainz could close it.
