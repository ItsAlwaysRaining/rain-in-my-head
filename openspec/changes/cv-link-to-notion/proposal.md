# Proposal

## Why

The **Download CV** button on the Contact Me page downloads `web/public/contact/cv.pdf`, which is a placeholder that says "CV coming soon". Visitors who click it get the wrong thing. The CV lives in Notion, so the button should open that page instead.

## What Changes

- The secondary button changes from **Download CV** to **View CV**. It opens the Notion résumé page in a new tab and no longer downloads a file.
- The Notion résumé URL is set in `web/src/pages/Contact.tsx` as a constant.
- The placeholder `web/public/contact/cv.pdf` is deleted.
- The `contact-page` spec is amended: the button requirement, the download scenario, and the keyboard focus order now say "View CV" and open a new tab.
- The README sentence about replacing `web/public/contact/cv.pdf` is replaced with a pointer to the Notion page.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `contact-page`: the "Send email and Download CV" requirement changes to "Send email and View CV". The CV button opens the Notion résumé in a new tab instead of downloading a PDF. The keyboard focus scenario and the screen-reader scenario are updated to match.

## Impact

- `web/src/pages/Contact.tsx`: button label, `href`, and `target`/`rel` attributes.
- `web/public/contact/cv.pdf`: deleted.
- `openspec/specs/contact-page/spec.md`: requirement and scenarios amended on archive.
- `README.md`: CV sentence updated.
- No API, data, or infrastructure change.
- Dependency on the Notion page being shared publicly on the web. Without that, visitors hit a Notion login page. This is checked by hand before merge, not by the code.
