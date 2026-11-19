# Wave 1: Market, Trends, and Regulatory Raw Findings (Rain in My Head)

Created: 2026-11-18 / Last updated: 2026-11-18

Context: UX portfolio case study, not a business. 11 web searches run on 2026-11-18. Source tiers: T1 = analyst/official, T2 = tech/trade press, T3 = blogs/forums/directories. "STALE" = data older than 18 months (before 2025-05-18).

## A1. Market sizing

| Metric | Figure | Date | Tier | Tag | Notes |
|---|---|---|---|---|---|
| Spotify MAU | 788M (+11% YoY, from 713M) | Q3 2026, reported 2026-10-22 | T1 (SEC 6-K) | [Data] | Q4 2026 guidance: 818M |
| Spotify Premium subscribers | 306M (+9% YoY, from 281M) | Q3 2026 | T1 | [Data] | Q4 2026 guidance: 316M |
| Spotify Wrapped launch engagement | 200M users in first 24h (+19% YoY); 500M+ shares day one (+41%) | Dec 2025 | T2 (MBW, Music Week) | [Data] | 2024 hit 200M only after 62h |
| Wrapped full campaign | 300M+ users, 630M shares | Q4 2025 earnings, Feb 2026 | T2 | [Data] | Campaign total, not comparable to 24h figure. 2024 full campaign: 245M |
| stats.fm users | "9M+ users" | Undated | T3 (AlternativeTo, marketing copy) | [Estimate] | Unverified self-claim |
| Last.fm users | No official count; Android app ~290K MAU | Oct 2025 | T3 (AppGoblin) | [Estimate] | App-only; excludes web and scrobblers |
| ListenBrainz users | ~100K (up from ~36K a year earlier) | Undated community post, likely 2025 | T3 (Lemmy) | [Estimate] | Undated; verify on ListenBrainz stats page |
| r/selfhosted | 790K+ members | Undated (DreamHost blog, ~2026) | T3 | [Estimate] | Reddit blocks unauthenticated counts (Findstack) |
| selfh.st self-host survey | 4,000+ respondents; 98.3% use containers (from 97%) | 2025 | T3 | [Data] | Useful as persona proxy (Docker is the default install path) |
| r/lastfm subscribers | Not found | - | - | - | Gap; check manually |
| "Music stats" niche size | No analyst figure found | - | - | [Estimate] | Rough proxy: Wrapped 200-300M engaged per year vs stats.fm ~9M and ListenBrainz ~100K, so year-round stats tools reach roughly 1-5% of Wrapped's audience |

Contradictions: none on Spotify figures (all sources match the 6-K). Wrapped 200M vs 300M is a 24h vs campaign difference, not a conflict.

## A2. Trends

- **AI playlists.** Spotify "Prompted Playlist" (beta, Premium, English) reported January 2026 (T2: gHacks, heise, Techloy). [Data] Markets conflict: US and Canada (Techloy) vs New Zealand first (heise). Coexists with 2024 "AI Playlist" (UK/Australia beta, later 40+ markets). AI DJ (2023) and Daylist (Sept 2023) remain; no usage numbers found. Daylist/AI DJ data is STALE.
- **AI music backlash.** Spotify removed 75M+ "spammy" tracks in the 12 months to Sept 2025 and added impersonation, spam-filter, and AI-disclosure (DDEX credits) policies (T2: Variety, MBW, 2025-09-25). [Data] The Velvet Sundown (AI act, 1M+ monthly listeners, mid-2025) stayed up. Deezer: ~28% of daily uploads fully AI-generated but ~0.5% of streams (T2). [Data] Spotify did not split AI vs other spam. Relevance: "explained, human-history-based" picks are a counter-positioning to opaque AI curation.
- **Data ownership and portability.** GDPR Art. 15/20 export; Spotify's Privacy page offers "Extended streaming history" (full lifetime plays as JSON, typically delivered within ~30 days). [Estimate: from prior knowledge, not re-verified this wave] This is the most robust ingest path because it bypasses API limits.
- **Self-hosting.** Steady growth signal (survey size, Docker ubiquity), but no reliable growth rate. [Estimate]
- **Nostalgia and rediscovery.** Wrapped's record year-on-year growth (+19% in 24h engagement) and the "listening age" feature going viral (Fast Company, Dec 2025, T2) suggest appetite for looking back at one's own taste. [Estimate: inference]

## A3. Regulatory and platform

### Spotify Web API timeline
1. **2024-11-27 (T1, Spotify developer blog), STALE but still in force.** New apps lost Related Artists, Recommendations, Audio Features, Audio Analysis, Get Featured Playlists, Category Playlists, and 30s preview URLs. Existing extended-quota apps kept them. [Data] Implication: no tempo/energy/valence "vibe" rules from Spotify; must use Last.fm tags, ListenBrainz/AcousticBrainz-style data, or local analysis.
2. **2025-05-15 (T3, Spotify Community moderator posts).** Extended Quota accepted from organizations only: registered business, launched service, 250K+ MAU, key markets, analytics proof. Existing extensions grandfathered. [Data, T3] Implication: a solo open-source project can never leave Development Mode.
3. **2026-02-11 new Client IDs / 2026-03-09 existing (T2: TechCrunch 2026-02-06; T1: Spotify Feb 2026 changelog and migration guide).** Development Mode now requires the app owner to have Premium; max 5 authorized users (down from 25); one Dev Mode Client ID per developer; reduced endpoint set; search capped at 10 results (T3). [Data]
4. **2026-03 changelog (T1).** Reverted only the `external_ids` removal on albums and tracks. Playlist `/tracks` to `/items` change was NOT reverted. [Data]
5. **2026-07-23 (T3 only, unconfirmed).** Reports that Client ID limit rose to 25 per developer with a shared quota and `QUOTA_EXCEEDED` 429s. [Estimate] Verify on Spotify changelog.

