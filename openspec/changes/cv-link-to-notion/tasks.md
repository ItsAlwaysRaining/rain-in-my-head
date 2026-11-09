# Tasks

## 1. Contact page

- [x] 1.1 In `web/src/pages/Contact.tsx`, add a `CV_URL` constant set to the Notion résumé URL, and replace the Download CV `ButtonLink` with a "View CV" link to it using `target="_blank" rel="noreferrer"` and the visually hidden "(opens in a new tab)" text. Verify with `npm run build` in `web/` passing and no `download` attribute left in the file.
- [x] 1.2 Delete `web/public/contact/cv.pdf`. Verify with `ls web/public/contact/` showing no `cv.pdf`, and `grep -rn "cv.pdf" web/src` returning nothing.
- [ ] 1.3 Run `npm run dev` in `web/`, open `/contact`, and confirm the View CV button opens the Notion page in a new tab while the Contact Me page stays open. Verify by hand and note the result in the PR.

## 2. Docs and spec

- [x] 2.1 Update the README sentence about `web/public/contact/cv.pdf` so it says the CV button opens the Notion résumé and gives the constant's file. Verify with `grep -n "cv.pdf" README.md` returning nothing.
- [ ] 2.2 Archive this change with `/opsx:archive` so `openspec/specs/contact-page/spec.md` gets the amended requirements. Verify with `openspec validate contact-page` passing and `grep -n "Download CV" openspec/specs/contact-page/spec.md` returning nothing.

## 3. Integration check

- [ ] 3.1 Confirm the Notion page is shared to the web (open it in a private browser window and check it loads without a sign-in). This is the owner's step, so it is recorded in the PR, not ticked by code.
