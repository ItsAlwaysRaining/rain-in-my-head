# Design

## Context

The Contact Me page (`web/src/pages/Contact.tsx`) renders the secondary button as `ButtonLink` with `href="/contact/cv.pdf"` and the `download` attribute. The external links in the same file already use `target="_blank" rel="noreferrer"` with a visually hidden "(opens in a new tab)" note. See proposal.md - Why for the motivation, and specs/contact-page/spec.md for the required behaviour.

## Goals / Non-Goals

**Goals:**
- The button opens the Notion résumé in a new tab, with the same accessible pattern as the other external links on the page.
- The URL lives in one constant so a future change is a one-line edit.

**Non-Goals:**
- No PDF hosting. The Notion page is the source of truth for the CV.
- No change to the Send email button or the contact list.
- No change to how the Notion page is shared. That is done in Notion by the owner.

## Decisions

- **Link to Notion, not a PDF in the repo.** The CV is maintained in Notion, so a copy in `web/public` would drift. Alternative considered: export a PDF from Notion and keep the download. Rejected because it adds a manual step on every CV change.
- **Label "View CV", not "Download CV".** Nothing is downloaded any more. Alternative: keep the label and rely on the new tab. Rejected because the label would promise a file.
- **Reuse `ButtonLink`, add `target="_blank" rel="noreferrer"` and the same hidden "(opens in a new tab)" text used for the other external links.** Keeps the screen-reader behaviour in the spec. Alternative: a new component. Rejected because the existing one covers it.
- **Delete `web/public/contact/cv.pdf`.** Nothing links to it after the change, and the placeholder would otherwise stay live at `/contact/cv.pdf`.

## Risks / Trade-offs

- [Notion page is private] → visitors see a Notion sign-in page. Mitigation: the owner shares the page to the web before the PR is merged, and checks it in a private browser window. The code cannot check this.
- [Notion URL changes] → the link breaks. Mitigation: the URL is a single constant in `Contact.tsx`, and the spec names it.
- [The CV is public with the owner's email] → Mitigation: the owner confirms before merge. Same contact details are already public on the page.

## Migration Plan

Single PR. Deploy follows the normal flow (preview, then production on merge). Rollback: revert the PR, which restores the old button and PDF.

## Open Questions

None.
