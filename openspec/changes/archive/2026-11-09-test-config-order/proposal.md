# Proposal: each test module sets its own mode

Created 2026-11-09 · Last updated 2026-11-09

## Why

The test suite fails depending on file order. `config.py` reads `LISTENING_HOSTED`, `LISTENING_DB`, `DATABASE_URL` and `SESSION_SECRET` once, at first import. `tests/test_hosted_smoke.py` sets them at import time, so it only works if no other module has imported the app first. `tests/test_artist.py` imports `rain_in_my_head.artist`, which imports `config`, so with the normal alphabetical order the smoke test fails (14 tests). Run the other way round, the artist API test runs in hosted mode and gets refused. This is already failing on `origin/main` (reproduced at 588d1c0), so CI on `main` is red.

## What Changes

- The smoke test sets hosted mode through pytest fixtures that patch `config` (`HOSTED`, `DB_PATH`, and any other setting the app reads per request), instead of environment variables at import.
- `tests/test_artist.py` sets Mac mode explicitly in the test that calls the API, so it no longer depends on what loaded first.
- No application code changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. The `ci-checks` spec requires the smoke test to run the API in hosted mode, and it still does. The spec doesn't say how that mode is set, so no requirement changes. `skip_specs: true` is set in `.openspec.yaml`.

## Impact

- **Tests**: `tests/test_hosted_smoke.py`, `tests/test_artist.py`.
- **Application**: none.
- **CI**: the smoke test result on `main` turns green again. CI command unchanged.
- **Risk**: if the app reads a setting once at import (not per request), a patched value would not take effect. Checked in design.md.
