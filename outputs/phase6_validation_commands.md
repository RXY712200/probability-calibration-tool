# Phase 6 validation commands

Working directory:

```text
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability
```

## Baseline before edits

```text
uv run pytest
```

872 passed in 71.10s. No failed, skipped, xfailed or xpassed tests.

## Final full suite

```text
uv run pytest
```

952 passed in 54.69s. Failed: 0; skipped: 0; xfailed: 0; xpassed: 0.

## Phase 6 explicit collection and execution

```text
uv run pytest tests/integration/desktop --collect-only -q
uv run pytest tests/integration/desktop -q
```

80 collected; 80 passed in 13.14s.

## Focused integration coverage

```text
uv run pytest tests/integration/desktop/test_restore_session_rebuild.py tests/integration/desktop/test_recent_integration.py tests/integration/desktop/test_correction_integration.py tests/integration/desktop/test_startup_routing.py tests/integration/desktop/test_end_to_end.py -q
```

43 passed in 13.07s.

Additional literal focused commands executed while developing the suite:

```text
uv run pytest tests/integration/desktop/test_end_to_end.py -q
uv run pytest tests/integration/desktop/test_correction_integration.py tests/integration/desktop/test_backup_catalog.py -q
uv run pytest tests/integration/desktop/test_restore_session_rebuild.py -q
uv run pytest tests/integration/desktop/test_error_boundary.py -q
uv run pytest tests/integration/desktop/test_bootstrap.py tests/integration/desktop/test_end_to_end.py -q
```

Results at execution time respectively: 1, 15, 14, 25 and 7 passed. The suite subsequently grew to the final 80 tests; these incremental counts are not additional tests.

## Independent accepted-baseline regressions

```text
uv run pytest tests/unit/core -q
```

213 passed in 0.74s.

```text
uv run pytest tests/integration/persistence --ignore=tests/integration/persistence/test_migrations_phase4.py -q
```

293 passed in 9.99s.

```text
uv run pytest tests/integration/application --ignore=tests/integration/application/reliability --ignore=tests/integration/application/test_presentation_capabilities.py -q
```

153 passed in 15.00s.

```text
uv run pytest tests/integration/application/reliability tests/integration/infrastructure tests/integration/persistence/test_migrations_phase4.py -q
```

107 passed in 7.09s.

```text
uv run pytest tests/ui tests/integration/application/test_presentation_capabilities.py -q
```

106 passed in 9.23s.

The --ignore arguments only isolate the original phase counts; the omitted later-phase groups were run separately and are included in the unfiltered full suite.

## Unpackaged module import

```text
uv run --directory src python -c "import probability_calibration_tool.bootstrap; print('Unpackaged module import OK')"
```

Unpackaged module import OK.

An automated subprocess also executes the actual __main__ module, real bootstrap, event loop, StartupService and shutdown with temporary LOCALAPPDATA. It uses a zero-delay Qt quit event, not an arbitrary performance threshold.

## Final Ruff

```text
uv run ruff check .
uv run ruff format --check .
```

All checks passed! / 171 files already formatted (final rerun after report creation).

Initial Ruff runs found import/formatting, sorted-slots, missing explicit subprocess.check and broad-boundary-catch annotations in new files; these were fixed. No accepted tests or lint rules were weakened.

## Scope/hash audit

Only one accepted file changed: the RoundRepository gained a narrow eager read-only candidate query.
All 59 accepted test/helper Python files were hash-identical to the pre-edit baseline.
No existing source/test files were deleted.

SPEC SHA-256: AEE4EB200BEA8EC1A652A65A2076645613E6057C37D6280A9A0787CC5B040FC4
Schema SHA-256: FB457C818780A94EF62AB53A3ED02FC0779FF1C4B0001734FBD67D56486F9315

No changes to accepted Core, Domain, Workflow/services, Phase 4 reliability, original Phase 5 UI, pyproject.toml, uv.lock or .gitignore.

## Not performed

Windows 125%/150% manual DPI, PyInstaller/installer work, packaged-app tests and 100k performance release smoke. No Phase 7 implementation started.
