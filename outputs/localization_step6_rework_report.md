# Localization Step 6 External Review Narrow Rework Report

## Scope

This narrow, test-only rework strengthens the formal P10–P14 evidence requested by external review. No production code, official translation catalog, schema, dependency, packaging, version, or SPEC file changed. Step 7–9 were not started.

## Files

Modified:

- `tests/localization/test_bilingual_business_parity.py` — P10/P11 now capture the actual `runtime.result.disposition` before Restore and assert the observed normal/emergency values in both language tracks.
- `tests/localization/test_bilingual_failure_parity.py` — P12 now proves exact invalid-input DB before/after equality; P13 and P14 now execute through real DesktopHost/DesktopWindow/session paths with actual business-call spies and real presentation-boundary failures.
- `outputs/localization_step6_qa_matrix.md` — P10–P14 rows now describe the strengthened observed oracles and actual test seams.

Added:

- `outputs/localization_step6_rework_report.md` — this rework scope, evidence, and result report.
- `outputs/localization_step6_rework_validation.md` — literal commands and exact validation results.

Deleted:

- none

The original `outputs/localization_step6_completion_report.md` and `outputs/localization_step6_validation_commands.md` were not overwritten.

## Finding 1 — Real production P14 boundary

Both variants run separate real EN and official-QM zh_CN processes-in-test with isolated app roots, settings, databases, backups, logs, DesktopHost, DesktopWindow, and DesktopSession state. Business IDs and clocks are deterministic and compared; random Error IDs are checked for presence/correlation only.

P14 Calculate:

- Carrier: real character/reference/input widget interaction followed by the real Calculate button path.
- Actual mutation spy: `RoundService.calculate` beneath the production Workflow/IntegratedRoundActions path.
- Failure seam: real `AnalysisPanel.render` after the business commit.
- Actual business call count: 1 in EN and 1 in zh_CN.
- Failed post-commit render count: 1 per track.
- Persisted rounds: total=1, pending=1.
- Persisted analysis snapshots: 1.
- Duplicate round/snapshot: none.
- Production `report_unexpected`: 1 per track.
- UI: Error ID present; private diagnostic and traceback absent.
- Log: matching Error ID, private diagnostic, and traceback present.

P14 Correction:

- Carrier: real Correction page selection, Begin, result/include/reason input, and Confirm path.
- Actual mutation spy: `CorrectionService.correct_post_run` beneath `DesktopSession.correct`.
- Failure seam: real post-commit `DesktopSession.correction_candidates` refresh invoked by DesktopWindow.
- Actual business call count: 1 in EN and 1 in zh_CN.
- Explicit second consumed-confirmation call remains a no-op; count remains 1.
- Total rounds: 2.
- Original A voided count: 1.
- Completed replacement B with `supersedes_round_id=A`: 1.
- Total non-null supersedes relationships: 1.
- Analysis snapshots: 2.
- Duplicate replacement: none.
- Production `report_unexpected`: 1 per track.
- UI/log safety: same Error ID/private-diagnostic/traceback guarantees as Calculate.

## Finding 2 — Observed P10/P11 startup disposition

The result structure now records `runtime.result.disposition` read from the actual StartupService runtime after `DesktopHost.show_initial_state()` and before Restore.

- P10 EN observed: `StartupDisposition.READY_DRAFT`.
- P10 zh_CN observed: `StartupDisposition.READY_DRAFT`.
- P11 damaged-live EN observed: `StartupDisposition.EMERGENCY_RECOVERY`.
- P11 damaged-live zh_CN observed: `StartupDisposition.EMERGENCY_RECOVERY`.
- EN and zh_CN machine/persistence results remain equal.

No expected constant is inserted into the returned machine structure. Expected values are asserted separately against the observed field.

## Finding 3 — Real P13 pre-commit no-retry

For each of UNKNOWN, unrecognized code, ROUND_NOT_FOUND, ROUND_NOT_PENDING, and ROUND_NOT_COMPLETED, both language tracks now:

- execute the real Desktop Calculate UI/session carrier;
- patch the actual underlying `RoundService.calculate` seam to raise the selected error;
- observe actual business call count=1;
- observe production `report_unexpected` count=1;
- assert full canonical DB `after == before` within each track;
- retain Workflow state DRAFT;
- show a safe Error ID without the private diagnostic;
- write the private diagnostic and traceback to the real track log;
- perform no retry.

Across five errors and two languages, all ten actual business-operation observations are count=1.

## Finding 4 — Explicit P12 zero-write

P12 now captures:

- `before_invalid = canonical_database(...)` immediately before invalid Calculate;
- `after_invalid = canonical_database(...)` immediately after the expected InputValidationError;
- exact assertion `after_invalid == before_invalid` before the valid pending round is created.

The returned validation oracle includes both snapshots and `database_unchanged=True`. The existing pending-regime-block public business-rule case then proceeds unchanged.

## Normalization

No normalization was broadened. `character_stats.updated_at` remains the sole business-database field normalization. Random Error IDs are compared by required presence/correlation. IDs, states, result/include, probability/odds, regimes, snapshots, supersedes links, provenance, ErrorCode, WarningCode, and user reasons remain unnormalized.

## Validation summary

- Strengthened P10–P14: 10 passed.
- All Step 6-specific: 29 passed.
- Localization architecture/static: 44 passed.
- All localization: 327 passed.
- Full suite: 1340 passed.
- Failed/errors/skipped/xfailed/xpassed: 0/0/0/0/0.
- Fresh extraction: production 225, official 225, contexts 12, missing 0, extra 0.
- Strict lrelease: 225 finished, 0 unfinished.
- Direct QTranslator: 225/225.
- Schema: user_version=1, exact six tables, no localization columns.
- Ruff check: passed.
- Ruff format check: 232 files already formatted.
- `git diff --check`: passed with no output.
- Protected files: 182 before / 182 after; missing=0, added=0, changed=0.
- Official TS SHA-256 unchanged: `82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257`.

No protected production file changed. No frozen-stage production defect was discovered.

Final status: `STEP 6 NARROW REWORK COMPLETE — READY FOR EXTERNAL RE-REVIEW`