### Playlist write in Development Mode (as of 2026-11-18)
- Create: `POST /me/playlists` (replaces removed `POST /users/{user_id}/playlists`). [Data, T1]
- Add tracks: `POST /playlists/{playlist_id}/items` (replaces `/playlists/{id}/tracks`, which now returns 403 in dev mode). [Data, T1 + T3 dev reports] Sibling item endpoints (GET/PUT/DELETE `/playlists/{id}/items`) follow the same rename. [Estimate]
- Description: playlist `description` field can carry the "why this song" summary (per-track explanations must live in the app, since Spotify has no per-track note field). [Estimate]
- Removed: `GET /users/{id}/playlists`; playlist contents only returned for playlists the user owns or collaborates on (T3). [Data/T3]
- Scopes needed: `playlist-modify-private` / `playlist-modify-public`. [Estimate: standard OAuth scopes]
- Constraints: each self-hoster registers their own app (own Client ID), owner must be Premium, max 5 users per instance. This fits a self-hosted, single-household model well. [Data + inference]

Contradictions: count of endpoints removed in Feb 2026 ("15" per Headphonesty vs longer lists in changelog); extended quota "registered business" vs "organizations".

### Last.fm API
- Non-commercial use only; commercial, research, or academic use needs prior contact (partners@last.fm); breach allows termination (T1, last.fm/api/tos, undated page). [Data] Open-source, free, self-hosted use fits. A portfolio case study is fine; a paid hosted version would not be without an agreement.
- Rate limit ~5 req/s (T3, unconfirmed). [Estimate]

## Gaps
r/lastfm size, official Last.fm and stats.fm counts, Daylist/AI DJ usage, Spotify March/July 2026 changelog full text, ListenBrainz dated count.

## Sources
- Spotify Q3 2026 6-K (T1): https://www.sec.gov/Archives/edgar/data/0001639920/000114036126040435/ef20084028_ex99-1.htm
- Hypebot Q3 2026: https://www.hypebot.com/spotify-q3-2026-788m-users-and-306m-subscribers/
- MBW Q3 2026: https://musicbusinessworldwide.com/spotify-is-on-course-for-a-3-3b-annual-operating-profit-in-2026-after-adding-6m-subscribers-in-q3
- MBW Wrapped 2025: https://www.musicbusinessworldwide.com/spotify-wrapped-campaign-hit-200m-engaged-users-in-24-hours-a-19-yoy-increase
- Music Week Wrapped 2025: https://www.musicweek.com/digital/read/spotify-wrapped-2025-was-biggest-ever-with-200-million-engaged-users/093178
- Fast Company Wrapped listening age: https://www.fastcompany.com/91454685/spotify-wrapped-2025-eagerly-checking-your-listening-age-everyone-else-is-too
- AlternativeTo ListenBrainz/stats.fm: https://alternativeto.net/software/listenbrainz
- AppGoblin Last.fm Android: https://appgoblin.info/apps/fm.last.android
- ListenBrainz 100K post: https://elektrine.com/post/772509
- DreamHost self-hosting 2026: https://www.dreamhost.com/blog/self-hosting/
- Findstack self-hosting stats: https://findstack.com/resources/self-hosting-statistics
- selfh.st 2025 survey: https://selfh.st/survey/2025-results/
- gHacks Prompted Playlist: https://www.ghacks.net/2026/01/23/spotify-introduces-prompted-playlist-ai-feature/
- heise Prompted Playlist: https://heise.de/-11111341
- Techloy Prompted Playlist: https://www.techloy.com/spotify-rolls-out-ai-powered-prompted-playlists-in-the-u-s-and-canada/
- TechCrunch AI playlists 2024: https://techcrunch.com/2024/04/07/spotify-launches-personalized-ai-playlists-you-can-build-using-prompts/amp
- Variety AI safeguards: https://au.variety.com/2025/digital/news/spotify-new-ai-safeguards-28228
- MBW 75M tracks: https://www.musicbusinessworldwide.com/spotify-has-deleted-75m-spammy-tracks-as-it-unveils-new-ai-music-policies/
- Spotify Nov 2024 Web API changes (T1): https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api
- TechCrunch Nov 2024: https://techcrunch.com/2024/11/27/spotify-cuts-developer-access-to-several-of-its-recommendation-features
- Spotify Community extended access criteria: https://community.spotify.com/t5/Spotify-for-Developers/Updating-the-Criteria-for-Web-API-Extended-Access/td-p/6920661/page/6
- Spotify Community Feb 2026 thread: https://community.spotify.com/t5/Spotify-for-Developers/February-2026-Spotify-for-Developers-update-thread/m-p/7368381
- TechCrunch Feb 2026 dev mode: https://techcrunch.com/2026/02/06/spotify-changes-developer-mode-api-to-require-premium-accounts-limits-test-users/
- Spotify Feb 2026 changelog (T1): https://developer.spotify.com/documentation/web-api/references/changes/february-2026
- Spotify Mar 2026 changelog (T1): https://developer.spotify.com/documentation/web-api/references/changes/march-2026
- Spotify Feb 2026 migration guide (T1): https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide
- Headphonesty Feb 2026: https://www.headphonesty.com/2026/02/spotify-crackdown-thousands-third-party-music-apps/
- Vorplabs API changes 2026: https://vorplabs.com/agent-tools/spotify-api-changes
- rspotify issue #550: https://github.com/ramsayleung/rspotify/issues/550
- your_spotify_v2 issue #5: https://github.com/razday/your_spotify_v2/issues/5
- Last.fm API ToS (T1): https://www.last.fm/api/tos
