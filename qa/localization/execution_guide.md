# Localization Step 7 Localization-Delta Execution Guide

Status: `MANUAL ACCEPTANCE PAUSED — PENDING EXTERNAL REVIEW`

This guide implements the localization-delta contract in `manual_checklist.md`. It supersedes the prior 212-row broad manual route without rewriting its historical reports. It does not re-certify frozen Correction, Restore, Emergency Restore, persistence, atomicity, supersession, replacement, or recovery business semantics.

## 1. Safety and formal baseline

- Formal manual observation is only at **2560×1600 @ 150%**.
- Use only the isolated prepared runtime roots and the real application entrypoint.
- A row observes presentation, wording, geometry, language state, or priority. Do not execute a destructive business transaction merely to close a localization row.
- Record raw Windows screenshots; do not AI-edit or crop to conceal a defect. Human reviewers alone choose PASS, FAIL, or a justified N/A.

Common preparation:

```powershell
uv run python tools/localization_step7_prepare.py compile-qm
uv run python tools/localization_step7_prepare.py prepare all
uv run python tools/localization_step7_prepare.py show <scenario>
```

Ordinary real-app launch:

```powershell
$env:PYTHONPATH='src'
$env:LOCALAPPDATA=(Resolve-Path 'outputs\localization_step7_runtime\<scenario>\localappdata').Path
uv run python -m probability_calibration_tool
```

The rich healthy fixture is shared by English and zh_CN: Isaac is production-observed valid and statistically ready at 50W/50L; Magdalene is insufficient at 1W/0L; Cain has no eligible history.

## 2. Gate A — Environment & identity

Before any screenshot, record Windows identity, native display, 150% scaling, isolated root, English built-in identity, zh_CN official-QM identity, and TS/QM/Qt provenance. Do not treat preparation output as visual acceptance.

## 3. Gate B — English built-in regression

Use `healthy_en` for healthy Round, Analysis, Modify/Recalculate, Post-run presentation, Maintenance, Start New Regime, ordinary validation error, and keyboard spot checks. Use `correction_en` and `restore_normal_en` only to open their candidate/editor or confirmation UI, inspect at minimum practical geometry, and leave via Cancel/Back. Use `recovery` for representative Recovery presentation.

Existing raw Session A screenshots may be transferred by the carry-forward map; their existence never marks a row PASS. Preserve `EN_150_analysis_fixture_mismatch_observation.png` as a non-formal observation, not a product defect.

## 4. Gate C — official zh_CN presentation

Use `healthy_zh` for the Chinese identity/glyph scan, all 34 character mappings, Round, Analysis, Maintenance, terminology, leakage classification, and ordinary Unicode/keyboard checks. Use `correction` and `restore_normal` for presentation-only candidate/editor/confirmation checks; do not commit a Correction or Restore. Use `recovery_zh` or `data_safety` for representative Recovery/StartupSafety presentation.

For every observed English fragment, classify it as `INTENTIONAL_PRODUCT_NAME`, `INTENTIONAL_TECHNICAL_TOKEN`, `QT_OWNED`, or `DEFECT_APP_OWNED`. `Regime` must never appear as `模式`; Restore, Recovery, and Emergency Recovery must stay distinguishable.

## 5. Gate D — lifecycle and fallback

Use the dedicated isolated scenarios: `lifecycle`, `missing_pack`, `corrupt_pack`, `wrong_filename`, `wrong_location`, `invalid_preference`, `confirm_pack_loss`, and `save_failure`. For restart rows record `Launch 1 → action → process exit → Launch 2`; closing only a window is not sufficient. Use the explicitly permitted in-session pack mutation only where the scenario requires it. N/A_ALLOWED rows remain NOT_RUN unless a human later records the exact safety rationale and Step 6 evidence.

## 6. Gate E — safety and priority presentation

