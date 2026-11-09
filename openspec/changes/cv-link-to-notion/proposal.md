# Proposal

## Why

The **Download CV** button on the Contact Me page downloads `web/public/contact/cv.pdf`, which is a placeholder that says "CV coming soon". The CV lives in Notion, and the page should point visitors at the real résumé and portfolio pages with the same kind of link as the other contacts. The Send email button also duplicates the Email entry, and the email address needs to change to `August@storyandstructure.studio`.

## What Changes

- The Email entry shows `August@storyandstructure.studio` and still opens a mail message.
- **Send email** button removed. The Email entry already does this.
- **Download CV** button removed. The Notion résumé becomes a **Résumé** entry in the Contact links list, styled like the other links, with the Notion icon.
- A **Portfolio** entry is added to the same list, linking to the Notion portfolio page (`https://app.notion.com/p/3f3bd4600b7980d088a1e74e415022d3`), with the Notion icon.
- The placeholder `web/public/contact/cv.pdf` is deleted.
- A Notion icon is added at `web/public/contact/notion.svg`, drawn in the same outline style as the other icons.
- The README sentence describing the Contact page is updated.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `contact-page`: the **Contact links** requirement lists six entries (adds Résumé and Portfolio) and the new email address. The **Send email and Download CV** requirement is removed. The keyboard and screen-reader requirement drops the buttons and covers the new entries.

## Impact

- `web/src/pages/Contact.tsx`: email constant, two new entries, buttons removed, unused button import removed.
- `web/src/pages/Contact.module.css`: unused `.actions` rule removed.
- `web/public/contact/notion.svg`: new icon.
- `web/public/contact/cv.pdf`: deleted.
- `openspec/specs/contact-page/spec.md`: requirements amended on archive.
- `README.md`: Contact page sentence updated.
- No API, data, or infrastructure change.
- Dependency on the Notion pages being shared publicly on the web. Without that, visitors hit a Notion login page. This is checked by hand before merge, not by the code.
- The Notion icon is a hand-drawn outline approximation, not the official Notion mark.
