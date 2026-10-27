# Design

## Context

`/contact` already renders `Contact` from `web/src/pages/Placeholders.tsx`: a `PageHeader` with the right title and intro line, then a `ComingSoon` card. The shell supplies the top nav, the Home › Contact Me breadcrumbs and the page padding. `ui.tsx` has a `Button` (a `<button>` with `.primary` / `.secondary` styles) and a global `:focus-visible` outline in `theme.css`. Other pages load static SVGs from `web/public/<page>/` with plain `<img>` tags (Landing, Storm).

Figma **Contact Me · Desktop** (`362:20290`) measurements, all mapped to existing tokens:

| Part | Figma | Code |
|---|---|---|
| Title + intro | H1 Fredoka Bold 36, Body Lexend Light 16 muted, 560 wide | existing `PageHeader` |
| Body | column, gap 16 | `gap: var(--space-4)` |
| "Get in touch" | Section, Fredoka SemiBold 28 | `<h2>` (global style) |
| Row (`Contact / Social link`) | 480 wide, padding 8 0, gap 12, items centred | `width: min(480px, 100%)`, `padding: var(--space-2) 0`, `gap: var(--space-3)` |
| Icon circle | 40 × 40, `surface-raised`, radius 999, 20 px icon centred | `--surface-raised`, `border-radius: 50%` |
| Name | Label semibold, Lexend 15/600, `text` | `font-size: 0.9375rem; font-weight: 600` |
| Address | Nav & controls, Lexend 14/400, `rain` | `font-size: 0.875rem; color: var(--rain)` |
| Name ↔ address | space-between, gap 12 | `justify-content: space-between` |
| Actions | row, gap 12 | `gap: var(--space-3)` |

## Goals / Non-Goals

**Goals:**
- Match the Figma frame at desktop width with existing tokens and components.
- Keep all contact details in one constant, so swapping in the real email and LinkedIn is a one-line change.

**Non-Goals:**
- A contact form or any backend. Email goes through `mailto:`.
- Changing the shared `.primary` / `.secondary` button sizes to match the Figma Button component exactly (Figma: padding 6 × 14, 15 px, radius 8; code: 4 × 12, 14 px, radius 6). That gap exists on every page and is out of scope here.

## Decisions

**Each whole row is one link.** The name, address and icon sit inside a single `<a>`. That gives a 56 px tall click target and one tab stop per service, and the visible text ("GitHub github.com/ItsAlwaysRaining") becomes the link's accessible name. *Alternative:* only the blue address is a link, as the colour hints. Rejected because the target is smaller and the name would be read separately from the link.

**Icons are decorative (`alt=""`).** The issue asks that "each icon has an accessible label". The service name sits next to each icon inside the same link, so the link's name already labels it. Giving the `<img>` its own alt would make screen readers say "GitHub GitHub …". The spec writes this as "says which service it is … icons not announced separately".

**New-tab links say so.** External rows get `target="_blank" rel="noreferrer"`, like the issue link in `ComingSoon`, and a visually hidden " (opens in a new tab)" span. The Email row and Send email don't open a new tab.

**Buttons are links styled as buttons.** Send email (`mailto:`) and Download CV (`/contact/cv.pdf` with the `download` attribute) both navigate or download, so they are `<a>` elements. Add `ButtonLink` to `ui.tsx`, reusing the `.primary` / `.secondary` classes, plus `text-decoration: none`, inherited font and the right text colour for anchors. *Alternative:* `<Button onClick={() => location.href = …}>`. Rejected because it breaks middle-click and "copy link" and isn't a real link to assistive tech.

**Icons as files in `web/public/contact/`.** `mail.svg`, `linkedin.svg`, `github.svg` and `lastfm.svg` are downloaded unchanged from the Figma icon components (stroke `#A6AEC2` = `--text-muted`), loaded with `<img>` like Storm and Landing do. GitHub, LinkedIn and Last.fm are full 16 × 16 icons, drawn at 20 × 20 as the design does. `mail.svg` is the inner group (13.5 × 10.5) of `icon/mail`. The design places it centred in the 20 px slot at 1.25× scale, so it renders at 16.875 × 13.125.

**Contact data in one array.** `Contact.tsx` holds `EMAIL` and a `LINKS` array (`name`, `href`, `display`, `icon`, plus width and height). Email and LinkedIn hold the design's placeholders (`hello@example.com`, `linkedin.com/in/your-name`) until the owner supplies real ones.

**Placeholder CV.** A one-page PDF saying the CV is coming soon is generated once and committed at `web/public/contact/cv.pdf`, so Download CV works now. The owner replaces the file. It is a hand-written minimal PDF with no new dependency.

**"Get in touch" colour.** Figma fills it with raw white. The code uses the global `h2` colour (`--text`, `#e2e7f0`) to stay on the palette tokens.

**Narrow screens.** The rows are `width: min(480px, 100%)`. The name doesn't shrink, and the address can wrap (`overflow-wrap: anywhere`, right-aligned), so nothing is cut off or causes horizontal scroll at 390 px.

## Risks / Trade-offs

- [Placeholder email, LinkedIn and CV go live if merged as is] → The PR says so, and links issue #34 with "Refs" rather than "Closes", so the issue stays open until the owner swaps in the real values.
- [A public email address attracts spam] → The owner chooses the address. `mailto:` is the issue's requirement, and obfuscation is out of scope.
- [Merge conflict with `feature/about-page` in `Placeholders.tsx` and `App.tsx`] → The edits are small and separate (different exports and imports). Whichever PR merges second rebases.

## Open Questions

- The real email address, LinkedIn URL and CV PDF. These are values only and don't change the approach or tasks.
