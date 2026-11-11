## Why

Clicking the lightning bolt on the landing page takes a logged-out visitor to the login page, because Storm is a trusted-only page. The bolt should always open Storm. Logging in needs its own way in: the top bar has Log out but no Log in.

## What Changes

- **Storm opens for everyone:** add `storm` to the guest pages, so the bolt opens Storm with or without a login. Storm loads no data, so this exposes nothing.
- **Log in in the top bar:** a logged-out visitor on the hosted site sees a "Log in" link at the end of the top bar (and the Mobile menu), where Log out sits when logged in. It goes to `/login`. It is not shown on the owner's Mac, where there is no login.

## Capabilities

### New Capabilities

- `storm-page`: who may open Storm.

### Modified Capabilities

- `top-bar-menu`: adds the Log in link.

## Impact

- `src/rain_in_my_head/access.py` (guest pages), `tests/test_mainstream.py` (used `storm` as a non-guest page).
- `web/src/App.tsx` (Log in link).
- No data, schema or hosting changes.
