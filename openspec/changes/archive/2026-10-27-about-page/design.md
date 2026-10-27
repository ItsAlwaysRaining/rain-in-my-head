# Design

## Context

`/about` renders `About` from `web/src/pages/Placeholders.tsx`, a `PageHeader` plus a `ComingSoon` card. The top nav (`SECTIONS` in `routes.ts`) and breadcrumbs already handle `/about`. Pages are React components with CSS modules and the tokens in `theme.css`. `web/` has no unit-test runner; checks are `npm run typecheck`, `npm run build` and the page in a browser.

Figma, **About · Desktop** (`262:1334`), inside the page content area:

| Element | Figma | Code |
|---|---|---|
| Title "About" | H1, Fredoka Bold 36 | existing `PageHeader` |
| Body row | gap 48, align top | flex row, `gap: var(--space-7)` |
| Photo frame | 420 × 480, `--radius`, surface-raised fill, 1.5 px dashed `--line` border | `<figure>`-free `div` with `aspect-ratio: 420 / 480` |
| Text column | fills the rest; children 48 apart | flex column, `gap: var(--space-7)` |
| Section headings | Section style: Fredoka SemiBold 28 / 1.25, white | `<h2>`, `var(--display)`, 600, 28px, `var(--text)` |
| Body text | Body: Lexend Light 16 / 1.7, `--text`, max 720, paragraphs 16 apart | `<p>`, `max-width: 720px`, `gap: var(--space-4)` |

## Goals / Non-Goals

**Goals:** match the frame at desktop width; stack cleanly on phones; ship final copy.

**Non-Goals:** a mobile Figma frame (none exists, so the narrow layout follows the issue: photo above text); links to contact channels (the Contact Me page, #34, covers those); editing the copy from data or a CMS.

## Decisions

1. **Own file, not `Placeholders.tsx`.** `About.tsx` + `About.module.css`, like the Landing and Storm pages when they left the placeholder file. `ComingSoon` stays for the other placeholders.
2. **Copy in the component.** It's static, short and only on this page; a separate content file would add indirection for no gain.
3. **Headings use the existing tokens.** Section headings use `--display` and `--text` rather than the design's pure white; `--text` (#e2e7f0) is the project's text colour and the difference is not visible on `--page`. The title reuses `PageHeader`, so it matches every other page.
4. **Photo with a fallback, not a hard dependency.** The page renders `<img src="/about/photo.jpg" alt="…">` with `object-fit: cover` in the frame. If it fails to load (`onError`), the component swaps in the dashed placeholder: the Figma `icon/image` SVG at 24 px, centred, with the frame marked `aria-hidden`. The design's hint text ("Photo of me · 420 × 480") is a design-file note, so it isn't shown on the live site. *Alternative*: wait for the photo before building. Rejected so the page can ship and the photo can follow as a one-file commit.
5. **Icon from Figma.** Download the `icon/image` vector from the design context into `web/public/about/image.svg` and reference it by path, unchanged.
6. **Breakpoint 900 px.** Below it the row becomes a column and the frame becomes `width: min(420px, 100%)`, keeping its aspect ratio. 900 px is already used by other pages, and at that width the text column beside a 420 px photo would drop under about 380 px.

### Draft copy

Drawn from the Figma **1 · Research** page (problem statement, North Star, persona, questions, user stories). Wording is open to the owner's edits before apply.

**About Me**


> I'm a big nerd. In 2011 I started "scrobbling" all of my music listening data to Last.fm (So, I've always been like this). Streaming services were just starting to become popular and I started using Spotify but I really missed some of the "Smart Playlist" features Windows Media Player had. Those features never made it back into music players.
>
> I accepted this as a trade-off but eventually I became a data engineer and managed to carve out a little time for a personal project. This has been an experiment for me in many ways. I wanted to learn more about UI/UX (current obsession - every page here has a wireframe and clickable prototype in Figma), Web Dev and web hosting applications, AI (Vibe coding - I'm not a front end developer, spec driven design, and integrating AI into a web app - in progress). Now I get to see my own data, make custom playlists, and play with generating my own AI playlists (though the data is pretty limited - for now).
 
**About This App**

> Rain in My Head turns my Last.fm listening history into dashboards I can explore and playlists I can save to Spotify. Its North Star is simple: control over my own data, so I can run my own analytics. It answers questions like what I've been listening to lately, which artists are new to me, and what I played the summer three years ago, and it builds playlists for times of day or seasons of my life. It builds playlists for me based on my listening history because Friday from 5 pm to 7 pm has its own feeling.

Alt text: "Photo of the author of Rain in My Head" until the owner supplies a description of the real photo.

## Risks / Trade-offs

- [The photo isn't in the repo yet] → The placeholder frame keeps the layout right; adding `web/public/about/photo.jpg` (and updating the alt text) is a follow-up commit the owner makes.
- [Copy states personal facts drawn from design notes] → The draft is in this file for review; the owner corrects it before or during apply.
- [48 px between each heading and its text, as in Figma, is loose] → Kept to match the design; flagged in the PR so the owner can decide.
