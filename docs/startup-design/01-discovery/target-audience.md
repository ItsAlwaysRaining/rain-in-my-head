# Target Audience: Rain in My Head

Created: 2026-11-18
Last updated: 2026-11-18

**Phase:** 3 · **Confidence:** Medium (secondary research only; interviews deferred) · Quotes: [raw/wave3-4-customers-distribution.md](raw/wave3-4-customers-distribution.md)

## Personas
Updated 2026-11-18: the owner set the analyst as the primary user. The earlier Self-Hoster persona is folded into it.

**1. The Data-Owning Analyst (primary user).** Works with data for a living and wants the same control over their own music history. Comfortable in a terminal, uses git, and clones open-source projects to run locally. Often active in r/selfhosted, r/lastfm, or r/dataisbeautiful, and may already run Maloja, Koito, or YourSpotify. Wants their history in SQLite, SQL access, and rules they can read, not a black box. Reads the README before the UI.

**2. The Long-Time Listener (secondary).** In their late 20s to 40s, with 10+ years of Spotify or Last.fm history. Feels "stuck in a loop" and misses old favorites. Won't touch a terminal, so they get playlists only when an analyst friend or partner runs the tool for them. Design the output for them; design the setup for the analyst.

Note: most of the pain research below comes from listener forums. The analyst's pains are inferred, not yet confirmed by interviews (see Experiment 1).

## Pain hierarchy (ranked by frequency in the research)
1. **Stuck in a loop:** DJ, Daily Mix, and Discover Weekly repeat the same songs (2023–2026). [Data]
2. **Discover Weekly getting worse:** it brings back songs people already heard or skipped. [Data]
3. **AI-generated songs** breaking trust (60+ page forum thread). [Data]
4. **Long-term taste ignored:** old favorites forgotten. [Data]
5. **No "why":** fear of paid placement (November 2025 class action). [Data]
6. **Data ownership:** a weaker pain, but a motivator for Last.fm users. [Data]

## Jobs to be done
- (Primary) "Let me **own and query** my listening data on my own machine."
- "When my playlists feel stale, help me **rediscover music I already loved** so listening feels like mine again."
- "When I get a recommendation, **tell me why** so I can check the logic."
- "When I'm nostalgic for a time in my life, **take me back to that era's music**."

## Language map (words users actually use)
"stuck in a loop", "same 20 songs", "AI slop", "forgotten about", "time machine", "scrobbles", "Wrapped all year round", "broken my trust"

## Top quotes
- "This has completely broken my trust because I used to feel like Spotify recommendations were made for me."
- "[The DJ] seems to think that I only want to listen to maybe 20 songs."
- A third-party shuffler let them hear "songs I had completely forgotten about."

(Verify each quote at its link before using it in the case study.)

## Biggest barrier
Setup: Spotify Premium, plus your own Spotify developer app, plus a Last.fm API key.
- **Real product:** runs locally, and Claude walks the user through each step. This lowers the barrier a lot.
- **Portfolio:** a hosted web app with a guided setup flow, designed as a case-study centerpiece. It isn't the expected way to use the product.

## Red flags / yellow flags
- 🟡 Every finding is secondary. Interviews are deferred and are validation experiment #1.
- 🟡 The two personas pull in different directions. Default to the Long-Time Listener for the UI, and put the power features behind it.
