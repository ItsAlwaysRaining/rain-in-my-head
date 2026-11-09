# Design

## Context

`src/rain_in_my_head/config.py` computes `HOSTED`, `DB_PATH`, `DATABASE_URL` and `SESSION_SECRET` from the environment when it is first imported. Every test module that imports app code shares that one module object for the whole pytest run. See proposal.md for the failure.

Checked in the code:
- The app reads `config.HOSTED`, `config.DB_PATH`, `config.DATABASE_URL` and `config.SESSION_SECRET` inside functions and routes, on each request (`src/rain_in_my_head/api.py`, `src/rain_in_my_head/viewers.py` line 52). Patching them on the `config` module therefore takes effect on the next request.
- The one exception is `api.py` line 50, where `HOSTED` sets `docs_url` and `openapi_url` when the app object is built. No test checks those URLs, so this doesn't matter here.
- `api/index.py` does `os.environ.setdefault("LISTENING_DB", ...)` at import. That only fills in a value that isn't already set, and the smoke test patches `DB_PATH` itself, so it doesn't affect the test.

## Goals / Non-Goals

**Goals:**
- Each test module's mode is set inside the module (by fixture), not by whichever module loaded first.
- The suite gives the same result in any file order.

**Non-Goals:**
- Changing `config.py` or any application code.
- Splitting the smoke test into a separate process or a separate CI step.
- Testing the docs URLs.

## Decisions

**1. Patch `config` with monkeypatch in the smoke test, instead of setting environment variables at import.** The smoke test gets an autouse fixture that sets `HOSTED = True`, `DB_PATH = PUBLIC_DB`, `DATABASE_URL = ""` and `SESSION_SECRET` for the test, and undoes them afterwards. This sets hosted mode where the app reads it, and leaves no state behind for other modules. *Alternative:* a `conftest.py` that sets hosted mode for the whole run. Rejected, since it would make every other test run hosted. *Alternative:* a subprocess per smoke test. Rejected for now as more code than needed. The owner picked the fixture approach.

**2. `tests/test_artist.py` sets Mac mode in the API test.** The test already patches `config.DB_PATH`. It also sets `HOSTED = False` with monkeypatch, so it doesn't depend on what loaded first. The other tests in that file call `artist_page` directly and don't read `HOSTED`, so they are unchanged.

**3. Keep the smoke test's guard.** The `assert config.HOSTED` line stays. It now checks the fixture's patch, which means a broken fixture still fails loudly.

## Risks / Trade-offs

- **A new test module reads `config` at import without patching it** → the same order problem can come back. Mitigation: the rule goes in the test module docstring and in the smoke test's comment.
- **`docs_url` depends on import order** → not tested, so no effect today. Mitigation: noted here; fix separately if docs routes ever get a test.
- **Patching leaks if a fixture is missing its undo** → monkeypatch restores values automatically at teardown, so this is covered.

## Migration Plan

No data or deploy change. The fix goes in one PR. Rollback is reverting the PR.

## Open Questions

None.
