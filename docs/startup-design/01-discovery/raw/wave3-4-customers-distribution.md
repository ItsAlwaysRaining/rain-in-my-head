# Wave 3-4: Customer Voice, Demand, Audience, and Distribution

Created: 2026-11-18 / Last updated: 2026-11-18

Product: Rain in My Head (open-source, self-hosted; Last.fm history, taste eras, rediscovery playlists, playlist rules, explained playlists written to Spotify). Purpose: UX portfolio case study. Interviews are deferred, so this desk research stands in for customer voice.

## Method and caveats

- 15 web searches run on 2026-11-18. Most quotes came through search-engine extracts of the pages, not full page reads. Before a quote goes in the final case study, open the link and check the exact wording and date.
- Reddit was hard to reach directly. Many Reddit quotes come through secondary sources (Android Authority, TechRadar, Stagehoppers) or Reddit mirrors. The Spotify Community forum gave the most first-hand complaints.
- Source tiers: **T1** primary or official data (company statements, court filings, GitHub, peer-reviewed research). **T2** reputable press (TechCrunch, TechRadar, Rolling Stone, NN/g). **T3** first-hand user posts (Spotify Community, Reddit, X, Bluesky). **T4** blogs, vendor content, SEO tools, and third-party estimates.
- Labels: **[Data]** a measured or published figure. **[Estimate]** a modeled or third-party figure, or my own inference.

## C1. Customer voice

### Ranked pains

| Rank | Pain | Evidence strength | Product answer |
|---|---|---|---|
| 1 | Stuck in a loop: the same 10-200 songs over and over (DJ, Daily Mix, shuffle, Discover Weekly) | Very high: many threads from 2023 to 2026, plus press coverage | Rediscovery from full history, plus no-repeat rules |
| 2 | Discover Weekly is getting worse and recycles songs the listener already heard or skipped | High: many forum threads, and the problem continued after the 2025 overhaul | Rules such as "not played in 2 years" and "never skipped" |
| 3 | AI-generated "slop" in Discover Weekly and Release Radar, and lost trust | High, rising since 2025: TechRadar, Futurism, DMN, and the "Mark/Disable AI songs" idea thread with 60+ pages | Picks come only from the listener's own scrobbled artists, with an explanation |
| 4 | Ignoring long-term taste, so old favorites are forgotten | Medium-high | Taste eras, plus forgotten-favorites playlists |
| 5 | No explanation of why a song was picked, and a fear of paid promotion (payola) | Medium: one lawsuit, academic work, and a few users | "Why this song" note on every track |
| 6 | Data ownership: Spotify keeps the history and Wrapped once a year is not enough | Medium-low as a pain, but a strong motive for Last.fm users | Self-hosted, and the user owns their Last.fm data |

### Verbatim quotes

Check every quote at its link before using it. [V] means wording quoted in the search extract. [P] means a close paraphrase reported by a secondary source.

