# User Journey: Rain in My Head

Created: 2026-11-18
Last updated: 2026-11-18

**Phase:** 6 · **Persona:** Data-Owning Analyst (primary, updated 2026-11-18). The Long-Time Listener only sees stages 5 to 7, when an analyst runs it for them.

| Stage | Touchpoint | They think or feel | Drop-off risk |
|---|---|---|---|
| 1. Discover | GitHub, r/selfhosted, or r/lastfm post | "My data, local, in SQLite? Let's look." 🙂 | README doesn't show a result in the first screen |
| 2. Setup: clone and Last.fm | `git clone`, then add the Last.fm API key to `.env` | "OK, a key, easy." 🙂 | Can't find the API key page; unclear `.env` steps |
| 3. Setup: Spotify app | Spotify dashboard, redirect URI, add yourself as a user | "Fine, but why is this so fiddly?" 😟 | **Highest risk.** Premium requirement, confusing Spotify dashboard |
| 4. History loads | Progress bar (a backfill can take hours) | "Is it working?" 😐 | Closes the tab |
| 5. First playlist | Forgotten favorites preview | "Oh wow, I forgot this song!" 😍 | Reasons feel generic |
| 6. Send to Spotify | One button → opens Spotify | "It's really there." 🙂 | Spotify error 403 |
| 7. Return | Time-machine, rules | "Let's do 2016." 🙂 | No reminder to come back |

## Aha moment
**Stage 5:** seeing a forgotten song with a reason like "You played this 140 times in spring 2014 and never since," backed by a query the analyst can open. Target: from `git clone` to this moment in under 15 minutes.

## Design so the aha comes before the pain
Show a forgotten favorites preview using **Last.fm only** (stage 2) **before** asking for the Spotify setup (stage 3). The user feels the value first, then puts up with the hard step.

## Two versions of setup
- **Real product (local):** the user clones the repo and asks Claude to "set up Rain in My Head." Claude follows the repo's setup guide, explains each Spotify and Last.fm step in plain words, and fills in the `.env` file. This is where the real value is.
- **Portfolio version (hosted web app):** the full guided setup flow above. It's designed to show how to handle a hard setup; it isn't how people are expected to use the product.

## Biggest drop-off risks
1. Spotify developer app setup.
2. Waiting for history to backfill.
3. Generic reasons.
