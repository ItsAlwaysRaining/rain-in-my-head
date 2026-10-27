# Tasks

## 1. Assets

- [x] 1.1 Download the Figma icon assets for `icon/mail` (group in `362:20290`), `icon/linkedin` (`373:5023`), `icon/github` (`373:5027`) and `icon/lastfm` (`373:5033`) into `web/public/contact/`. Verify each file is a non-empty SVG with its root width and height intact (mail 13.5 × 10.5, the rest 16 × 16)
- [x] 1.2 Generate the one-page placeholder `web/public/contact/cv.pdf` ("CV coming soon"). Verify `file` reports a PDF and it opens in Preview

## 2. Shared button link

- [ ] 2.1 Add `ButtonLink` to `web/src/components/ui.tsx` (an `<a>` with the `.primary` / `.secondary` classes) and the anchor fixes in `ui.module.css` (no underline, inherited font, `--page` text on primary and `--text` on secondary). Verify with `npm run typecheck`

## 3. The page

- [ ] 3.1 Create `web/src/pages/Contact.tsx` and `Contact.module.css`: `PageHeader` with the existing title and intro, `h2` "Get in touch", the four rows from one `LINKS` array (whole row is an `<a>`, decorative icon in a 40 px circle, name and address with space-between, a visually hidden "(opens in a new tab)" on external rows), then the Send email (`mailto:`) and Download CV (`download`) `ButtonLink`s, using the measurements in design.md. Verify with `npm run typecheck`
- [ ] 3.2 Remove `Contact` (and the now-unused imports, if any) from `Placeholders.tsx` and import it from `pages/Contact` in `App.tsx`. Verify `npm run build` passes and `/contact` shows no "Coming soon" card or issue #34 link
- [ ] 3.3 Narrow screens: rows at `min(480px, 100%)`, address wraps rather than overflows. Verify at 390 px that every address is fully visible and `document.documentElement.scrollWidth` equals the window width

## 4. Check against the spec and design

- [ ] 4.1 At 1440 px, compare `/contact` with the Figma screenshot of `362:20290`: row width (480), icon circle (40) and icon sizes (mail 16.875 × 13.125, others 20 × 20), type sizes, gaps. Record the measured numbers in the PR
- [ ] 4.2 Check each scenario in `specs/contact-page/spec.md`: nav highlight and breadcrumbs, row order, `mailto:` and new-tab `href`/`target` values, the CV response is `application/pdf` with `download` set, Tab order with a visible outline, each link's accessible name (via the accessibility tree), and one `h1` followed by one `h2`
