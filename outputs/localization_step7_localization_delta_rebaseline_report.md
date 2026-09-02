# Localization Step 7 Localization-Delta Manual Scope Rebaseline Report

Status: `STEP 7 LOCALIZATION-DELTA MANUAL SCOPE REBASELINE COMPLETE — READY FOR EXTERNAL REVIEW`

## Why the contract changed

The former Step 7 contract had 212 formal rows and repeated broad Release 1.0 product acceptance: real Correction, Normal Restore, and Emergency Restore transactions; persistence/replacement and atomicity observations; correction supersession; recovery business-state transitions; and post-run mutation confirmation. Those semantics were frozen before localization and remain covered by Step 6 bilingual/business regression. Repeating them manually solely because their screens contain translated text was not localization-delta certification.

This is a manual-certification scope correction, not a production fix, a Step 6 rollback, or a change to frozen business behavior.

## New formal contract

The new contract has **63 formal rows**: **61 MANDATORY** and **2 N/A_ALLOWED**, all `NOT_RUN` after preparation.

| Gate | Rows | Manual localization risk retained |
|---|---:|---|
| A — Environment & Localization Identity | 7 | runtime/pack identity and isolated 150% baseline |
| B — English Built-in Regression | 15 | English presentation regression and representative geometry |
| C — Official zh_CN Presentation | 15 | official QM, glyphs, terminology, 34 character mappings, contexts and geometry |
| D — Language Lifecycle / Fallback | 16 | restart-only lifecycle, fallback, preference and translator states |
| E — Localization-Sensitive Safety / Priority Presentation | 8 | localized wording, priority, fallback interaction and safe error text |
| F — Evidence / Defect Closure | 2 | raw evidence integrity and defect closure |
| Total | 63 | localization delta only |

Removed from formal manual certification: real Correction/Restore/Emergency Restore transactions, DB replacement checks, atomicity, correction supersession, persistence semantics, recovery business-state semantics, and repeated destructive transaction paths. The new guide still uses real production UI and isolated prepared fixtures for presentation-only observation where needed.

## Retained coverage

- Formal geometry is 2560×1600 at 150% only, with representative default/minimum/maximized coverage where localized text can affect layout.
- All 12 frozen contexts are human-traceable: AppShell, Round, Analysis, Maintenance, Correction, Restore, Recovery, StartupSafety, Errors, Characters, DomainLabels, and Localization.
- All 34 zh_CN character mappings are in C-ZH-02, including `???`, `堕化???`, long Tainted names, and `雅各和以扫`.
- Complete lifecycle/fallback core remains mandatory except only safely impractical settings-read and degraded-Qt cases, which remain N/A_ALLOWED and require precise Step 6 evidence.
- Localization-sensitive safety/priority coverage remains mandatory: Recovery/Data Safety priority, ALREADY_RUNNING, Emergency fallback, bilingual expected/unexpected errors, error-over-warning, and translated warning presentation.

## Existing evidence policy

Existing raw Session A English screenshots are preserved and deterministically indexed in `localization_step7_manual_evidence_carry_forward.md`. They may support future human review but remain `NOT_YET_TRANSFERRED`; no automatic PASS is created. The fixture-mismatch observation remains non-formal, non-defect evidence.

## Files modified

- `outputs/localization_step7_manual_checklist.md`
- `outputs/localization_step7_execution_guide.md`
- `outputs/localization_step7_scenario_manifest.md`
- `tools/localization_step7_prepare.py`

## Files added

- `outputs/localization_step7_localization_delta_rebaseline_report.md`
- `outputs/localization_step7_localization_delta_rebaseline_validation.md`
- `outputs/localization_step7_manual_evidence_carry_forward.md`

## Files deleted

None.

Production changes = 0. Step 7 manual execution remains paused pending external review. Step 8 and Step 9 were not started.
