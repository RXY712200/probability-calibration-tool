# Localization Step 7 Localization-Delta Manual Scope Rebaseline Validation

Status: `STEP 7 LOCALIZATION-DELTA MANUAL SCOPE REBASELINE COMPLETE — READY FOR EXTERNAL REVIEW`

Validation is recorded after the required commands complete. The frozen old 212-row contract is superseded by the new 63-row localization-delta contract; it is not rewritten as historical completion evidence.

## Contract totals

| Gate | Rows | Mandatory | N/A_ALLOWED | NOT_RUN |
|---|---:|---:|---:|---:|
| A | 7 | 7 | 0 | 7 |
| B | 15 | 15 | 0 | 15 |
| C | 15 | 15 | 0 | 15 |
| D | 16 | 14 | 2 | 16 |
| E | 8 | 8 | 0 | 8 |
| F | 2 | 2 | 0 | 2 |
| Total | 63 | 61 | 2 | 63 |

The traceability gate verifies unique IDs, all `NOT_RUN`, 150%-only formal scaling, no legacy DPI IDs, no 100%/125% formal route, every guide route as a prepared scenario or approved environment route, all 12 contexts, all 34 character mappings, lifecycle mandatory core, safety-priority mandatory core, English and zh_CN presentation coverage, and absence of formal destructive business-transaction recertification.

## Commands and results

```powershell
uv run python tools/localization_step7_prepare.py compile-qm
uv run python tools/localization_step7_prepare.py prepare all
uv run python tools/localization_step7_prepare.py traceability-check
uv run python tools/localization_step7_prepare.py safety-check
```

All exited 0. QM validation reported frozen TS SHA-256 `82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257`, 225 active/finished translations, zero unfinished translations, and QTranslator 225/225. The final runtime inventory is 45 scenarios, 187 files, and zero log/lock/Daily residue.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest tests/localization/test_bilingual_business_parity.py tests/localization/test_bilingual_failure_parity.py tests/localization/test_localization_drift_guardrails.py -q
uv run pytest tests/localization/test_architecture.py tests/localization/test_presentation_architecture.py tests/localization/test_localization_drift_guardrails.py -q
uv run pytest tests/localization -q
uv run pytest
```

Results: 29 passed in 7.89s; 44 passed in 9.30s; 327 passed in 19.84s; 1340 passed in 102.98s. For every pytest command: failed=0, errors=0, skipped=0, xfailed=0, xpassed=0.

```powershell
uv run ruff check .
uv run ruff format --check .
git diff --check
```

All exited 0. Ruff check passed, Ruff format reported 258 files already formatted, and the Git whitespace check produced no output.

## Identity and boundary audit

- Schema: `user_version=1`; exact tables are `character_stats`, `characters`, `history_regimes`, `meta`, `round_analysis_snapshots`, and `rounds`; localization columns are absent.
- Production changes = 0. The protected production/frozen-file inventory remained 340 files with SHA-256 `d5e2e732833744864a1bc675aae29f2e8f35e7dbccfff6a41867f00299b036df`.
- Official TS and QA QM identity are unchanged; QTranslator remains 225/225.
- All 17 existing raw PNG files are preserved; the fixture-mismatch observation remains present and non-defect evidence.
- Step 7 manual execution remains paused. No Step 7 completion report was created. Step 8 and Step 9 were not started.
