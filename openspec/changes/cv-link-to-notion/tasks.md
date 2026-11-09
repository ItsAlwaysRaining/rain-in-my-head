# Tasks

## 1. Contact page

- [x] 1.1 In `web/src/pages/Contact.tsx`, add a `CV_URL` constant set to the Notion résumé URL, and replace the Download CV `ButtonLink` with a "View CV" link to it using `target="_blank" rel="noreferrer"` and the visually hidden "(opens in a new tab)" text. Verify with `npm run build` in `web/` passing and no `download` attribute left in the file.
- [x] 1.2 Delete `web/public/contact/cv.pdf`. Verify with `ls web/public/contact/` showing no `cv.pdf`, and `grep -rn "cv.pdf" web/src` returning nothing.
- [ ] 1.3 Run `npm run dev` in `web/`, open `/contact`, and confirm the Résumé and Portfolio entries open the Notion pages in new tabs while the Contact Me page stays open. Verify by hand and note the result in the PR.

## 2. Docs and spec

- [x] 2.1 Update the README sentence about `web/public/contact/cv.pdf` so it says the CV button opens the Notion résumé and gives the constant's file. Verify with `grep -n "cv.pdf" README.md` returning nothing.
- [ ] 2.2 Archive this change with `/opsx:archive` so `openspec/specs/contact-page/spec.md` gets the amended requirements. Verify with `openspec validate contact-page` passing and `grep -n "Download CV\|Send email" openspec/specs/contact-page/spec.md` returning nothing.

## 3. Email, buttons and list entries

- [x] 3.1 In `web/src/pages/Contact.tsx`, set the email constant to `August@storyandstructure.studio`, remove the Send email and View CV buttons and the unused `ButtonLink` import, and remove the `.actions` rule from `Contact.module.css`. Verify with `npm run build` passing and `grep -n "Send email\|aowheeler\|ButtonLink\|actions" web/src/pages/Contact.tsx` returning nothing.
- [x] 3.2 Add Résumé (`CV_URL`) and Portfolio (`https://app.notion.com/p/3f3bd4600b7980d088a1e74e415022d3`) entries to the Contact links list, with the Notion icon at `web/public/contact/notion.svg`. Verify with `npm run build` passing and `ls web/public/contact/notion.svg` existing.
- [ ] 3.3 Check the Notion icon in the browser beside the other icons (same circle, same size and colour). Verify by hand, as part of 1.3.

## 4. Integration check

- [ ] 4.1 Confirm the Notion pages are shared to the web (open each in a private browser window and check it loads without a sign-in). This is the owner's step, so it is recorded in the PR, not ticked by code.
