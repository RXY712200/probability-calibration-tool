# Localization Step 7 Manual Acceptance Contract Rebaseline Report

Status: `STEP 7 MANUAL ACCEPTANCE CONTRACT REBASELINED TO 150% — READY FOR EXTERNAL REVIEW`

## Decision and scope

Reason: the tester's formal daily Windows environment is 2560×1600 @ 150% Windows display scaling. This is an acceptance-scope decision, not a production defect.

Release 1.0 human UI certification now covers 150% scaling only. Other Windows scaling values are not formally human-certified in this release; this does not mean they are unsupported.

The prior Step 7 preparation contract is superseded only for its scaling matrix. All business, lifecycle, bilingual, safety, geometry, keyboard, stale/repeat, and critical semantics remain in the formal checklist.

## Checklist rebaseline

- Starting contract: 235 rows.
- Removed exactly 23 redundant DPI rows:
  - `EN-DPI-150-01` through `EN-DPI-150-05`
  - `ZH-DPI125-01` through `ZH-DPI125-07`
  - `ZH-DPI150-01` through `ZH-DPI150-07`
  - `CR-DPI150-01` through `CR-DPI150-04`
- Final contract: 212 unique IDs; 204 `MANDATORY`; 8 `N/A_ALLOWED`.
- All 212 rows remain `NOT_RUN`; PASS=0; FAIL=0; selected N/A=0.
- Every remaining English, zh_CN, lifecycle, and critical manual row uses 150%.
- ENV-03 now states: formal UI certification is 2560×1600 @ 150%, with default/minimum-practical/maximized geometry according to checklist coverage.

The old Session F multi-DPI matrix was removed. Sessions A–E now all operate at 150% without Windows scaling changes. Ordinary English and zh_CN coverage, including dedicated Correction and Restore fixtures, is retained at that baseline.

The prior brief 100% English startup observation is `OUT_OF_SCOPE_REBASELINE`; it is not referenced by the formal checklist and carries no PASS result forward.

## Scenario and protected scope

- Scenario count remains 45. Scaling is a Windows human-environment property; no 150%-specific scenarios were added.
- Production changes: 0.
- Protected changes: 0.
- Protected baseline: 340 files, SHA-256 `d5e2e732833744864a1bc675aae29f2e8f35e7dbccfff6a41867f00299b036df` before and after.
- Official TS, SPEC, schema/version, dependencies, packaging, localization business semantics, production UI geometry, accepted Step 3–6 tests/reports, and all prior Step 7 preparation/rework reports were unchanged.

## Files modified

- `outputs/localization_step7_manual_checklist.md`
- `outputs/localization_step7_execution_guide.md`
- `outputs/localization_step7_scenario_manifest.md`
- `tools/localization_step7_prepare.py`

## Files added

- `outputs/localization_step7_manual_contract_rebaseline_report.md`
- `outputs/localization_step7_manual_contract_rebaseline_validation.md`

## Files deleted

None. The 23 listed checklist rows were removed; no raw human evidence was deleted. The disposable runtime fixtures were rebuilt in place with the same 45 scenario paths.

## Boundary

- Human 150% formal acceptance has NOT resumed; it is paused pending external review.
- Formal checklist rows: 212; all 212 are NOT_RUN.
- No formal screenshot PASS is carried forward.
- Step 7 completion report is absent.
- Step 8: NOT started.
- Step 9: NOT started.
- No commit/tag/push/reset/checkout/release/distribution build occurred.
