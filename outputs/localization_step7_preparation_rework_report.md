# Localization Step 7 Manual Acceptance Preparation Narrow Rework Report

Status: `STEP 7 MANUAL ACCEPTANCE PREPARATION NARROW REWORK COMPLETE — READY FOR EXTERNAL RE-REVIEW`

## Scope and outcome

This is a test/manual-QA preparation correction only. No production source, official TS, schema, dependency, packaging, installer, version, or frozen Step 3-6 asset was changed. Human visual acceptance was not performed.

The rework restores real bilingual routes for every critical `Language=Both` row, adds the eight omitted geometry rows, prepares true Data Safety priority combinations, removes language overclaims from the manifest, and hardens every preparation-tool reset/write/mutation boundary against nested reparse escape.

## Modified

Exact durable files modified from the rejected first preparation attempt:

- `tools/localization_step7_prepare.py` — added 19 isolated scenarios, real warning-combination seams, nested mutation guards, disposable junction safety self-tests, and the 235-row traceability gate.
- `outputs/localization_step7_manual_checklist.md` — added the eight frozen geometry rows, changed CR-SAFE-03 to accurate `en fallback`, and updated totals.
- `outputs/localization_step7_execution_guide.md` — added exact bilingual routes, evidence paths, geometry steps, Data Safety combinations, and exhaustive traceability.
- `outputs/localization_step7_scenario_manifest.md` — records actual preferred/effective language, pack, DB, fault seam, and supported route side without EN/zh overclaims.
- `outputs/localization_step7_runtime/README.md` — updated disposable-state count and nested reparse safety boundary.

The 111 retained runtime paths from the first preparation were rebuilt as disposable state by `prepare all`. Their exact final paths are included in the final 187-file inventory below.

## Added

Durable rework records:

- `outputs/localization_step7_preparation_rework_report.md` — this report.
- `outputs/localization_step7_preparation_rework_validation.md` — exact command/result evidence.

New disposable runtime paths: 76.

- `outputs/localization_step7_runtime/correction_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/correction_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/correction_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/correction_en/scenario.json`
- `outputs/localization_step7_runtime/correction_warning_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/correction_warning_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/correction_warning_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/correction_warning_en/scenario.json`
- `outputs/localization_step7_runtime/correction_warning_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/correction_warning_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/correction_warning_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/correction_warning_zh/scenario.json`
- `outputs/localization_step7_runtime/data_safety_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/data_safety_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/data_safety_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/data_safety_en/scenario.json`
- `outputs/localization_step7_runtime/data_safety_fallback/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/data_safety_fallback/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/data_safety_fallback/scenario.json`
- `outputs/localization_step7_runtime/data_safety_warning_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/data_safety_warning_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/data_safety_warning_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/data_safety_warning_en/scenario.json`
- `outputs/localization_step7_runtime/data_safety_warning_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/data_safety_warning_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/data_safety_warning_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/data_safety_warning_zh/scenario.json`
- `outputs/localization_step7_runtime/multiple_pending_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/multiple_pending_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/multiple_pending_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/multiple_pending_zh/scenario.json`
- `outputs/localization_step7_runtime/over_retention_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/over_retention_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/over_retention_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/over_retention_en/scenario.json`
- `outputs/localization_step7_runtime/over_retention_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/over_retention_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/over_retention_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/over_retention_zh/scenario.json`
- `outputs/localization_step7_runtime/quarantine_warning_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/quarantine_warning_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/quarantine_warning_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/quarantine_warning_en/scenario.json`
- `outputs/localization_step7_runtime/quarantine_warning_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/quarantine_warning_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/quarantine_warning_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/quarantine_warning_zh/scenario.json`
- `outputs/localization_step7_runtime/recovery_no_pending_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/recovery_no_pending_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/recovery_no_pending_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/recovery_no_pending_zh/scenario.json`
- `outputs/localization_step7_runtime/recovery_stale_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/recovery_stale_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/recovery_stale_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/recovery_stale_en/scenario.json`
- `outputs/localization_step7_runtime/recovery_stale_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/recovery_stale_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/recovery_stale_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/recovery_stale_zh/scenario.json`
- `outputs/localization_step7_runtime/recovery_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/recovery_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/recovery_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/recovery_zh/scenario.json`
- `outputs/localization_step7_runtime/restore_normal_en/localappdata/ProbabilityCalibrationTool/backups/recent/recent_20260901T120000.000000Z_state-b-0001.db`
- `outputs/localization_step7_runtime/restore_normal_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/restore_normal_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/restore_normal_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/restore_normal_en/scenario.json`
- `outputs/localization_step7_runtime/unexpected_warning_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/unexpected_warning_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/unexpected_warning_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/unexpected_warning_en/scenario.json`
- `outputs/localization_step7_runtime/unexpected_warning_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/unexpected_warning_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/unexpected_warning_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/unexpected_warning_zh/scenario.json`

