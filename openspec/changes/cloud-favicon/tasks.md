# Tasks

## 1. The icon

- [ ] 1.1 Create `web/public/favicon.svg`: a two-tone cloud (fill `#5CC8F0`, outline `#141A2A`) on a 32×32 viewBox, as in design.md. Verify by rendering it at 16px and 32px on white and on `#202124` (for example, a scratch HTML page in headless Chrome) and checking the cloud reads clearly on all four
- [ ] 1.2 Check the contrast pairs from the spec: outline vs. white ≥ 3:1 and fill vs. `#202124` ≥ 3:1, computed with the WCAG formula; record the ratios in the PR

## 2. Both dashboards

- [ ] 2.1 Link the icon in `web/index.html` (`<link rel="icon" type="image/svg+xml" href="/favicon.svg">`). Verify that `npm run build` puts `favicon.svg` in `web/dist/`, and that `curl -I localhost:8000/favicon.svg` and the Vite dev server both return `image/svg+xml`
- [ ] 2.2 Set `page_icon` in `dashboard/app.py` to the absolute path of `web/public/favicon.svg`, resolved from `__file__`. Verify that the Streamlit page's `<link rel="icon">` is a `data:image/svg+xml` URL that decodes to the same file
- [ ] 2.3 Open every page of both dashboards in Chrome and confirm the tab shows the cloud (spec: "Cloud icon in the browser tab")

## 3. Wrap-up

- [ ] 3.1 Note in the README's "Two dashboards" section that the tab icon is `web/public/favicon.svg`, shared by both apps. Verify the README renders the path correctly
