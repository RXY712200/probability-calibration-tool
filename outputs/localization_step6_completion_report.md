# Localization Step 6 Completion Report

## A. Scope summary

Localization Step 6 added tests-only automated regression and localization QA. It introduced a real official-QM bilingual harness, formal P1–P14 machine/persistence parity, failure/no-retry evidence, source/catalog/runtime/schema drift guardrails, and three evidence reports. No production implementation, official TS, schema, dependency, packaging, version, or SPEC file was changed.

## B. Files changed

Modified:

- none

Added:

- `tests/localization/qa_helpers.py` — isolated EN/zh_CN test tracks, deterministic business clock/IDs, strict official-QM builder, and explicit six-table canonical comparator.
- `tests/localization/test_bilingual_business_parity.py` — P1–P11, representative subjective probabilities, textual odds, recovery, and restore parity.
- `tests/localization/test_bilingual_failure_parity.py` — P12–P14 expected/unexpected failure, logging, Error ID, commit/no-retry parity.
- `tests/localization/test_localization_drift_guardrails.py` — fresh extraction, runtime-pack, identity/mapping/schema, and real-QM anti-anchoring gates.
- `outputs/localization_step6_completion_report.md` — this A–K completion report.
- `outputs/localization_step6_validation_commands.md` — literal validation commands and results.
- `outputs/localization_step6_qa_matrix.md` — actual P1–P14 and failure/architecture traceability.

Deleted:

- none

No Step 6 file was changed and later reverted. The working tree already contained the accepted Step 3–5 implementation and evidence as uncommitted/untracked content before Step 6; those files were not authored or modified by Step 6.

## C. Fresh catalog/QM

- Official TS: `translations/probability_calibration_tool_zh_CN.ts`
- Official TS SHA-256: `82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257`
- Fresh production extraction: 225 active source keys
- Official catalog: 225 active source keys
- Exact contexts: 12
- Missing: 0
- Extra: 0
- Strict lrelease: exit 0; `225 finished and 0 unfinished`
- Fresh QM: `C:/Users/rxy71/AppData/Local/Temp/pct-step6-final/probability_calibration_tool_zh_CN.qm`
- QM size: 19,429 bytes
- QM SHA-256: `712747514fccce8f3f5e610dbdddf07187f9167b22d33365f97ca06a4d9b5547`
- PySide6: 6.11.2
- Qt: 6.11.2
- Direct QTranslator audit: loaded=true, 225/225 exact translations

The fresh extraction comparison uses semantic `(context, source, numerus)` keys. TS location metadata and source-file line numbers are not semantic.

## D. Bilingual parity

Every formal scenario starts two isolated tracks. EN asserts Effective=`en` and no app translator. zh_CN asserts Preferred=`zh_CN`, Effective=`zh_CN`, and an installed real app translator compiled from the official TS.

| ID | Implemented machine/persistence oracle | Test reference |
|---|---|---|
| P1 | Basic Calculate/no history; locked analysis and persistence | `test_bilingual_business_parity.py::test_p1_p9_formal_bilingual_business_and_six_table_parity[P1]` |
| P2 | Insufficient-history model, readiness, interval, snapshot | same family `[P2]` |
| P3 | Valid-history model, EV/relation facts, snapshot | same family `[P3]` |
| P4 | Same-round Modify/Recalculate lock and Loss+Include completion | same family `[P4]` |
| P5 | Win+Exclude retained completed row and excluded stats | same family `[P5]` |
| P6 | Void audit, exact Unicode reason, no history contribution | same family `[P6]` |
| P7 | Old/new regime semantics, retained old history, exact Unicode reason | same family `[P7]` |
| P8 | A/B correction, supersedes link, copied prediction/snapshot, Loss+Exclude | same family `[P8]` |
| P9 | Recovery same round/snapshot, no Calculate/new ID/duplicate commit, Win+Include | same family `[P9]` |
| P10 | Normal Restore, pre-restore safety provenance, session replacement | `test_p10_p11_formal_bilingual_restore_parity[P10-normal]` |
| P11 | Emergency Restore and correct no-normal-safety distinction | same family `[P11-emergency]` |
| P12 | Public validation/business semantic code, field, state, zero/blocked effects | `test_bilingual_failure_parity.py::test_p12_formal_bilingual_expected_validation_and_business_failure_parity` |
| P13 | UNKNOWN/unrecognized/stale codes, safe UI, Error ID, full log, no retry | `test_p13_formal_bilingual_unknown_and_stale_failure_parity` |
| P14 | Calculate and Correction commits survive presentation/refresh failure exactly once | `test_p14_formal_bilingual_commit_then_presentation_failure_is_never_retried` |

