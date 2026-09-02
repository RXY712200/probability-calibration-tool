# Localization Step 7 Valid-History Fixture Rework Validation

Status: `STEP 7 VALID-HISTORY FIXTURE REWORK COMPLETE — READY FOR EXTERNAL REVIEW`

All commands ran from the project root. No command performs human visual acceptance.

## Canonical readiness evidence

```powershell
uv run pytest tests/unit/core/test_historical.py -q
```

Result: `19 passed in 0.57s`; failed=0, errors=0, skipped=0, xfailed=0, xpassed=0. This is the accepted Golden-test source for the 18W/2L, 19W/1L, 20W/0L, and 50W/50L gate outcomes.

## Step 7 preparation and production-path probes

```powershell
uv run python tools/localization_step7_prepare.py compile-qm
uv run python tools/localization_step7_prepare.py prepare all
uv run python tools/localization_step7_prepare.py probe healthy_en
uv run python tools/localization_step7_prepare.py probe healthy_zh
uv run python tools/localization_step7_prepare.py traceability-check
uv run python tools/localization_step7_prepare.py safety-check
```

All exited 0. QM compilation reported 225 active/finished translations, zero unfinished, and 225 QTranslator matches. Both rich probes observed Isaac `valid` and statistically ready at 50W/50L, Magdalene `insufficient` and not ready at 1W/0L, and Cain `no_history` with 0W/0L eligible history. Traceability confirmed 212 unique NOT_RUN rows, 204 mandatory rows, 8 N/A_ALLOWED rows, the fixed Preparation totals, and formal scaling 150%. Safety reported all eight checks true.

## Accepted regression gates

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest tests/localization/test_bilingual_business_parity.py tests/localization/test_bilingual_failure_parity.py tests/localization/test_localization_drift_guardrails.py -q
uv run pytest tests/localization/test_architecture.py tests/localization/test_presentation_architecture.py tests/localization/test_localization_drift_guardrails.py -q
uv run pytest tests/localization -q
uv run pytest
```

Results: 29 passed in 4.43s; 44 passed in 3.04s; 327 passed in 20.69s; 1340 passed in 127.25s. For every pytest command: failed=0, errors=0, skipped=0, xfailed=0, xpassed=0.

## Schema and static checks

```powershell
$env:PYTHONPATH='src'; uv run python -c '<schema inventory assertion>'
uv run ruff check .
uv run ruff format --check .
git diff --check
```

The schema assertion passed: user version 1; tables `character_stats`, `characters`, `history_regimes`, `meta`, `round_analysis_snapshots`, and `rounds`; localization columns `[]`. Ruff check passed, the final Ruff format check reported 255 files already formatted, and the Git whitespace check produced no output.

## Final runtime and boundary audit

- Final `prepare all`: exit 0.
- Runtime inventory: 45 scenarios, 187 files, 0 log/lock/Daily residue.
- Production changes: 0; protected 340-file SHA-256 remained `d5e2e732833744864a1bc675aae29f2e8f35e7dbccfff6a41867f00299b036df`.
- Checklist: 212 formal rows, all NOT_RUN; 204 mandatory and 8 N/A_ALLOWED.
- Existing results are unchanged and formal scaling remains 150%.
- Step 7 manual acceptance remains paused; no completion report exists; Step 8/9 were not started.
