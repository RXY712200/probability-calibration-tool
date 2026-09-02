# Localization Step 7 Manual Acceptance Preparation Final Consistency Rework Report

Status: `STEP 7 MANUAL ACCEPTANCE PREPARATION FINAL CONSISTENCY REWORK COMPLETE — READY FOR EXTERNAL FINAL REVIEW`

## Scope and outcome

This was a preparation-contract correction only. It made no production-code change, performed no human visual acceptance, selected no checklist result, and did not start Step 8 or Step 9.

The final machine gates prove:

- checklist IDs: 235/235 unique
- requirements: 227 `MANDATORY`, 8 `N/A_ALLOWED`
- results: 235 `NOT_RUN`, 0 PASS, 0 FAIL, 0 selected N/A
- critical bilingual routes: 26/26
- zh_CN DPI routes: 18/18 Effective=zh_CN
- human screenshots: 0

## Modified files

- `outputs/localization_step7_manual_checklist.md` — corrected ZH-DPI125-07 and ZH-DPI150-07 to the aggregate six-page minimum-practical contract.
- `outputs/localization_step7_execution_guide.md` — separated Regime from dedicated Correction/Restore routes, defined the twelve screenshots per zh_CN scaling, removed stale fixed-count fault wording, removed the malformed Appendix A heading, and replaced phantom trace paths with session/evidence references.
- `outputs/localization_step7_scenario_manifest.md` — removed broad EN/ZH claims, assigned dedicated Correction/Restore DPI ownership, removed Data Safety ownership of CR-GEO-03, and narrowed the Recovery-localization fallback claim.
- `tools/localization_step7_prepare.py` — strengthened traceability-check with exact count, aggregate DPI route/page, manifest ownership, broad-overclaim, and phantom-trace gates.

The disposable `outputs/localization_step7_runtime/` tree was rebuilt from the unchanged 45-scenario definitions. Final inventory: 45 scenario roots, 187 files, 5,961,960 bytes, and zero log/lock/daily/cache/safety-self-test residue.

## Added files

- `outputs/localization_step7_preparation_final_rework_report.md`
- `outputs/localization_step7_preparation_final_rework_validation.md`

## Deleted files

None.

The generated `outputs/localization_step7_runtime/_qa_artifacts/fresh_production_extraction.ts` was safely replaced in place for a fresh extraction audit; no source or accepted report was deleted.

## High-DPI contract

At both 125% and 150%:

- IDs 01–04 use `healthy_zh` for DRAFT, Characters, Analysis, and Maintenance.
- ID 05 uses `correction`.
- ID 06 uses `restore_normal`.
- ID 07 is the aggregate of `healthy_zh+correction+restore_normal` and requires six separate minimum-practical screenshots: DRAFT, Characters, Analysis, Maintenance, Correction, and Restore.
- all routes are Effective=zh_CN; fallback English is not counted.

## Session and manifest corrections

- Session A: `healthy_en` owns Regime; `correction_en` and `restore_normal_en` own their default and minimum-practical evidence.
- Session B: `healthy_zh` owns Regime; `correction` and `restore_normal` own their default and minimum-practical evidence.
- Healthy scenario rows no longer use `EN-*` or `ZH-*` broad claims and do not claim dedicated Correction/Restore IDs.
- `data_safety_en` and `data_safety` no longer claim CR-GEO-03. Emergency minimum geometry remains on `emergency_invalid`/`emergency_restore`.
- `recovery_localization_fallback` is narrowed to CR-REC-04 and LC-63.

## Protected scope

The captured protected set contained 340 files across production source, non-localization tests, SPEC/config/lock files, official TS, and packaging. Its normalized aggregate SHA-256 remained:

`d5e2e732833744864a1bc675aae29f2e8f35e7dbccfff6a41867f00299b036df` → `d5e2e732833744864a1bc675aae29f2e8f35e7dbccfff6a41867f00299b036df`

Production code changes in this rework: 0.

Official TS remained SHA-256 `82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257`.

The four previously accepted Step 7 preparation reports remained byte-identical at their recorded SHA-256 values. No Step 3–6 report or test was changed.

## Boundary

- Human visual acceptance: NOT performed.
- All 235 checklist rows: NOT_RUN.
- Screenshots judged PASS: 0.
- Step 7 completion report: absent.
- Production code changes: 0.
- Step 8: NOT started.
- Step 9: NOT started.
- Commit/tag/push/reset/checkout/release/distribution build: none.
