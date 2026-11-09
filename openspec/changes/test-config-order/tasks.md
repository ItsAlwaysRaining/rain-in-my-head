# Tasks

## 1. Smoke test sets hosted mode with fixtures

- [ ] 1.1 In `tests/test_hosted_smoke.py`, remove the `os.environ` assignments made at import. Add an autouse fixture that patches `config.HOSTED` to True, `config.DB_PATH` to `PUBLIC_DB`, `config.DATABASE_URL` to `""` and `config.SESSION_SECRET` to the throwaway test value, using monkeypatch. Verify: `uv run pytest tests/test_hosted_smoke.py -q` passes all 14 tests.
- [ ] 1.2 Keep the `assert config.HOSTED` guard and update its comment to say the fixture sets the mode. Verify: the guard passes, and a temporary edit that removes the fixture makes the guard fail (revert after checking).

## 2. Artist API test sets Mac mode explicitly

- [ ] 2.1 In `tests/test_artist.py`, in `test_api_artist_serialises_first_played_monthly_and_month`, patch `config.HOSTED` to False with monkeypatch next to the existing `DB_PATH` patch. Verify: `uv run pytest tests/test_artist.py -q` passes 11 tests.

## 3. Order-independence checks

- [ ] 3.1 Run the whole suite in the normal order: `uv run --no-default-groups --group web --with pytest --with httpx pytest tests -q`. Verify: all pass (21 existing plus any new).
- [ ] 3.2 Run the two files in the opposite order: `pytest tests/test_hosted_smoke.py tests/test_artist.py -q` and `pytest tests/test_artist.py tests/test_hosted_smoke.py -q`. Verify: both pass.
- [ ] 3.3 Run the security lint as CI does: `uvx ruff@0.17.3 check src api tests`. Verify: "All checks passed!".
