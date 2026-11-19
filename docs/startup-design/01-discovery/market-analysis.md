# Market Analysis: Rain in My Head

Created: 2026-11-18
Last updated: 2026-11-18

**Phase:** 3 · **Confidence:** Medium · Sources: [raw/wave1-market-trends-regulatory.md](raw/wave1-market-trends-regulatory.md), [raw/wave3-4-customers-distribution.md](raw/wave3-4-customers-distribution.md)

> This is a portfolio project with no revenue goal. "Market" here means *who has this problem and how many of them could self-host*, not TAM in dollars.

## Sizing (people, not dollars)
| Layer | Size | Label | Confidence |
|---|---|---|---|
| Spotify monthly users / Premium subscribers (Q3 2026) | 788M / 306M | [Data] tier 1, SEC filing | High |
| Wrapped 2025 engagement | 300M+ users, 630M shares | [Data] tier 2 | High |
| People who already track their listening (stats.fm, Last.fm, ListenBrainz) | ~9M stats.fm installs (~327K monthly users), ~100K ListenBrainz | [Estimate] tier 3, undated | Low |
| People who could self-host (r/selfhosted) | 790K+ members | [Estimate] tier 3, undated | Low |
| **Realistic reach:** Premium users who track their listening *and* can self-host | Low thousands | [Opinion] | Low |

**Takeaway:** Interest is huge (Wrapped) but the self-host funnel is tiny. That's fine for a portfolio piece. The case study should show that you understand this funnel.

## Platform and regulatory constraints
- [Data] Writing playlists in Spotify's development mode still works: `POST /me/playlists` creates a playlist and `POST /playlists/{id}/items` adds tracks. The old `/users/{id}/playlists` and `/playlists/{id}/tracks` endpoints were removed or return 403 since February and March 2026.
- [Data] Development mode requires the app owner to have **Premium**, allows **at most 5 users** per app, and gives one dev Client ID per developer. Extended access requires a business with 250K+ monthly active users, which this project will never have.
- [Data] Since November 2024, new apps **can't use** Recommendations, Audio Features, Audio Analysis, or Related Artists. Mood or energy rules need Last.fm tags or another source.
- [Data] The Last.fm API is free for non-commercial use, which fits this project.
- [Estimate] Spotify's extended streaming-history export (GDPR) can fill in history from before Last.fm tracking. This needs verifying.

## Timing
Good. The AI-music backlash (75M spam tracks removed in September 2025, a 60+ page forum thread asking for AI-song filters, and a November 2025 payola class action) makes "explained, from your own history" a timely angle. [Data]

## Red flags / yellow flags
- 🟡 Each user needs Spotify Premium and their own developer app. This is softened because the real product runs locally and Claude walks the user through setup. The hard, hosted setup flow is a portfolio piece only.
- 🟡 No audio features from Spotify, so rules are limited to history, time, artist, and tags.