## Deleted

- none

The rejected first-attempt reports were preserved without edits:

- `outputs/localization_step7_preparation_report.md`
- `outputs/localization_step7_preparation_validation.md`

The defect log was not modified. `outputs/localization_step7_completion_report.md` was not created.

## Final counts

- scenarios: 45 declared / 45 prepared / 0 missing / 0 extra / 0 spec mismatch
- runtime files: 187
- runtime bytes: 5,961,960
- checklist rows: 235
- unique IDs: 235
- MANDATORY: 227
- N/A_ALLOWED: 8
- NOT_RUN: 235
- PASS: 0
- FAIL: 0
- selected N/A: 0
- all critical Language=Both routes: 26/26 with independent Effective=en and Effective=zh_CN scenarios
- zh_CN DPI routes: 18/18 use Effective=zh_CN
- fallback-English routes counted as zh_CN: 0

## Cross-language critical coverage

The final guide supplies independent EN and Effective=zh_CN routes for all 26 critical `Language=Both` rows. This includes Recovery, expected errors, Data Safety, unexpected error/priority, Restore Cancel/minimum/keyboard, Emergency/unexpected geometry, stale/repeat observations, and the four N/A_ALLOWED critical rows. Those four rows remain NOT_RUN and no N/A decision was selected.

## Data Safety combinations

- CR-SAFE-01: `data_safety_en` (Effective=en) plus `data_safety` (Effective=zh_CN).
- CR-SAFE-03: `data_safety_fallback` combines the missing-snapshot Data Safety condition with Preferred=zh_CN, missing pack, and Effective=en fallback. Checklist metadata is `en fallback`.
- CR-SAFE-04: `data_safety_warning_en` and `data_safety_warning_zh` append the existing `WarningCode.BACKUP_OVER_RETENTION` at `RuntimeContext.result.warnings` after real StartupService evaluation. Real DesktopHost, SafetyWindow, safe-error, and warning-list presentation remain in use.
- CR-UNX-05: `unexpected_warning_en` and `unexpected_warning_zh` provide the error-over-warning combination in both effective languages.
- CR-REC-09: `recovery_stale_en` and `recovery_stale_zh` remove only the isolated pending snapshot after the real Recovery page exists.
- CR-COR-05: `correction_warning_en` and `correction_warning_zh` preserve the real Correction commit and inject only the existing Recent-backup failure seam.
- CR-BK-03/04: bilingual routes append only the named existing over-retention/quarantine warning code to the real startup result and use real warning presentation.

Every injected launcher prints `TEST-ONLY MANUAL QA FAULT INJECTION` and the exact seam. No fake text, dialog, page, or production replacement was introduced.

## Safety guards

All required refusal cases passed:

- unknown scenario rejected
- unauthorized mutation rejected
- runtime root project-controlled
- scenario-level reparse escape rejected
- nested languages reparse rejected
- nested backup reparse rejected
- nested data reparse rejected
- QA artifact output reparse escape rejected
- reparse mechanism exercised: disposable Windows directory junction

Reset additionally scans the entire scenario tree and refuses nested reparse points before recursive deletion. Pack removal/restoration, candidate expiry, pending/snapshot mutation, QA compilation/writes, and fixture writes all resolve through guarded targets. The real default LocalAppData root is discovered from the Windows user-shell registry (with a USERPROFILE fallback), so a scenario-level `LOCALAPPDATA` override cannot be mistaken for the user's real root. Safety tests used only `outputs/localization_step7_runtime/_safety_selftest` and never the real user application root.

## Final runtime inventory (187 files)