All six frozen tables are read using explicit column lists and stable semantic ordering: `characters`, `history_regimes`, `rounds`, `round_analysis_snapshots`, `character_stats`, and `meta`. P1–P14 collectively compare their semantic persistence effects; the core scenario harness snapshots all six tables.

Normalization allowlist:

- `character_stats.updated_at` only, replaced by a test sentinel because that repository audit timestamp has no injected-clock seam and the language tracks run sequentially.
- Random Error IDs are compared for required presence/correlation, not literal equality.
- Temporary filesystem paths and file mtimes are not business comparator fields.

Character IDs, business round IDs, states, results, include flags, probabilities, odds, regime semantics, snapshot math, supersedes links, backup provenance, ErrorCode, WarningCode, reasons, and persistence effects are not normalized away.

## E. Failure/reliability

- Localization infrastructure: missing/invalid/canonical-name/location packs, settings failures, Qt-only degradation, and app-translator activation cleanup remain covered by `test_catalog.py`, `test_runtime.py`, and `test_bootstrap.py`.
- Preference/save: confirm-time pack disappearance; access/format/readback failure; same-language no-op; Cancel/Esc/X zero-write are covered by `test_preferences.py` and `test_language_ui.py`.
- Expected validation/business: P12 runs real EN/zh_CN tracks; exhaustive structural semantic maps remain covered by presentation integration/mapping tests.
- Unexpected/internal: P13 covers UNKNOWN, unrecognized, ROUND_NOT_FOUND, ROUND_NOT_PENDING, and ROUND_NOT_COMPLETED with private-diagnostic log evidence and safe UI.
- Warning/priority: warning-only, expected+warning, unexpected+warning, and post-commit warning-render failure remain covered by presentation and compound-failure tests.
- Startup: healthy/localization notice, safety/Recovery priority, and ALREADY_RUNNING suppression remain covered.
- Recovery: P9 plus zero/multiple/stale/missing-snapshot application tests.
- Restore: P10/P11 plus invalid candidate, safety failure, replacement failure, and post-replacement failure tests.
- Correction: P8/P14 plus pending/empty-reason/backup failure and compound refresh tests.
- Backup reliability: failed candidate preservation, over-retention, nonfatal Recent/Daily behavior, and quarantine warnings remain covered.

No-retry call-count evidence:

- P13: unexpected pre-commit operation count = 1, production `report_unexpected` count = 1; persistence effect = 0.
- P14 Calculate: business call count = 1; pending round/snapshot effect = exactly 1.
- P14 Correction: business call count = 1; A/B correction effect = exactly 1.
- Existing UI compound tests also assert Calculate/Recalculate, Complete/Correction/Regime, and warning/presentation failure call counts.

Pre-commit and post-commit failures are separate test families and separate persistence oracles.

## F. Architecture/drift

