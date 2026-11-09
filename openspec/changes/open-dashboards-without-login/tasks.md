# Tasks

## 1. Server: anonymous visitors get the guest pages

- [ ] 1.1 In `access_guard` (src/rain_in_my_head/api.py), treat a request with no session as the guest page set (`access.TIER_PAGES["guest"]`) instead of returning `login_required`; verify with a test that an anonymous `GET /api/overview` on the hosted site returns 200
- [ ] 1.2 Make `/api/me` return the guest pages with `logged_in: false` for anonymous visitors; verify with a test that the response lists "overview" and does not list "visitors"

## 2. Server: refusals stay

- [ ] 2.1 Verify with tests that, anonymously on the hosted site, `POST` to a playlist creation route is refused with the playlist refusal message, `/api/ai` routes are refused, typed SQL is refused, and each of the six pre-defined queries runs
- [ ] 2.2 Verify with a test that anonymous `POST /api/events` is refused and stores nothing

## 3. Web: anonymous visitors open the guest pages

- [ ] 3.1 In `RequireAccess` (web/src/auth.tsx), redirect to login only when the visitor is anonymous and the page is not in their list; verify with `npm run typecheck` and `npm run build` in `web/`
- [ ] 3.2 Check the client ignores a refused `/api/events` call for anonymous visitors (no error shown); verify in the preview build

## 4. Verification

- [ ] 4.1 Run the new tests with `uv run --with pytest --with httpx pytest` (skipping tests/test_hosted_smoke.py, which needs data/public.db)
- [ ] 4.2 Run `npm run build` in `web/` and `ruff` on changed Python files
- [ ] 4.3 On the Vercel preview, signed out: open each guest page, check the Visitors page redirects to login, check the playlist refusal message and the AI page