| # | Quote | Theme | Source (tier, date) |
|---|---|---|---|
| 1 | "They appear, I swipe them away, and they're back again in a few weeks." [V] | Repeats | Spotify Community, Discover Weekly recycling thread (T3, c. 2022-2024) https://community.spotify.com/t5/Accounts/Discover-Weekly-keeps-recycling-the-same-songs/m-p/5108457 |
| 2 | "Over half of my Discover Weekly songs I've already heard before" [V, thread title] | Repeats | Spotify Community (T3, c. 2022) https://community.spotify.com/t5/Your-Library/Over-half-of-my-Discover-Weekly-songs-I-ve-already-heard-before/m-p/5105574/highlight/true |
| 3 | "Discovery weekly has been progressively getting worse" [V, thread title] | DW decline | Spotify Community (T3, c. 2022) https://community.spotify.com/t5/Your-Library/Discovery-weekly-has-been-progressively-getting-worse/m-p/5359421/highlight/true |
| 4 | "Discover weekly playlist is getting worse month by month" [V, thread title] | DW decline | Spotify Community (T3, 2025) https://community.spotify.com/t5/Social-Random/Discover-weekly-playlist-is-getting-worse-month-by-month/td-p/7059304 |
| 5 | "Does anyone else think the spotify algorithm is getting worse" [V, thread title] | DW decline | Spotify Community (T3, 2025) https://community.spotify.com/t5/Content-Questions/Does-anyone-else-think-the-spotify-algorithm-is-getting-worse/m-p/7113061 |
| 6 | "Spotify Stuck in a Loop" [V, idea title] | Loop | Spotify Community Live Ideas (T3, 2025-2026) https://community.spotify.com/t5/Live-Ideas/Spotify-Stuck-in-a-Loop/idi-p/7332393 |
| 7 | "...only plays the same 10 songs over and over again" (user with about 200 artists) [V] | DJ loop | Spotify Community, "Dj repeats same songs" (T3, 2023-2024) https://community.spotify.com/t5/Android/Dj-repeats-same-songs/m-p/5600021 |
| 8 | "[The DJ] seems to think that I only want to listen to maybe 20 songs" [V] | DJ loop, ignores taste | Spotify Community (T3, 2023-2024) https://community.spotify.com/t5/Android/Dj-repeats-same-songs/m-p/6215025/highlight/true |
| 9 | "Make Spotify DJ less repetitive" [V, idea title] | DJ loop | Spotify Community Live Ideas (T3, 2023-2025) https://community.spotify.com/t5/Live-Ideas/Make-Spotify-DJ-less-repetitive/idi-p/5809645 |
| 10 | Daylist is "essentially just another version of the Daily Mix" [V] | Daylist | Spotify Community (T3, 2025) https://community.spotify.com/t5/Content-Questions/Daylist-seems-to-be-repeating-itself/td-p/7088389 |
| 11 | Spotify support: "there isn't a way to manually reset or refresh your Daylist recommendations" [V] | Lack of control | Same thread (T1 official reply, 2025) |
| 12 | Same 30 songs "five days a week despite having 1,500 songs in their playlist" [P] | Loop | Reddit via Stagehoppers (T4, 2025) https://stagehoppers.com/spotify-algorithm/ |
| 13 | Features feel "stuck in a loop" of roughly "100-200 songs" [P] | Loop | Reddit via Stagehoppers (T4, 2025) https://stagehoppers.com/spotify-algorithm/ |
| 14 | An exact 72-song sequence played twice in identical order on back-to-back days, in a 2,000-song playlist [P] | Shuffle | Reddit via Android Authority (T2, 2025) https://androidauthority.com/spotify-shuffle-repeating-song-queue-3708815 |
| 15 | A third-party shuffler let them hear "songs I had completely forgotten about" [V] | Forgotten favorites | Reddit, quoted in an aggregator (T3/T4, 2025) https://stagehoppers.com/spotify-algorithm/ |
| 16 | "Why is shuffle still absolute garbage" [V, thread title] | Shuffle | r/spotify mirror (T3, 2025-04-21) https://reddit.birdcat.cafe/r/spotify/comments/1k4izqe/why_is_shuffle_still_absolute_garbage |
| 17 | "This has completely broken my trust because I used to feel like Spotify recommendations were made for me." [V] | AI tracks, trust | Spotify Community via TechRadar (T3, 2025) https://www.techradar.com/audio/spotify/ai-music-is-flooding-spotify-and-subscribers-are-furious-heres-why-music-fans-no-longer-trust-discover-weekly |
| 18 | "Discover Weekly is unusable now cause it is just full of AI slop" [V] | AI tracks | X user via TechRadar (T3, 2025) same link as #17 |
| 19 | "Six songs out of 30 on my Discover Weekly playlist on Spotify were AI this week" [V] | AI tracks | Bluesky user via Digital Music News (T3, 2025-10-22) https://www.digitalmusicnews.com/2025/10/22/spotifys-discover-weekly-lists-hit-with-a-deluge-of-ai-slop/ |
| 20 | AI content has become "too much of an occurrence to the point where it no longer looks coincidental" [V] | AI tracks | r/truespotify via TechRadar (T3, 2025) same link as #17 |
| 21 | "Half of the weekly playlists are filled with AI generated..." [V, thread title] | AI tracks | Spotify Community (T3, 2025) https://community.spotify.com/t5/Music-Discussion/Half-of-the-weekly-playlists-are-filled-with-AI-generated/m-p/6288755/highlight/true |
| 22 | "Release Radar this week was almost all AI generated music" [V, thread title] | AI tracks | Spotify Community (T3, 2023-2024) https://community.spotify.com:443/t5/Content-Questions/Release-Radar-this-week-was-almost-all-AI-generated-music/m-p/5633369/highlight/true |
| 23 | "Songs with weird, all-caps artists with AI pictures" and artists with "no text in bios" [V] | AI tracks | Users quoted by Futurism (T2, 2025) https://futurism.com/artificial-intelligence/ai-slop-invading-spotify-discover-weekly-playlists |
| 24 | The plaintiff "cannot discern which songs are recommended for legitimate editorial or personalized reasons and which are promoted due to undisclosed commercial arrangements" [V] | Payola, why this song | Class action reported by Rolling Stone AU (T2/T1, 2025-11) https://au.rollingstone.com/music/music-news/class-action-lawsuit-spotify-payola-discovery-mode-86702/ |
| 25 | Commercial services, Spotify included, "fail to provide any explainability on why a particular song was recommended" [V] | Why this song | arXiv, EXPLORE (T1, 2024) https://arxiv.org/html/2401.00353v1 |
| 26 | "Discover: See what I listened to Days/Months/Years ago" [V, idea title] | Old favorites, history | Spotify Community Live Ideas (T3, long-running) https://community.spotify.com/t5/Live-Ideas/Discover-See-what-I-listened-to-Days-Months-Years-ago/idi-p/1344468 |
| 27 | "Option to turn OFF 'Made for You' customized playlists" [V, idea title] | Algorithm fatigue | Spotify Community Live Ideas (T3) https://community.spotify.com/t5/Live-Ideas/Option-to-turn-OFF-quot-Made-for-You-quot-customized-playlists/idi-p/5952434 |
| 28 | "Help, I think Spotify is making me boring! And it's all AI's fault" [V, headline] | Taste narrowing | TechRadar (T2, 2025) https://techradar.com/computing/artificial-intelligence/help-i-think-spotify-is-making-me-boring-and-its-all-ais-fault |

