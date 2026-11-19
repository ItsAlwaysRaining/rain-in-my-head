# Wave 2: Competitor Landscape for Rain in My Head

Created: 2026-11-18 / Last updated: 2026-11-18

Context: UX portfolio case study, not a business. Rain in My Head is an open-source, self-hosted app that reads a user's full Last.fm history, lets them explore eras of their taste (time-machine), surfaces forgotten favorites, applies user-set playlist rules, and writes explained playlists ("why this song was picked") to Spotify.

Method: 13 web searches on 2026-11-18. No pages were fetched in full, so figures come from search snippets and secondary sources.

**Source tiers.** T1 = official vendor page, docs, or repo. T2 = established tech press (TechCrunch, Engadget, The Next Web, MacRumors). T3 = aggregators, blogs, vendor marketing about rivals, and forums. **[Data]** = a figure stated in a source. **[Estimate]** = my inference or a figure from an unreliable source. Every figure is dated by when the source captured it, where known.

**Verification gaps (said up front).** Calliope, Lastgen, and the MusicBee playlist plugin did not show up as identifiable products in search. Volt.fm returned nothing. Their rows come from my own knowledge only and are marked "unverified". Re-check them before quoting them in the case study.

---

## 1. Comparison matrix

Legend: Y = yes, P = partial, N = no, ? = unverified.