- `outputs/localization_step7_runtime/README.md`
- `outputs/localization_step7_runtime/_qa_artifacts/fresh_production_extraction.ts`
- `outputs/localization_step7_runtime/_qa_artifacts/qa_qm_identity.json`
- `outputs/localization_step7_runtime/_qa_artifacts/schema_gate.db`
- `outputs/localization_step7_runtime/_qa_artifacts/step7_qa_probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/already_running/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/already_running/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/already_running/scenario.json`
- `outputs/localization_step7_runtime/backup_warning/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/backup_warning/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/backup_warning/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/backup_warning/scenario.json`
- `outputs/localization_step7_runtime/confirm_pack_loss/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/confirm_pack_loss/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/confirm_pack_loss/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/confirm_pack_loss/scenario.json`
- `outputs/localization_step7_runtime/correction/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/correction/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/correction/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/correction/scenario.json`
- `outputs/localization_step7_runtime/correction_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/correction_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/correction_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/correction_en/scenario.json`
- `outputs/localization_step7_runtime/correction_warning_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/correction_warning_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/correction_warning_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/correction_warning_en/scenario.json`
- `outputs/localization_step7_runtime/correction_warning_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/correction_warning_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/correction_warning_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/correction_warning_zh/scenario.json`
- `outputs/localization_step7_runtime/corrupt_pack/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/corrupt_pack/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/corrupt_pack/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/corrupt_pack/scenario.json`
- `outputs/localization_step7_runtime/data_safety/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/data_safety/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/data_safety/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/data_safety/scenario.json`
- `outputs/localization_step7_runtime/data_safety_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/data_safety_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/data_safety_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/data_safety_en/scenario.json`
- `outputs/localization_step7_runtime/data_safety_fallback/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/data_safety_fallback/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/data_safety_fallback/scenario.json`
- `outputs/localization_step7_runtime/data_safety_warning_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/data_safety_warning_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/data_safety_warning_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/data_safety_warning_en/scenario.json`
- `outputs/localization_step7_runtime/data_safety_warning_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/data_safety_warning_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/data_safety_warning_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/data_safety_warning_zh/scenario.json`
- `outputs/localization_step7_runtime/emergency_invalid/localappdata/ProbabilityCalibrationTool/backups/recent/recent_20260901T120000.000000Z_emergency-good-0001.db`
- `outputs/localization_step7_runtime/emergency_invalid/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/emergency_invalid/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/emergency_invalid/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/emergency_invalid/scenario.json`
- `outputs/localization_step7_runtime/emergency_missing_pack/localappdata/ProbabilityCalibrationTool/backups/recent/recent_20260901T120000.000000Z_emergency-good-0001.db`
- `outputs/localization_step7_runtime/emergency_missing_pack/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/emergency_missing_pack/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/emergency_missing_pack/scenario.json`
- `outputs/localization_step7_runtime/emergency_restore/localappdata/ProbabilityCalibrationTool/backups/recent/recent_20260901T120000.000000Z_emergency-good-0001.db`
- `outputs/localization_step7_runtime/emergency_restore/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/emergency_restore/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/emergency_restore/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/emergency_restore/scenario.json`
- `outputs/localization_step7_runtime/healthy_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/healthy_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/healthy_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/healthy_en/scenario.json`
- `outputs/localization_step7_runtime/healthy_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/healthy_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/healthy_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/healthy_zh/scenario.json`
- `outputs/localization_step7_runtime/invalid_preference/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/invalid_preference/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/invalid_preference/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/invalid_preference/scenario.json`
- `outputs/localization_step7_runtime/lifecycle/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/lifecycle/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/lifecycle/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/lifecycle/scenario.json`
- `outputs/localization_step7_runtime/missing_pack/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/missing_pack/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/missing_pack/scenario.json`
- `outputs/localization_step7_runtime/multiple_pending/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/multiple_pending/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/multiple_pending/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/multiple_pending/scenario.json`
- `outputs/localization_step7_runtime/multiple_pending_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/multiple_pending_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/multiple_pending_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/multiple_pending_zh/scenario.json`
- `outputs/localization_step7_runtime/over_retention_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/over_retention_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/over_retention_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/over_retention_en/scenario.json`
- `outputs/localization_step7_runtime/over_retention_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/over_retention_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/over_retention_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/over_retention_zh/scenario.json`
- `outputs/localization_step7_runtime/quarantine_warning_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/quarantine_warning_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/quarantine_warning_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/quarantine_warning_en/scenario.json`
- `outputs/localization_step7_runtime/quarantine_warning_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/quarantine_warning_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/quarantine_warning_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/quarantine_warning_zh/scenario.json`
- `outputs/localization_step7_runtime/recovery/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/recovery/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/recovery/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/recovery/scenario.json`
- `outputs/localization_step7_runtime/recovery_localization_fallback/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/recovery_localization_fallback/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/recovery_localization_fallback/scenario.json`
- `outputs/localization_step7_runtime/recovery_no_pending/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/recovery_no_pending/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/recovery_no_pending/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/recovery_no_pending/scenario.json`
- `outputs/localization_step7_runtime/recovery_no_pending_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/recovery_no_pending_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/recovery_no_pending_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/recovery_no_pending_zh/scenario.json`
- `outputs/localization_step7_runtime/recovery_stale_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/recovery_stale_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/recovery_stale_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/recovery_stale_en/scenario.json`
- `outputs/localization_step7_runtime/recovery_stale_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/recovery_stale_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/recovery_stale_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/recovery_stale_zh/scenario.json`
- `outputs/localization_step7_runtime/recovery_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/recovery_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/recovery_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/recovery_zh/scenario.json`
- `outputs/localization_step7_runtime/restore_corrupt/localappdata/ProbabilityCalibrationTool/backups/recent/recent_20260901T120000.000000Z_corrupt-0001.db`
- `outputs/localization_step7_runtime/restore_corrupt/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/restore_corrupt/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/restore_corrupt/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/restore_corrupt/scenario.json`
- `outputs/localization_step7_runtime/restore_invalid/localappdata/ProbabilityCalibrationTool/backups/recent/recent_20260901T120000.000000Z_state-b-0001.db`
- `outputs/localization_step7_runtime/restore_invalid/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/restore_invalid/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/restore_invalid/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/restore_invalid/scenario.json`
- `outputs/localization_step7_runtime/restore_normal/localappdata/ProbabilityCalibrationTool/backups/recent/recent_20260901T120000.000000Z_state-b-0001.db`
- `outputs/localization_step7_runtime/restore_normal/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/restore_normal/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/restore_normal/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/restore_normal/scenario.json`
- `outputs/localization_step7_runtime/restore_normal_en/localappdata/ProbabilityCalibrationTool/backups/recent/recent_20260901T120000.000000Z_state-b-0001.db`
- `outputs/localization_step7_runtime/restore_normal_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/restore_normal_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/restore_normal_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/restore_normal_en/scenario.json`
- `outputs/localization_step7_runtime/save_failure/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/save_failure/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/save_failure/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/save_failure/scenario.json`
- `outputs/localization_step7_runtime/unexpected_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/unexpected_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/unexpected_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/unexpected_en/scenario.json`
- `outputs/localization_step7_runtime/unexpected_warning_en/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/unexpected_warning_en/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/unexpected_warning_en/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/unexpected_warning_en/scenario.json`
- `outputs/localization_step7_runtime/unexpected_warning_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/unexpected_warning_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/unexpected_warning_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/unexpected_warning_zh/scenario.json`
- `outputs/localization_step7_runtime/unexpected_zh/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/unexpected_zh/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/unexpected_zh/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/unexpected_zh/scenario.json`
- `outputs/localization_step7_runtime/wrong_filename/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/wrong_filename/localappdata/ProbabilityCalibrationTool/languages/probability_calibration_tool_zh_CN.WRONG.qm`
- `outputs/localization_step7_runtime/wrong_filename/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/wrong_filename/scenario.json`
- `outputs/localization_step7_runtime/wrong_location/localappdata/ProbabilityCalibrationTool/data/probability.db`
- `outputs/localization_step7_runtime/wrong_location/localappdata/ProbabilityCalibrationTool/probability_calibration_tool_zh_CN.qm`
- `outputs/localization_step7_runtime/wrong_location/localappdata/ProbabilityCalibrationTool/settings.ini`
- `outputs/localization_step7_runtime/wrong_location/scenario.json`

## Boundary confirmation

- Human visual acceptance: NOT performed.
- All 235 checklist rows: NOT_RUN.
- Screenshot judged PASS: none.
- Step 7 completion report: not created.
- Production modification: none.
- Step 8: not started.
- Step 9: not started.
- Commit/tag/push/reset/checkout/release/distribution build: none.