Use prepared abnormal/fault-injected fixtures only for real production UI presentation: `recovery_localization_fallback`, `data_safety_en`, `data_safety`, `data_safety_fallback`, `data_safety_warning_en`, `data_safety_warning_zh`, `already_running`, `emergency_missing_pack`, `unexpected_en`, `unexpected_zh`, `unexpected_warning_en`, `unexpected_warning_zh`, and `backup_warning`. For E-SP-02, observe `data_safety_fallback` for Data Safety over the localization fallback notice, plus `data_safety_warning_en` and `data_safety_warning_zh` for Data Safety over an ordinary warning in both applicable languages. These rows verify translated wording, priority, fallback interaction, and safe public error text. They do not re-prove transaction semantics.

## 7. Gate F — evidence and closure

One raw screenshot may support several rows. Classify defects BLOCKER, HIGH, MEDIUM, or LOW. No BLOCKER/HIGH may remain unresolved; a production/localization repair requires the affected Step 6 regression rerun. Preparation code must never select a human result.

## Appendix A - Formal checklist traceability

Each route is either a real prepared scenario or the approved `ENVIRONMENT` identity route. Contexts are real production localization contexts observed by the listed human route.

| ID | Route | Human observation / evidence route | Contexts |
|---|---|---|---|
| A-ENV-01 | ENVIRONMENT | Windows identity record | — |
| A-ENV-02 | ENVIRONMENT | Native display record | — |
| A-ENV-03 | ENVIRONMENT | 2560×1600 @ 150% record | — |
| A-ENV-04 | healthy_en | Built-in English identity | Localization |
| A-ENV-05 | healthy_zh | Official zh_CN identity | Localization |
| A-ENV-06 | ENVIRONMENT | TS/QM and Qt provenance | Localization |
| A-ENV-07 | ENVIRONMENT | Isolated-root record | — |
| B-EN-01 | healthy_en | Startup screenshot | AppShell |
| B-EN-02 | healthy_en | Round default/minimum screenshot | Round; Characters |
| B-EN-03 | healthy_en | Locked valid-history Analysis screenshot | Analysis; DomainLabels |
| B-EN-04 | healthy_en | Three history-variant screenshots | Analysis; DomainLabels |
| B-EN-05 | healthy_en | Analysis default/minimum/maximized screenshots | Analysis |
| B-EN-06 | healthy_en | Modify/Recalculate presentation screenshot | Round; Analysis |
| B-EN-07 | healthy_en | Confirmation and New Round screenshot | Round |
| B-EN-08 | healthy_en | Maintenance default/minimum screenshot | Maintenance |
| B-EN-09 | healthy_en | Start New Regime editor screenshot | Maintenance |
| B-EN-10 | correction_en | Candidate/editor then Cancel/Back screenshot | Correction |
| B-EN-11 | restore_normal_en | Candidate/confirmation then Cancel/Back screenshot | Restore |
| B-EN-12 | healthy_en + recovery | Ordinary validation-error and Recovery screenshots | Recovery; Errors |
| B-EN-13 | healthy_en | Keyboard notes screenshot | AppShell |
| B-EN-14 | correction_en | Administrative minimum-practical screenshot | Correction |
| B-EN-15 | healthy_en | Built-in English readable screenshot | AppShell |
| C-ZH-01 | healthy_zh | Official-QM glyph/mixed-script screenshot | AppShell; Localization |
| C-ZH-02 | healthy_zh | All 34 character buttons screenshot | Characters |
| C-ZH-03 | healthy_zh | Round default/minimum screenshot | Round |
| C-ZH-04 | healthy_zh | Valid-history dynamic Analysis screenshot | Analysis; DomainLabels |
| C-ZH-05 | healthy_zh | Three history-variant screenshots | Analysis; DomainLabels |
| C-ZH-06 | healthy_zh | Analysis default/minimum/maximized screenshots | Analysis |
| C-ZH-07 | healthy_zh | Maintenance default/minimum screenshot | Maintenance |
| C-ZH-08 | correction | Candidate/editor and Unicode-input screenshot | Correction |
| C-ZH-09 | restore_normal | Candidate/confirmation screenshot | Restore |
| C-ZH-10 | recovery_zh | Minimum-practical Recovery screenshot | Recovery |
| C-ZH-11 | healthy_zh + correction + restore_normal + recovery_zh | Terminology evidence sheet | Round; Maintenance; Correction; Restore; Recovery; DomainLabels |
| C-ZH-12 | healthy_zh | English-fragment classification notes | AppShell; Errors |
| C-ZH-13 | correction | Chinese Unicode and keyboard notes | Correction |
| C-ZH-14 | healthy_zh + correction + restore_normal + recovery_zh + data_safety | Context observation index | AppShell; Round; Analysis; Maintenance; Correction; Restore; Recovery; StartupSafety; Errors; Characters; DomainLabels; Localization |
| C-ZH-15 | healthy_zh | Long-label/wrapping screenshot | Round; Analysis |
| D-LC-01 | lifecycle | Healthy English dialog screenshot | Localization |
| D-LC-02 | lifecycle | EN to zh_CN restart evidence | Localization |
| D-LC-03 | lifecycle | zh_CN to EN restart evidence | Localization |
| D-LC-04 | lifecycle | No-op/Cancel/Esc/X evidence | Localization |
| D-LC-05 | lifecycle | Explicit English default persistence evidence | Localization |
| D-LC-06 | missing_pack | Missing-pack fallback screenshot | Localization; StartupSafety |
| D-LC-07 | missing_pack | Restored-pack restart evidence | Localization |
| D-LC-08 | corrupt_pack | Corrupt-pack fallback screenshot | Localization |
| D-LC-09 | wrong_filename + wrong_location | Discovery fallback screenshots | Localization |
| D-LC-10 | invalid_preference | Invalid-preference fallback screenshot | Localization |
| D-LC-11 | ENVIRONMENT | Safe route or Step 6 N/A evidence | Localization |
| D-LC-12 | confirm_pack_loss | Confirm-time disappearance screenshot | Localization |
| D-LC-13 | save_failure | Save-failure dialog screenshot | Localization; Errors |
| D-LC-14 | ENVIRONMENT | Safe route or Step 6 N/A evidence | Localization |
| D-LC-15 | healthy_zh | Healthy QTranslator record | Localization |
| D-LC-16 | missing_pack | Once-per-process notice/dismissal screenshot | Localization; StartupSafety |
| E-SP-01 | recovery_localization_fallback | Recovery-over-notice screenshot | Recovery; Localization |
| E-SP-02 | data_safety_en + data_safety + data_safety_fallback + data_safety_warning_en + data_safety_warning_zh | Data Safety-over-fallback-notice and bilingual Data Safety-over-warning screenshots | StartupSafety; Errors; Localization |
| E-SP-03 | already_running | Second-instance suppression screenshot | StartupSafety; Localization |
| E-SP-04 | emergency_missing_pack | Emergency-over-fallback screenshot | StartupSafety; Localization |
| E-SP-05 | correction_en + correction | Bilingual expected-error screenshot | Errors; Correction |
| E-SP-06 | unexpected_en + unexpected_zh | Bilingual safe unexpected-error screenshots | Errors |
| E-SP-07 | unexpected_warning_en + unexpected_warning_zh | Error-over-warning screenshots | Errors |
| E-SP-08 | backup_warning | zh_CN backup-warning screenshot | StartupSafety |
| F-EV-01 | ENVIRONMENT | Raw-evidence inventory | — |
| F-EV-02 | ENVIRONMENT | Defect ledger and closure record | — |

## Final human handoff rule

Manual execution remains paused pending external review. A later completed Step 7 result requires every mandatory row to be PASS or FAIL, any N/A to meet the checklist rationale rule, and the required defect closure. This preparation creates no completion report and makes no acceptance decision.
