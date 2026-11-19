# Rain in My Head: Startup Design Summary

Created: 2026-11-18
Last updated: 2026-11-18

## Overview
Rain in My Head is a free, open-source, self-hosted **personal playlist engine**. It reads your whole Last.fm listening history, finds forgotten favorites and past eras, and writes Spotify playlists that explain why every song is there. It's a UX portfolio piece, designed as if for everyone and shared on GitHub for anyone to fork. It's not hosted for the public.

## Key research findings
- The pain is real: "stuck in a loop," AI songs, and forgotten favorites (forum complaints from 2023 to 2026).
- Spotify's Prompted Playlist already explains its picks, but with generic notes, using only Spotify history, on Spotify's servers.
- ListenBrainz is the closest open alternative, but it has no visible reasoning and a technical interface.
- Spotify development mode allows 5 users per app and requires Premium, so self-hosting is the only model.

## Positioning
For long-time listeners who feel stuck in an algorithm's loop, Rain in My Head is a personal playlist engine that builds Spotify playlists from your whole listening history and tells you why every song is there. Unlike Spotify's AI playlists, it uses only music you've actually loved, and your data never leaves your hands.

## Top 3 risks
1. **Setup is too hard for non-technical users.** Mitigation: the real product runs locally, and a Claude-assisted setup guide walks the user through each step. The hosted web app's guided setup is a portfolio piece only.
2. **The reasons aren't better than Spotify's.** Mitigation: the paper test (Experiment 2) before building.
3. **Spotify API restrictions.** Mitigation: M3U and JSPF export.

## What we know vs. what we're guessing
- **Known:** API constraints, that the pain exists, and the competitor landscape.
- **Guessing:** audience size, whether the reasons feel better than Spotify's, and whether people can finish setup.

## Scorecard
6.1/10: conditional proceed. The real product runs locally, with Claude-assisted setup; the hosted web app is a portfolio piece only. Future: imports from other listening apps with free APIs. A clear yes as a portfolio piece. See [06-validation/scorecard.md](06-validation/scorecard.md).

## Anti-patterns detected
- **Boiling the ocean (much reduced):** most of the four variations already exist in the repo and only need renaming. See [existing features](04-product/existing-features.md). Only three small additions are new.
- **Building in stealth:** zero interviews so far. Run Experiment 1 first.

## Documents
- Intake: [preflight](00-intake/preflight.md) · [brief](00-intake/brief.md) · [brainstorm](00-intake/brainstorm.md)
- Discovery: [market](01-discovery/market-analysis.md) · [competitors](01-discovery/competitor-landscape.md) · [audience](01-discovery/target-audience.md) · [trends](01-discovery/industry-trends.md) · [confidence](01-discovery/confidence-dashboard.md) · [gate](01-discovery/research-gate.md) · [raw/](01-discovery/raw/)
- Strategy: [lean canvas](02-strategy/lean-canvas.md) · [value prop](02-strategy/value-proposition.md) · [business model](02-strategy/business-model.md) · [positioning](02-strategy/positioning.md) · [go-to-market](02-strategy/go-to-market.md)
- Brand: [mission, vision, and values](03-brand/mission-vision-values.md) · [tone](03-brand/tone-of-voice.md) · [personality](03-brand/brand-personality.md)
- Product: [existing features](04-product/existing-features.md) · [MVP](04-product/mvp-definition.md) · [prioritization](04-product/feature-prioritization.md) · [journey](04-product/user-journey.md)
- Validation: [playbook](06-validation/validation-playbook.md) · [risks](06-validation/risk-analysis.md) · [assumptions](06-validation/assumptions-tracker.md) · [experiments](06-validation/experiment-design.md) · [kill criteria](06-validation/kill-criteria.md) · [scorecard](06-validation/scorecard.md)
- [30-day action plan](action-plan-30-days.md) · [PROGRESS](PROGRESS.md)