### Spotify's position (useful counterpoint)

- Spotify says Discovery Mode "doesn't buy plays," is limited to Radio, Autoplay, and some Mixes, and is "clearly disclosed." [Data] T1, 2025-11.
- Spotify says it does not promote or penalize AI tracks, and that "music has always been shaped by technology." [Data] T1 via TechRadar/PiunikaWeb, 2025-2026.
- There is no reliable public measure of the share of AI tracks in Discover Weekly (TechBloat). User counts such as "6 of 30" are anecdotes. [Estimate]

## C2. Demand signals

| Signal | Value | Label | Source (tier, date) |
|---|---|---|---|
| "spotify stats" US monthly searches | about 345K | [Estimate] | Ahrefs (T4, 2025-2026) https://ahrefs.com/websites/statsforspotify.com |
| statsforspotify.com traffic from that keyword | about 93K/mo | [Estimate] | Same |
| stats.fm installs, MAU | about 9M installs, about 327K MAU; developer claims 10M+ users | [Estimate] / claim | AppGoblin (T4) https://appgoblin.info/apps/dev.netlob.spotistats |
| Receiptify mobile clones | about 134K-146K installs each | [Estimate] | AppGoblin (T4) https://appgoblin.info/apps/1622577500 |
| Maloja (self-hosted scrobble DB) GitHub stars | 1.3K to 1.8K | [Data], snapshots | ecosyste.ms (T1/T4) https://awesome.ecosyste.ms/projects/github.com%2Fkrateng%2Fmaloja |
| Koito (self-hosted scrobbler) stars | about 1K; launched on r/selfhosted in 2025 | [Data] | ecosyste.ms; r/selfhosted mirror https://reddit.birdcat.cafe/r/selfhosted/comments/1lau6dq/introducing_koito_a_new_self_hosted_scrobbler_to |
| multi-scrobbler stars | about 1.2K | [Data], snapshot | selfhostyourself.com (T4) https://selfhostyourself.com/tags/scrobbling |
| Last.fm-to-Spotify playlist repos (Nostalgeist, lastfm_pg, Last-Spot, spotkov, Lastgen) | many small repos, mostly under 100 stars | [Estimate] | GitHub (T1) https://www.github.com/tchandler/Nostalgeist, https://github.com/dbeley/lastfm_pg |
| "Forgotten songs" tools exist (Resurface, my scrobbles., Playlistener Time Machine, Rediscover Weekly) | at least 4 small tools | [Data] | https://resurface-cmf.pages.dev/, https://www.producthunt.com/products/my-scrobbles/launches, https://community.spotify.com/t5/Social-Random/Time-Machine-for-making-playlists-from-Lastfm-history-of/td-p/5452743 |
| "Mark/Disable AI-Generated Songs" idea thread | 60+ pages of replies | [Data] | https://community.spotify.com/t5/Live-Ideas/Mark-Disable-AI-Generated-Songs/idi-p/6641329/page/62 |

