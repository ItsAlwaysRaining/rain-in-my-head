# Proposal

## Why

Analyst is the only section guests still see locked, yet on the hosted site it can only run the pre-defined queries and never typed SQL. There's nothing to hide, so the whole page should be open to everyone. Follows #63 (PR #64).

## What Changes

- `analyst` joins the guest starting pages, so every logged-in tier opens the whole Analyst page: the pre-defined query picker, each query's SQL, and the schema map.
- Nothing about what can run changes: on the hosted site only a pre-defined query, picked by name, runs, for everyone. Typed SQL stays refused.
- Analyst is no longer locked in the top bar for guests. Visitors is the only section still locked for guests.
- Trusted now differs from guest only by Storm.

## Capabilities

### New Capabilities
- `hosted-analyst`: who opens the Analyst page on the hosted site and what it can run.

### Modified Capabilities
- `top-bar-menu`: the locked-section examples used Analyst; they now use Visitors.

## Impact

- `src/rain_in_my_head/access.py`: add `analyst` to `GUEST_PAGES`.
- `tests/test_hosted_smoke.py`: a guest can open the Analyst routes and run a pre-defined query; typed SQL is still refused.
- `README.md`: tier text.
- The per-person limit on heavy requests (spec 012) already covers pre-defined queries, so guests are limited the same way.