| Name | Product | Pricing | Target | Funding | Traction | Writes to Spotify | Full history | Explains picks | Key strength | Key weakness |
|---|---|---|---|---|---|---|---|---|---|---|
| **Spotify Prompted Playlist** | Natural-language prompt makes an AI playlist that can refresh | Included with Premium (US/CA, English only) | Mainstream Premium users | Spotify (public company) | Rolled out to US and Canada Premium users in 2026 [Data, T1/T2] | Y (native) | Y: "entire listening history from when you first joined Spotify" [Data, T3] | **Y: a short note on each track saying why it fits** [Data, T1] | Has the closest version of the explained-picks idea, with no setup | Spotify-only history (no Last.fm, no other players). Spotify owns the data and the model. Notes are generic one-liners that some users find "extremely annoying" [Data, T3] |
| **Spotify Taste Profile** | View and edit, in natural language, the model Spotify has of your taste | Premium (beta) | Premium users 18+ | Spotify | Announced at SXSW on 2026-03-13. NZ beta, then US from about 2026-09-23 [Data, T2/T3] | N/A (steers recommendations) | Y (Spotify only) | P: shows the model, not reasons for each track | Openness about the model, with the user in control | No playlists of its own. You can't export it. Data stays with Spotify |
| **Discover Weekly / Daylist / AI DJ** | Recommendation playlists and an AI host | Free or Premium (DJ is Premium) | All Spotify users | Spotify | Very large; Spotify had about 713M MAU in an older report [Data, T3, date unclear] | Y | P (weighted toward recent plays) | P: DJ gives spoken intros, Daylist gives mood names | Default habit, no effort | Leans toward new music, not rediscovery. Black box |
| **Spotify Wrapped** | Annual year-in-review story | Free | All Spotify users | Spotify | Cultural event each December [Data, T2] | Y ("Your Top Songs" playlist) | N (one year) | P (narrative stats) | Shareability | Once a year, one year only. No rules |
| **Apple Music Replay** | Monthly and yearly listening recap | Included with Apple Music | Apple Music users | Apple | Replay 2025 launched 2025-12-02, with yearly summaries for every year on the service [Data, T2] | N (Apple Music only) | P (since joining Apple Music) | N | Monthly cadence, history across years | Locked to Apple, no Spotify |
| **YouTube Music Recap** | Annual recap with "ask about your listening" AI | Free | YT Music users | Google | YT Music about 125M subscribers (older figure) [Data, T3] | N | N | P (AI Q&A) | Conversational recap | Annual. Locked to Google |
| **stats.fm** | Spotify/Apple Music stats app. Plus tier imports the extended streaming history | Free. Plus is a one-time purchase (store tiers about $2.99 to $20.99; exact price unclear) [Data, T1/T3, 2026-03] | Stats-obsessed Spotify users, often teens and young adults | Indie / bootstrapped [Estimate] | 10M to 15M+ users or installs claimed by third parties [Estimate, T3] | P (exports some top-lists as playlists) [Estimate] | **Y with Plus** (Spotify's extended history; the export takes up to 30 days) [Data, T1] | N | Largest stats audience, polished mobile UX | Looks backward only: stats, not curation. Users report sync bugs after import [Data, T3]. Hosted, not self-owned |
| **Last.fm** | The original scrobbler with charts, profile, and recommendations | Free. Pro subscription (current price not confirmed) | Long-term music nerds, 20+ year users | Owned by Paramount [Estimate] | Biggest long-term history dataset, in the tens of millions of accounts [Estimate] | N | Y (it *is* the history) | N | The history source Rain in My Head reads from | Stagnant product. Doesn't write playlists or explain anything |
| **ListenBrainz + Troi** | Open, nonprofit scrobble database plus an open recommendation and playlist engine | Free (MetaBrainz nonprofit) | Open-data and self-host enthusiasts | Nonprofit (MetaBrainz) | Year in Music 2025 shipped 2026-01-02 [Data, T1] | **Y** (LB can export playlists to Spotify) [Data, T1/T3] | Y (and can import Last.fm history) | P: playlist names and scripts are open ("Top Missed", "Top Discoveries"), but no reason per track [Data, T1] | Open source, open data, ethical. Has a "Top Missed" rediscovery playlist | Experience aimed at engineers. Explanations live in the code, not the UI |
| **Nostalgeist** | GitHub script: a playlist from a random week of your Last.fm history | Free, OSS | Developers | None | Small repo, no releases [Data, T1] | Y | Y (Last.fm) | N | Closest match to the "time-machine" idea | Random week only, no rules, no UI, inactive |
| **Last-Spot / Spotify My Station** | Hobby scripts: Last.fm history to Spotify playlists (My Station adds an LLM for discovery) | Free, OSS | Developers | None | Very small [Estimate] | Y | Y / P | N | Proves the pipeline works | Command line only, no explanations, no exploring |
| **Smarter Playlists** | Visual rule-graph playlist builder (Paul Lamere) | Free | Power users | None (side project) | Long-running community, r/smarterplaylists [Data, T3] | Y | P (Spotify sources, can't read Last.fm counts) | N | Best rule engine around | Old UI. Spotify API restrictions threaten it. Successor algRHTM was "pending Spotify approval" in 2022 [Data, T1] |
| **Raygum** | Listening *diary* with ratings and notes; Spotify opt-in | Freemium [Estimate] | Reflective listeners | Unknown | Small [Estimate] | N | P (from opt-in onward) | P (*your own* notes about why music mattered) | The "why it matters" framing is close to ours | Not a scrobbler or playlist tool, by its own FAQ [Data, T1] |
| **Free Your Music Stats** | Stats across 20+ services, plus a playlist transfer business | Basic stats free. Transfer is paid | Users switching services | Bootstrapped company [Estimate] | Unknown | Y (transfer, not curation) | N (Spotify's 4 weeks, 6 months, and long-term windows) [Data, T1] | N | Works with many services | Stats are shallow. Its blog content also acts as SEO aimed at competitors |
| **Receiptify** | Top tracks shown as a shareable receipt | Free | Casual social sharers | None | Went viral in 2021, size unknown [Estimate] | P | N | N | Shareability | Gimmick. Exposed to Spotify API policy [Data, T3] |
| **Obscurify** | "How obscure is your taste" score | Free | Casual users | None | Unknown | P | N | P (an obscurity score, not reasons per track) | Fun identity hook | Spotify windows only. API risk |
| **Volt.fm** | Spotify stats profile pages | Free | Casual | ? | ? (no search results) | ? | N | N | — | Unverified, possibly inactive |
| **YourSpotify (your_spotify)** | Self-hosted Spotify stats dashboard, imports the extended history | Free, OSS | Self-hosters | None | About 4.6k GitHub stars [Data, T3, snapshot date unclear] | N | Y (via import) | N | The most popular self-hosted option. Proves self-hosters want this | Stats only. Spotify only |
| **Maloja** | Self-hosted scrobble database | Free, OSS | Self-hosters | None | About 1.6k to 1.8k stars [Data, T3] | N | Y | N | Data ownership | No playlists or recommendations |
| **Koito** | Newer self-hosted scrobbler compatible with ListenBrainz | Free, OSS | Self-hosters | None | About 0.7k to 1k stars; launched on r/selfhosted in 2025 [Data, T3] | N | Y | N | Fast growth from one Reddit launch | No playlists |
| **multi-scrobbler** | Sends scrobbles from many sources to Last.fm, LB, and Maloja | Free, OSS | Self-hosters | None | About 642 stars (older snapshot) [Data, T3] | N | N/A | N | Plumbing for data ownership | Infrastructure, not an experience |
| **MusicBee playlist plugins / auto-playlists** | Local-library rule playlists using play counts | Free | Windows local-library users | None | ? (unverified) | N | P (local counts) | N | Rules | Local files only. Unverified |
| **Spotalike / Magic Playlist / Chosic** | A seed song becomes a similar-songs playlist (Spotalike uses Last.fm similarity) | Free | Casual users | None or ads | Unknown [Estimate] | Y | N | N | Instant | Doesn't use the *user's* history |
| **PlaylistAI** | Prompt, poster, or TikTok becomes a playlist; can use listening history | Freemium subscription [Estimate] | Mainstream | VC-backed? [Estimate] | Covered in the press since 2023 [Data, T3] | Y | N (Spotify windows) | N | Lots of input types | Spotify's own feature now replaces it |
| **Calliope / Lastgen** | — | — | — | — | Not found in search (unverified) | ? | ? | ? | — | Could not confirm they exist |

---

## 2. Closest competitors (ranked by overlap)

1. **Spotify Prompted Playlist.** It is the only product found that ships notes for each track explaining why a song was picked, and it uses the user's whole Spotify history. It is the biggest threat to the "explained picks" angle.
2. **ListenBrainz + Troi.** Open, nonprofit, uses full history, writes to Spotify, and has a "Top Missed" playlist that is essentially forgotten favorites. What it lacks is a consumer UX and visible explanations in the interface.
3. **stats.fm (Plus).** Full imported history and a huge audience, but it is about stats, not curation or explanation.
4. **Nostalgeist, Last-Spot, and Smarter Playlists.** Each covers one piece (time-machine, the Last.fm-to-Spotify pipeline, rules) as a developer tool.
5. **YourSpotify, Maloja, and Koito.** Prove the self-hosted audience exists, but stop at dashboards.

## 3. Is the combination unoccupied?

Four attributes: (a) explains picks, (b) full long-term history, (c) writes to Spotify, and (d) user owns the data.

| Product | a | b | c | d |
|---|---|---|---|---|
| Spotify Prompted Playlist | Y | Y (Spotify only) | Y | **N** |
| ListenBrainz + Troi | P (code, not UI) | Y | Y | Y (open data, hosted by a nonprofit; self-host is possible) |
| stats.fm Plus | N | Y | P | N |
| Nostalgeist / Last-Spot | N | Y | Y | Y |
| YourSpotify / Maloja / Koito | N | Y | N | Y |

**Verdict [Estimate]:** No product found has all four together, so the combination is technically unoccupied. The gap is narrower than it looks, though:
- "Explained picks" alone is no longer new. Spotify shipped it to millions in 2026. The difference has to be *what* gets explained: specific reasons from the user's own history ("you played this 140 times in spring 2014, then not once since 2017"), compared with Spotify's general "fits your vibe" notes.
- ListenBrainz is one product decision away from closing the gap: it would only need to show its Troi reasoning in the UI. Treat it as an ally or a data source (open, Last.fm import) rather than a rival.
- The parts that are clearly defensible are **Last.fm as the source** (decades of history from many players, which Spotify can't see), **time-machine eras**, **user-written rules**, and **explanations tied to specific history**, all on a **self-hosted** stack.

## 4. Platform risk (affects everyone in column c)

- In Nov 2024 Spotify cut recommendation, related-artist, and some playlist endpoints for new and development-mode apps [Data, T2, TechCrunch 2024-11-27].
- From 2025-05-15, only organizations can get extended API access [Data, T1, Spotify community].
- There are reports that new app creation was disabled on 2025-12-28, that developer access requires Premium, and that test users were cut from 25 to 5 [Data, T3, Headphonesty 2026-02; not confirmed against T1].
- What this means: a self-hosted app where each user registers their own developer app and uses only core endpoints (read history from Last.fm, *write* playlists to Spotify) is the most realistic design, but its setup is hard. That setup is a core UX problem for the case study.

## 5. Go-to-market for the open-source players

- **Reddit is the main channel.** Koito launched with an "Introducing Koito" post on r/selfhosted (2025) and reached about 1k stars [Data, T3]. YourSpotify, Maloja, and multi-scrobbler all spread through r/selfhosted, r/lastfm, and r/truespotify threads asking "alternative to Last.fm or Wrapped" [Estimate].
- **Self-host directories** (selfhostyourself.com, AlternativeTo, awesome-selfhosted, LinuxLinks, ElfHosted's one-click store) give a long tail of discovery [Data, T3: all of these list Maloja, Koito, and multi-scrobbler].
- **Docker Hub, Unraid, and Flatpak packaging** lowers the install barrier. multi-scrobbler has an Unraid support thread and a Flatpak [Data, T1/T3].
- **Seasonal hooks.** Wrapped season (late Nov to Dec) drives "Wrapped alternative" searches. Free Your Music writes SEO content to catch it [Data, T1]. ListenBrainz publishes Year in Music in early January [Data, T1].
- **Product Hunt / Hacker News.** Only minor evidence for OSS tools in this space (an HN-mirrored self-hosted LB and Navidrome playlist post, 2026-01) [Data, T3]. Matters less than Reddit [Estimate].
- **Lesson for the case study:** time a demo post for r/selfhosted and r/lastfm around Wrapped season, ship a Docker one-liner, and list the app in awesome-selfhosted and AlternativeTo.

---

## Sources

1. stats.fm Plus FAQ (T1): https://support.spotistats.app/cs-CZ/docs/statsfm-plus/faq
2. stats.fm Spotify import guide (T1): https://support.spotistats.app/docs/import/spotify-import
3. App Pricing Lab, stats.fm IAP tiers, 2026-03-10 (T3): https://apppricinglab.com/app/apple/1526912392
4. stats.fm user claims (T3): https://marlvel.ai/api/llm/apps/music/stats-fm-for-spotify-music-app ; https://appgoblin.info/apps/dev.netlob.spotistats
5. Spotify community, stats.fm import sync issue (T3): https://community.spotify.com/t5/Other-Podcasts-Partners-etc/why-does-stats-fm-not-show-my-full-stream-history-despite-being/td-p/5949555
6. Spotify support, Prompted Playlists (T1): https://support.spotify.com/ca-en/article/prompted-playlists/
7. Engadget, Prompted Playlist (T2): https://www.engadget.com/entertainment/music/spotifys-new-playlist-feature-gives-users-more-control-over-their-recommendation-algorithm-203237903.html
8. Platformer, Prompted Playlists review (T2): https://platformer.news/spotify-prompted-playlists-ai-meta-vibes
9. AI Musicpreneur, full history claim (T3): https://www.aimusicpreneur.com/ai-music-news/spotify-prompted-playlists-music-discovery/
10. TechCrunch, Taste Profile, 2026-03-13 (T2): https://techcrunch.com/2026/03/13/spotify-will-let-you-edit-your-taste-profile-to-control-your-recommendations/
11. Technobezz, Taste Profile US rollout (T3): https://www.technobezz.com/news/spotify-taste-profile-beta-us-premium-listeners
12. MetaBrainz wiki, YIM playlists and Troi scripts (T1): https://wiki.musicbrainz.org/YIM2023Playlists
13. Troi repo (T1): https://github.com/metabrainz/troi-recommendation-playground
14. MetaBrainz blog, Year in Music 2025 (T1): https://blog.metabrainz.org/2026/01/02/year-in-music-2025-new-and-improved/
15. MetaBrainz forum, GSoC 2024 playlist export (T1): https://community.metabrainz.org/t/gsoc-2024-exporting-playlists-to-soundcloud-and-apple-music/684354
16. Self-hosted LB and Navidrome discovery playlists, 2026-01-22 (T3): https://hn.jakechampion.name/reader/https://chhs1.github.io/blog/2026/01/22/self-hosted-discovery-playlists.html
17. Nostalgeist repo (T1): https://www.github.com/tchandler/Nostalgeist
18. Last.fm "Forgotten" discovery experiment (T3): https://pixelbrix-site.pages.dev/experiments/music-discovery-tool/
19. Last-Spot (T3): https://gh.r-mj.com/coplat/last-spot
20. Spotify My Station (T3): https://awesome.ecosyste.ms/projects/github.com%2Frollecode%2Fspotify-my-station
21. Smarter Playlists, Paul Lamere (T1): https://musicmachinery.com/2015/07/25/smarter-playlists/ ; https://musicmachinery.com/
22. r/smarterplaylists (T3): https://axebps-redlib.hf.space/r/smarterplaylists
23. Raygum, Last.fm alternative page (T1): https://raygum.com/last-fm-alternative
24. Free Your Music Stats (T1): https://freeyourmusic.com/stats/list ; https://freeyourmusic.com/blog/spotify-stats-apps
25. Receiptify page (T3): https://hackmd.io/@receiptifytool/H1WJMjPs-x
26. Spotify community, API extended access criteria (T1): https://community.spotify.com/t5/Spotify-for-Developers/Updating-the-Criteria-for-Web-API-Extended-Access/m-p/6937587/highlight/true
27. TechCrunch, Spotify cuts recommendation API, 2024-11-27 (T2): https://techcrunch.com/2024/11/27/spotify-cuts-developer-access-to-several-of-its-recommendation-features
28. Headphonesty, 2026 API crackdown (T3): https://www.headphonesty.com/2026/02/spotify-crackdown-thousands-third-party-music-apps/
29. Koito repo (T1): https://github.com/gabehf/koito
30. Koito launch on r/selfhosted (T3): https://reddit.birdcat.cafe/r/selfhosted/comments/1lau6dq/introducing_koito_a_new_self_hosted_scrobbler_to
31. SelfHostYourself, Koito, Maloja, and YourSpotify (T3): https://selfhostyourself.com/services/koito ; https://selfhostyourself.com/services/maloja ; https://selfhostyourself.com/alternative-to/stats-for-spotify
32. AlternativeTo, Koito and Maloja (T3): https://alternativeto.net/software/koito/about ; https://alternativeto.net/software/maloja/about/
33. multi-scrobbler repo and index (T1/T3): https://www.github.com/FoxxMD/multi-scrobbler ; https://awesome.ecosyste.ms/api/v1/projects/github.com%2FFoxxMD%2Fmulti-scrobbler
34. Unraid multi-scrobbler thread (T3): https://forums.unraid.net/topic/99133-support-foxxmd-multi-scrobbler/
35. TechCrunch, Apple Music Replay 2025 (T2): https://techcrunch.com/2025/12/02/apple-musics-replay-2025-is-here
36. MacRumors, Replay 2025 (T2): https://www.macrumors.com/2025/12/02/apple-music-replay-2025-fully-available/
37. T3, YouTube Music Recap and user counts (T3): https://www.t3.com/tech/apps/google-beats-spotify-wrapped-this-year-with-youtube-music-recap-available-now
38. Android Central, Wrapped, Recap, and Replay (T2): https://www.androidcentral.com/apps-software/how-to-find-spotify-wrapped-youtube-music-recap-apple-music-replay
39. PopSci, Spotalike and Magic Playlist (T2): https://www.popsci.com/story/diy/create-smart-playlists-guide/
40. TechShark, Spotalike (T3): https://techshark.io/tools/spotalike/
41. PlaylistAI (T3): https://similarlabs.com/p/playlistai ; https://tribune.com.pk/story/2423018/1
42. Last.fm Pro description (T3): https://www.yorkshireeveningpost.co.uk/whats-on/arts-and-entertainment/spotify-wrapped-alternative-last-fm-scrobbling-how-to-join-how-it-works-4898115