Not found: search volumes for "forgotten songs playlist" and "last.fm playlist generator", or Reddit upvote counts. [Estimate] Both are long-tail terms, probably under 1K searches a month. Check them in Google Trends or Ahrefs before quoting any number.

Read: there is large demand for stats (wanting to see your listening), and a small niche asks for rediscovery. Many small tools solve one piece each. None combines eras, rules, and explanations. [Estimate]

## C3. Audience profile

- **Last.fm**: about 40M active users in 2009 is the last official figure [Data, outdated] (Erasmus thesis, T1). US audience estimate is about 427K, average age about 30, skewing female [Estimate] (rascasse.com, T4). Profile pages show long-term "lifelogging" listeners, some with 15-20 years of scrobbles (Treble, T2).
- **Behavior**: Last.fm only records plays from the day you connect. Spotify's extended streaming history export is the only route to older history, and it takes a wait [Data] (FreeYourMusic, T4). Many use Last.fm as "Wrapped all year round" (PinkNews 2025-12-06, T2).
- **stats.fm**: mobile-first, Spotify-only, younger and more casual "stats" audience [Estimate].
- **Self-hosted scrobblers** (Maloja, Koito, multi-scrobbler): technical homelab users who value data ownership and run Docker [Estimate].
- **Setup struggles for non-technical users** [Data] T2, 2026-02:
  - Spotify Developer Mode now needs a **Premium** account, has fewer endpoints, and allows fewer test users (reported as down from 25 to 5). Spotify calls it "intentionally limited." (TechCrunch 2026-02-06 https://techcrunch.com/2026/02/06/spotify-changes-developer-mode-api-to-require-premium-accounts-limits-test-users/)
  - Since Nov 2024, new apps lost recommendations, related artists, and audio features (AlternativeTo, T2). Extended access criteria were tightened in May 2025 (Spotify forum, T1).
  - Design implication: every self-hoster must create their own Spotify app (client ID, secret, redirect URI) and a Last.fm API key. For non-technical listeners this is the biggest drop-off risk. The product needs a guided setup with screenshots, clear error messages, and checks for the redirect URI. [Estimate]

## D1. Distribution and portfolio

### Where similar tools got noticed

| Channel | Evidence | Fit |
|---|---|---|
| r/selfhosted | Koito launched with an "Introducing Koito" post and reached about 1K stars (T3/T1) | Best for the technical segment |
| r/lastfm, r/truespotify | Main place for complaints; Playlistener was discussed there (T3) | Best for listeners; follow self-promotion rules |
| awesome-selfhosted, selfhostyourself.com, ecosyste.ms | Maloja and multi-scrobbler are listed (T4) | Long-tail discovery; needs a stable release |
| Product Hunt | "my scrobbles." launched there (T4) | Low effort, small reach |
| Hacker News Show HN | No scrobbler Show HN found in this search | Not tested; worth a try with a demo instance |
| Spotify Community "Live Ideas" threads | Thousands of people already asking for this | Do not spam; cite as evidence |

### What makes the case study stand out to hiring managers

- Show decision quality and the reasoning behind choices, not just polish (UX Planet 2026, T4).
- 54.5% of hiring managers call the research process the most important part [Estimate, vendor survey] (Koji 2026, T4).
- Concrete outcomes and before/after (Toptal, T4). NN/g surveyed over 200 hiring managers: expectations differ by level (T2) https://www.nngroup.com/videos/ux-portfolios-hiring/
- Two or three deep case studies, a role statement at the top, and an easy-to-scan structure (UX Design Institute, T4).
- For this project: real users (stars, installs, Reddit replies) count as outcomes. Show how the explainability design answers the trust gap (quotes 17, 24, and 25). Show the setup-funnel redesign as a hard UX problem.

## Language map (words users actually use)

| User words | Meaning | Use in UI/copy? |
|---|---|---|
| "stuck in a loop", "same 20 songs", "over and over" | Repetition | Yes, in the problem statement |
| "recycling", "already heard", "back again" | DW repeats | Yes |
| "getting worse", "used to be good" | Decline, nostalgia for old DW | Marketing only |
| "AI slop", "fake artists", "no bio" | AI tracks | Careful; use "real artists you've played" |
| "made for me", "trust" | Personal fit | Yes: "picked from your own history" |
| "forgotten about", "songs I forgot", "old days", "rediscover" | Rediscovery | Yes, a core feature name |
| "time machine", "years ago", "what I listened to" | Eras | Yes ("eras" plus "time machine" as a metaphor) |
| "scrobbles", "scrobbling" | Last.fm logging | Yes for Last.fm users; explain it for others |
| "Wrapped all year", "stats" | Wanting to see your history | Yes, a hook |
| "boring", "echo chamber" | Taste narrowing | Marketing only |
| "why was this recommended", "promoted", "payola" | Transparency | Use "why this song" |
| "turn off", "reset", "refresh" | Control | Yes: "rules" |

## Sources

1. https://community.spotify.com/t5/Accounts/Discover-Weekly-keeps-recycling-the-same-songs/m-p/5108457
2. https://community.spotify.com/t5/Your-Library/Over-half-of-my-Discover-Weekly-songs-I-ve-already-heard-before/m-p/5105574/highlight/true
3. https://community.spotify.com/t5/Your-Library/Discovery-weekly-has-been-progressively-getting-worse/m-p/5359421/highlight/true
4. https://community.spotify.com/t5/Social-Random/Discover-weekly-playlist-is-getting-worse-month-by-month/td-p/7059304
5. https://community.spotify.com/t5/Content-Questions/Does-anyone-else-think-the-spotify-algorithm-is-getting-worse/m-p/7113061
6. https://community.spotify.com/t5/Live-Ideas/Spotify-Stuck-in-a-Loop/idi-p/7332393
7. https://community.spotify.com/t5/Android/Dj-repeats-same-songs/m-p/5600021
8. https://community.spotify.com/t5/Android/Dj-repeats-same-songs/m-p/6215025/highlight/true
9. https://community.spotify.com/t5/Live-Ideas/Make-Spotify-DJ-less-repetitive/idi-p/5809645
10. https://community.spotify.com/t5/Content-Questions/Daylist-seems-to-be-repeating-itself/td-p/7088389
11. https://community.spotify.com/t5/Live-Ideas/Option-to-turn-OFF-quot-Made-for-You-quot-customized-playlists/idi-p/5952434
12. https://community.spotify.com/t5/Live-Ideas/Discover-See-what-I-listened-to-Days-Months-Years-ago/idi-p/1344468
13. https://community.spotify.com/t5/Live-Ideas/Mark-Disable-AI-Generated-Songs/idi-p/6641329/page/62
14. https://community.spotify.com/t5/Music-Discussion/Half-of-the-weekly-playlists-are-filled-with-AI-generated/m-p/6288755/highlight/true
15. https://community.spotify.com:443/t5/Content-Questions/Release-Radar-this-week-was-almost-all-AI-generated-music/m-p/5633369/highlight/true
16. https://community.spotify.com/t5/Social-Random/Time-Machine-for-making-playlists-from-Lastfm-history-of/td-p/5452743
17. https://www.techradar.com/audio/spotify/ai-music-is-flooding-spotify-and-subscribers-are-furious-heres-why-music-fans-no-longer-trust-discover-weekly
18. https://www.techradar.com/audio/spotify/spotify-denies-its-pushing-unwanted-ai-slop-onto-subscribers-claiming-it-does-not-promote-or-penalize-tracks-created-using-ai-tools
19. https://techradar.com/computing/artificial-intelligence/help-i-think-spotify-is-making-me-boring-and-its-all-ais-fault
20. https://www.digitalmusicnews.com/2025/10/22/spotifys-discover-weekly-lists-hit-with-a-deluge-of-ai-slop/
21. https://futurism.com/artificial-intelligence/ai-slop-invading-spotify-discover-weekly-playlists
22. https://piunikaweb.com/2026/01/05/youtube-music-ai-slop-recommendations-problem/
23. https://au.rollingstone.com/music/music-news/class-action-lawsuit-spotify-payola-discovery-mode-86702/
24. https://faroutmagazine.co.uk/spotify-accused-modern-payola-lawsuit-discovery-mode/
25. https://androidauthority.com/spotify-shuffle-repeating-song-queue-3708815
26. https://stagehoppers.com/spotify-algorithm/
27. https://reddit.birdcat.cafe/r/spotify/comments/1k4izqe/why_is_shuffle_still_absolute_garbage
28. https://www.aol.com/spotify-great-helping-discover-music-081001557.html
29. https://arxiv.org/html/2401.00353v1
30. https://www.frontiersin.org/articles/10.3389/fdata.2021.693494/pdf
31. https://repositum.tuwien.at/handle/20.500.12708/209944
32. https://ahrefs.com/websites/statsforspotify.com
33. https://appgoblin.info/apps/dev.netlob.spotistats
34. https://appgoblin.info/apps/1622577500
35. https://awesome.ecosyste.ms/projects/github.com%2Fkrateng%2Fmaloja
36. https://reddit.birdcat.cafe/r/selfhosted/comments/1lau6dq/introducing_koito_a_new_self_hosted_scrobbler_to
37. https://selfhostyourself.com/tags/scrobbling
38. https://www.github.com/tchandler/Nostalgeist
39. https://github.com/dbeley/lastfm_pg
40. https://gh.r-mj.com/coplat/last-spot
41. https://resurface-cmf.pages.dev/
42. https://www.producthunt.com/products/my-scrobbles/launches
43. https://worker-github.shheric.workers.dev/coryrwest/rediscover-weekly
44. https://pixelbrix-site.pages.dev/experiments/music-discovery-tool/
45. https://thesis.eur.nl/pub/10564/Cooke,%20L.J.pdf
46. https://rascasse.com/explore/us/lastfm-8838
47. https://www.treblezine.com/?p=106045
48. https://www.thepinknews.com/2025/12/06/spotify-wrapped-last-fm/
49. https://freeyourmusic.com/blog/spotify-extended-streaming-history
50. https://techcrunch.com/2026/02/06/spotify-changes-developer-mode-api-to-require-premium-accounts-limits-test-users/
51. https://alternativeto.net/news/2024/11/spotify-limits-features-from-is-web-api-impacting-third-party-developers-and-ai-apps
52. https://community.spotify.com/t5/Spotify-for-Developers/Updating-the-Criteria-for-Web-API-Extended-Access/td-p/6920661/page/8
53. https://www.nngroup.com/videos/ux-portfolios-hiring/
54. https://uxplanet.org/why-good-ux-portfolios-never-get-interviews-in-2026-11-hiring-red-flags-6ea28fb2f9b3
55. https://www.koji.so/blog/ux-research-portfolio-guide-2026
56. https://www.toptal.com/designers/ux/ux-portfolio-tips-recruiter
57. https://www.uxdesigninstitute.com/blog/hiring-managers-ux-portfolio/
