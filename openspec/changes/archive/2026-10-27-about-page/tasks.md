# Tasks

## 1. Asset

- [x] 1.1 Download the Figma `icon/image` vector from the **About · Desktop** design context into `web/public/about/image.svg`. Verify the file is a non-empty SVG with its root width and height intact

## 2. The page

- [x] 2.1 Create `web/src/pages/About.tsx` and `About.module.css`: `PageHeader` "About", then the body row with the photo frame and the text column (`h2` About Me + two paragraphs, `h2` About This App + one paragraph) using the copy and measurements in design.md. Verify with `npm run typecheck`
- [x] 2.2 Photo frame: `<img src="/about/photo.jpg">` with alt text and `object-fit: cover`; on load error, the dashed placeholder with the 24 px image icon, `aria-hidden`. Verify in the browser that with no photo file there is no broken-image icon and the frame matches the Figma frame (420 × 480, dashed border, centred icon)
- [x] 2.3 Below 900 px, stack the photo above the text at `min(420px, 100%)` wide with the same aspect ratio. Verify at 390 px that the photo is above About Me and `document.documentElement.scrollWidth` equals the window width
- [x] 2.4 Remove `About` from `Placeholders.tsx` and import it from `pages/About` in `App.tsx`. Verify `/about` shows no "Coming soon" card or issue link, `npm run build` passes, and clicking About in the top nav highlights it with breadcrumbs Home › About

## 3. Check against the design

- [x] 3.1 At 1440 px, compare `/about` with the Figma screenshot of `262:1334`: title, photo position and size, heading and body type, gaps. Record measured sizes (photo box, heading font size, text column max width) in the PR
- [x] 3.2 Check the heading outline (one `h1`, then two `h2`s in order) and that each spec scenario in `specs/about-page/spec.md` holds
