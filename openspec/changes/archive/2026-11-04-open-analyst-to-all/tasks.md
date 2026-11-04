## 1. Access

- [x] 1.1 In `access.py`, add `analyst` to `GUEST_PAGES` and update the comments that call Analyst a trusted page
- [x] 1.2 In `tests/test_hosted_smoke.py`, replace the "guest cannot open Analyst" test with: a guest gets 200 on `/api/sql/meta` and `/api/schema`, runs a listed query, and gets 403 `refused` for typed SQL; a logged-out request gets 403 `login_required`
- [x] 1.3 Run `uv run --with pytest --with httpx pytest tests` and confirm it passes

## 2. Page and docs

- [x] 2.1 Check the top bar and the Analyst page as a guest in a real browser: Analyst has no lock, the picker and schema map load, a listed query runs, and Visitors is the only locked section
- [x] 2.2 Update the README tier text (`--tier trusted` now opens Storm only; a guest opens Analyst)

## 3. Finish

- [x] 3.1 Run `/opsx:archive` and push; the change rides on PR #64