- Source/context drift: fresh production extraction exactly equals the 225 official semantic keys in the frozen 12 contexts.
- Import-layer isolation: Core/Domain/Application/Persistence remain free of UI localization and Qt translation dependencies.
- Runtime-pack restrictions: exact external `languages/probability_calibration_tool_zh_CN.qm`; no globbing, TS loading, project-root, `translations`, build, or cwd discovery.
- Visible-text/error protocol: no translated button/label text drives machine behavior; no `str(exc)`/diagnostic presentation path.
- Enum mapping: exhaustive explicit mappings for EvState, OddsCombinationStatus, ModelRelation, and HistoryModelStatus; explicit N/A.
- Character identity: exact IDs 1–34, no Tainted Esau, stable ID-only CharacterOption, exact CorrectionCandidate fields.
- Preferred/Effective/process lifetime: no live retranslation; save is next-launch-only; same-language no-op and notices remain protected.
- Persistence isolation: schema has no localization-specific business columns; all six-table bilingual oracles compare machine semantics.

Drift categories represented by the gates are `SOURCE_DRIFT`, `CONTEXT_DRIFT`, `CATALOG_DRIFT`, `PRESENTATION_ARCHITECTURE_DRIFT`, `ERROR_BOUNDARY_DRIFT`, `RUNTIME_PACK_DRIFT`, and `BUSINESS_ISOLATION_DRIFT`.

## G. Regression/schema

- Step 6-specific: `29 passed in 3.56s`; failed/errors/skipped/xfailed/xpassed = 0/0/0/0/0.
- Architecture/static: `44 passed in 6.19s`; failed/errors/skipped/xfailed/xpassed = 0/0/0/0/0.
- All localization: `327 passed in 21.10s`; failed/errors/skipped/xfailed/xpassed = 0/0/0/0/0.
- Full suite: `1340 passed in 109.48s`; failed/errors/skipped/xfailed/xpassed = 0/0/0/0/0.
- Schema: `PRAGMA user_version = 1`.
- Exact tables: `character_stats`, `characters`, `history_regimes`, `meta`, `round_analysis_snapshots`, `rounds`.
- Localization-specific business columns: none.
- Ruff check: passed.
- Ruff format check: 230 files already formatted.
- Git diff check: passed with no output.

## H. Protected scope

The protected baseline was captured after initial Step 6 test-only files existed but before any protected edit; no protected file was edited at any point in Step 6.

- Protected files before: 182
- Protected files after: 182
- Missing: 0
- Added within protected groups: 0
- Changed: 0
- Official TS unchanged: yes; SHA-256 remains `82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257`
- Every file under `src/` unchanged by Step 6: yes
- `SPEC_1.0.md`, `pyproject.toml`, `uv.lock`, and `packaging/` unchanged by Step 6: yes

## I. QA matrix

- Path: `outputs/localization_step6_qa_matrix.md`
- Formal scenario rows: 14 (P1–P14)
- P1–P14 traceability: complete; each row points to a real test function/parametrized ID.
- Failure-category traceability: localization infrastructure, preference/save, expected/unexpected errors, warning/priority, startup, Recovery, Restore, Correction, backup reliability, architecture/drift, runtime pack, and persistence.
- The matrix records only actual tests collected and passed; it does not claim manual acceptance.

## J. Git state

- Initial HEAD: `00bd24b9fdc509809962ace4412b1e233b7c6598`
- Final HEAD: `00bd24b9fdc509809962ace4412b1e233b7c6598`
- Initial and final `git status --short` contain the pre-existing uncommitted/untracked accepted Step 3–5 implementation/evidence, plus the new Step 6 tests/reports under the already-untracked `tests/localization/` and `outputs/` directories.
- `git diff --stat`: 45 pre-existing tracked files, 711 insertions, 258 deletions; untracked Step 3–6 files are not included by Git in that statistic.
- Reset/checkout performed: no.
- Commit/tag performed: no.

The literal final status and diff output are retained in `outputs/localization_step6_validation_commands.md` so pre-existing work is not misattributed to Step 6.

## K. Remaining stage boundary

- Step 7: not started.
- Step 8: not started.
- Step 9: not started.
- Manual UI acceptance: not performed.
- Release packaging: not performed.
- Version bump: not performed.
- GitHub Release artifact: not created.
- Final distribution hash freeze: not performed.

Final status: `IMPLEMENTATION COMPLETE — READY FOR EXTERNAL STEP 6 REVIEW`
