## 1. API

- [ ] 1.1 Add `preset` to `/api/genre` and `_genre_view`; resolve with `overview.resolve_range`; dates without preset = custom, nothing = all
- [ ] 1.2 Return `range` (same shape as the Overview's) and `share: {color_index, points}` built from `overview.genre_shares`
- [ ] 1.3 Add `tests/test_genre.py`: preset resolution, old date-only links, share values sum check, `color_index` null outside top 6
- [ ] 1.4 Update `Genre` / `GenreParams` types in `web/src/api.ts`

## 2. Range chips

- [ ] 2.1 Move the Overview's chips + Custom popup into `components/RangePicker.tsx` (+ CSS); Overview uses it with no visible change
- [ ] 2.2 Use `RangePicker` on `Genre.tsx`; changing the range keeps `genre` and drops the selected artist
- [ ] 2.3 Overview genre links pass `preset` (or `preset=custom&start&end` when a period or Custom is active)

## 3. Share chart

- [ ] 3.1 Add `web/src/charts/genre.ts`: area + line in the genre's colour, peak label, percent axis
- [ ] 3.2 Render it on `Genre.tsx` under the header as a card titled "Share of tagged plays"

## 4. Check

- [ ] 4.1 Compare with Figma 263:2051 (chip row, chart card, peak label) and fix gaps
- [ ] 4.2 `npm run build`/lint and scoped pytest; full regression once before the PR
- [ ] 4.3 In the browser: each chip, Custom Apply, Overview → Genre link keeps the chip, Indie shows Moss
