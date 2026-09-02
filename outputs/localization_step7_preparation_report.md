# Localization Step 7 Preparation Report

## A. Scope

This was preparation only for future human `Localization Step 7 — Manual UI Acceptance`.

Status at handoff: `MANUAL ACCEPTANCE NOT STARTED`.

No screenshot was captured, no visual judgment was made, no checklist row was marked PASS, and Step 7 was not self-accepted.

## B. Files

### Modified

- none

No pre-existing file was modified by Step 7 preparation. In particular, no file under `src\`, no official TS, no schema/spec/dependency/packaging/version file, and no accepted Step 3–6 test/report file changed.

### Added — durable preparation files

- `outputs\localization_step7_manual_checklist.md` — formal 227-row manual checklist; all rows NOT_RUN.
- `outputs\localization_step7_defects.md` — empty defect ledger and routing rules.
- `outputs\localization_step7_execution_guide.md` — Sessions A–F, exact launch/actions, DPI handling, evidence filenames, and human decision instructions.
- `outputs\localization_step7_scenario_manifest.md` — per-scenario state, commands, supported IDs, injection classification, and safety notes.
- `outputs\localization_step7_preparation_report.md` — this A–K preparation report.
- `outputs\localization_step7_preparation_validation.md` — literal commands, results, regressions, protected hashes, and retained development failures.
- `tools\localization_step7_prepare.py` — test/manual-QA-only scenario compiler/preparer/launcher/prober with fixed-root guards.
- `outputs\localization_step7_manual\en\README.md` — states that English screenshots have not been collected.
- `outputs\localization_step7_manual\zh_CN\README.md` — states that zh_CN screenshots have not been collected.
- `outputs\localization_step7_manual\lifecycle\README.md` — states that lifecycle screenshots have not been collected.
- `outputs\localization_step7_manual\critical\README.md` — states that critical screenshots have not been collected.
- `outputs\localization_step7_manual\defects\README.md` — states that defect evidence has not been collected.

### Added — disposable runtime files (exact inventory: 111)

- `outputs\localization_step7_runtime\_qa_artifacts\fresh_production_extraction.ts` — fresh lupdate extraction audit artifact.
- `outputs\localization_step7_runtime\_qa_artifacts\step7_qa_probability_calibration_tool_zh_CN.qm` — strict Step 7 QA QM with a deliberately noncanonical pool filename.
- `outputs\localization_step7_runtime\_qa_artifacts\qa_qm_identity.json` — QA QM hash/size/225-of-225 identity.
- `outputs\localization_step7_runtime\_qa_artifacts\schema_gate.db` — disposable schema validation database.
- `outputs\localization_step7_runtime\already_running\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\already_running\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\already_running\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\backup_warning\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\backup_warning\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\backup_warning\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\backup_warning\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\confirm_pack_loss\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\confirm_pack_loss\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\confirm_pack_loss\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\confirm_pack_loss\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\correction\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\correction\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\correction\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\correction\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\corrupt_pack\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\corrupt_pack\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\corrupt_pack\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\corrupt_pack\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\data_safety\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\data_safety\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\data_safety\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\data_safety\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\emergency_invalid\localappdata\ProbabilityCalibrationTool\backups\recent\recent_20260901T120000.000000Z_emergency-good-0001.db` — isolated verified restore candidate.
- `outputs\localization_step7_runtime\emergency_invalid\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\emergency_invalid\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\emergency_invalid\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\emergency_invalid\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\emergency_missing_pack\localappdata\ProbabilityCalibrationTool\backups\recent\recent_20260901T120000.000000Z_emergency-good-0001.db` — isolated verified restore candidate.
- `outputs\localization_step7_runtime\emergency_missing_pack\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\emergency_missing_pack\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\emergency_missing_pack\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\emergency_restore\localappdata\ProbabilityCalibrationTool\backups\recent\recent_20260901T120000.000000Z_emergency-good-0001.db` — isolated verified restore candidate.
- `outputs\localization_step7_runtime\emergency_restore\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\emergency_restore\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\emergency_restore\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\emergency_restore\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\healthy_en\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\healthy_en\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\healthy_en\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\healthy_en\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\healthy_zh\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\healthy_zh\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\healthy_zh\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\healthy_zh\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\invalid_preference\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\invalid_preference\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\invalid_preference\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\invalid_preference\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\lifecycle\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\lifecycle\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\lifecycle\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\lifecycle\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\missing_pack\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\missing_pack\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\missing_pack\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\multiple_pending\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\multiple_pending\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\multiple_pending\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\multiple_pending\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\README.md` — disposable runtime boundary and safety notice.
- `outputs\localization_step7_runtime\recovery_localization_fallback\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\recovery_localization_fallback\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\recovery_localization_fallback\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\recovery_no_pending\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\recovery_no_pending\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\recovery_no_pending\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\recovery_no_pending\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\recovery\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\recovery\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\recovery\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\recovery\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\restore_corrupt\localappdata\ProbabilityCalibrationTool\backups\recent\recent_20260901T120000.000000Z_corrupt-0001.db` — intentional corrupt recognized backup fixture.
- `outputs\localization_step7_runtime\restore_corrupt\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\restore_corrupt\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\restore_corrupt\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\restore_corrupt\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\restore_invalid\localappdata\ProbabilityCalibrationTool\backups\recent\recent_20260901T120000.000000Z_state-b-0001.db` — isolated verified restore candidate.
- `outputs\localization_step7_runtime\restore_invalid\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\restore_invalid\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\restore_invalid\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\restore_invalid\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\restore_normal\localappdata\ProbabilityCalibrationTool\backups\recent\recent_20260901T120000.000000Z_state-b-0001.db` — isolated verified restore candidate.
- `outputs\localization_step7_runtime\restore_normal\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\restore_normal\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\restore_normal\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\restore_normal\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\save_failure\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\save_failure\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\save_failure\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\save_failure\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\unexpected_en\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\unexpected_en\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\unexpected_en\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\unexpected_en\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\unexpected_zh\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\unexpected_zh\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm` — audited scenario-local QA language pack.
- `outputs\localization_step7_runtime\unexpected_zh\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\unexpected_zh\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\wrong_filename\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\wrong_filename\localappdata\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.WRONG.qm` — intentional language-pack discovery fixture.
- `outputs\localization_step7_runtime\wrong_filename\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\wrong_filename\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.
- `outputs\localization_step7_runtime\wrong_location\localappdata\ProbabilityCalibrationTool\data\probability.db` — isolated live SQLite scenario fixture.
- `outputs\localization_step7_runtime\wrong_location\localappdata\ProbabilityCalibrationTool\probability_calibration_tool_zh_CN.qm` — language-pack discovery fixture.
- `outputs\localization_step7_runtime\wrong_location\localappdata\ProbabilityCalibrationTool\settings.ini` — isolated preferred-language setting.
- `outputs\localization_step7_runtime\wrong_location\scenario.json` — machine-readable scenario identity, paths, commands, and fixture evidence.

### Deleted

- none

The intentionally absent `outputs\localization_step7_completion_report.md` was not created.

## C. Real application entrypoint

Canonical production development entrypoint:

```powershell
$env:PYTHONPATH='src'; $env:LOCALAPPDATA=(Resolve-Path 'outputs\localization_step7_runtime\healthy_en\localappdata').Path; uv run python -m probability_calibration_tool
```

`src\probability_calibration_tool\__main__.py` delegates to the real production bootstrap. The explicit `PYTHONPATH=src` is required by the repository's src layout. The only isolation override is process-local `LOCALAPPDATA`, which existing production `AppPaths.from_local_appdata()` resolves to:

`outputs\localization_step7_runtime\<scenario>\localappdata\ProbabilityCalibrationTool`

Ordinary cases use this real module command. Only the declared fault cases use the test-only tool launcher, which composes the real production bootstrap/session/windows after inserting one narrow seam.

## D. Manual runtime isolation

The approved disposable root is `outputs\localization_step7_runtime\`. It is physically separate from `outputs\localization_step7_manual\` evidence storage.

Every scenario has its own `localappdata\ProbabilityCalibrationTool`, database, settings, languages, backups, logs, and runtime directories. The final prepared tree has 26 scenario roots and no startup-generated log/lock files; those will appear only when a future human launches a scenario.

Safety controls:

- fixed scenario-name allowlist; no arbitrary path argument;
- resolved target must be an immediate child of the approved runtime root;
- original real default `%LOCALAPPDATA%\ProbabilityCalibrationTool` is frozen at tool startup and explicitly rejected;
- links/junctions/reparse targets are rejected before recursive reset;
- recursive deletion is limited to one whitelisted scenario;
- mutation actions are whitelisted per scenario and exact target;
- no network access;
- production never imports this tool.

## E. Official QM

- official TS: `translations\probability_calibration_tool_zh_CN.ts`
- TS SHA-256: `82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257`
- fresh extraction: 225 active units, 12 contexts, missing 0, extra 0
- strict lrelease: 225 finished, 0 unfinished
- direct QTranslator: loaded, nonempty, exact 225/225
- QA QM size: 19,429 bytes
- QA QM SHA-256: `712747514fccce8f3f5e610dbdddf07187f9167b22d33365f97ca06a4d9b5547`
- PySide6: 6.11.2
- Qt: 6.11.2

The QA artifact pool uses the deliberately noncanonical filename `step7_qa_probability_calibration_tool_zh_CN.qm`. The production canonical filename is assigned only when copied into an intended scenario's real `languages\` directory, apart from the explicit wrong-location/wrong-filename discovery fixtures. It is a Step 7 QA artifact, not a Step 8 distribution artifact.

## F. Prepared scenarios

- `healthy_en` — English healthy UI plus valid/insufficient/no-history data.
- `healthy_zh` — zh_CN healthy UI using the audited canonical QM.
- `lifecycle` — EN↔zh_CN save/exit/restart lifecycle.
- `missing_pack` — preferred zh_CN with missing pack and later no-preference-change restoration.
- `corrupt_pack` — corrupt canonical QM fallback.
- `wrong_filename` — valid QM with wrong filename.
- `wrong_location` — valid QM in wrong directory.
- `invalid_preference` — unsupported preference preserved until explicit repair.
- `confirm_pack_loss` — confirm-time pack disappearance.
- `save_failure` — real Language dialog with isolated writer failure.
- `recovery` — single valid pending round and snapshot.
- `recovery_no_pending` — pending removed only after Recovery page is shown.
- `recovery_localization_fallback` — Recovery with preferred zh_CN/missing pack.
- `multiple_pending` — deterministic two-pending fail-closed fixture.
- `data_safety` — recognized DB with required snapshot removed.
- `already_running` — two real processes on one isolated root.
- `correction` — one completed correction candidate and no pending.
- `restore_normal` — live A with two completed vs verified B with one.
- `restore_invalid` — Normal Restore candidate removable after selection.
- `restore_corrupt` — recognized corrupt candidate excluded from verified list.
- `emergency_restore` — damaged live DB plus verified healthy candidate.
- `emergency_invalid` — Emergency candidate removable after selection.
- `emergency_missing_pack` — Emergency plus preferred zh_CN/missing pack.
- `unexpected_en` — real EN safe-error path from RoundService seam.
- `unexpected_zh` — real zh_CN safe-error path from RoundService seam.
- `backup_warning` — real committed operation plus Recent-backup warning seam.

All Correction and Restore transactions remain unexecuted; the human will perform them through the real GUI later.

## G. Checklist

| Prefix | Rows | MANDATORY | N/A_ALLOWED | Result at preparation handoff |
|---|---:|---:|---:|---|
| ENV | 7 | 7 | 0 | all NOT_RUN |
| EN | 46 | 46 | 0 | all NOT_RUN |
| ZH | 68 | 68 | 0 | all NOT_RUN |
| LC | 45 | 41 | 4 | all NOT_RUN |
| CR | 61 | 57 | 4 | all NOT_RUN |
| Total | 227 | 219 | 8 | 227 NOT_RUN |

Contract/checklist ID comparison: contract unique 227; checklist unique 227; missing 0; extra 0.

The eight `N/A_ALLOWED` rows are not marked N/A. A future human/external reviewer must provide the required three-part rationale before choosing N/A.

## H. Fault injection

Test-only fault seams:

- `save_failure`: after real production localization initialization, replace only `LocalizationContext._settings_factory`; real reads remain, a no-write writer reports `QSettings.AccessError`, and the real production `LanguageDialog` renders the failure. Enables LC-54/55.
- `unexpected_en` and `unexpected_zh`: after the real `DesktopHost` creates its real session/window, replace only the concrete `RoundService.calculate` instance with a deterministic private `RuntimeError`. Production GUI boundary and `report_unexpected` remain authoritative. Enables CR-UNX-01–05.
- `backup_warning`: replace only `BackupService.create(RECENT)` with an isolated `OSError`; the real business transaction and nonfatal coordinator run. Enables CR-BK-01/02.

Every fault launch prints `TEST-ONLY MANUAL QA FAULT INJECTION` and the exact seam. No substitute UI, expected-text replacement, production import, or packaging hook exists.

Ordinary environment/file mutations (pack removal/restoration, pending removal after Recovery appears, selected candidate expiry) are isolated fixtures, not production fault launchers.

## I. Evidence structure

Created:

- `outputs\localization_step7_manual\en\`
- `outputs\localization_step7_manual\zh_CN\`
- `outputs\localization_step7_manual\lifecycle\`
- `outputs\localization_step7_manual\critical\`
- `outputs\localization_step7_manual\defects\`

Only README placeholders exist. No screenshot evidence exists.

The execution guide specifies project-relative filenames. Future evidence must be an original Windows screenshot with enough page context, no AI modification, and no defect-concealing crop. Annotated copies must remain separate.

## J. Validation

Automated preparation gates:

- official TS hash unchanged;
- fresh extraction 225 active / 12 contexts / missing 0 / extra 0;
- strict lrelease 225 finished / 0 unfinished;
- QTranslator exact 225/225;
- scenario safety/reset/prepare/mutation probes passed;
- 26 isolated roots built;
- healthy EN/zh_CN real-entrypoint offscreen launch smoke passed;
- representative Recovery/Correction/Normal Restore/Emergency fixture probes passed;
- unexpected EN/zh_CN, generic save failure, and backup-warning launch smokes passed;
- real LanguageDialog save-failure probe preserved preference;
- Step 6-specific: 29 passed;
- localization architecture/static: 44 passed;
- all localization: 327 passed;
- full suite: 1340 passed;
- failed/errors/skipped/xfailed/xpassed: 0/0/0/0/0;
- schema: user_version 1; exact six tables; no localization business columns;
- `uv run ruff check .`: passed;
- `uv run ruff format --check .`: passed, 245 files formatted;
- `git diff --check`: passed;
- protected scope: before 182, after 182, missing/added/changed 0/0/0.

The validation report preserves all preparation-command/tooling failures and their corrections. No frozen production defect was found.

Preparation environment observation: raw Windows fields reported `Windows 10 Pro / Professional / 2009 / build 26200`; active display reported 2560×1600; current AppliedDPI was 144 (150%); PySide6/Qt were 6.11.2. These observations do not execute the formal manual matrix.

## K. Boundary

- Manual visual acceptance was not performed.
- Zero Step 7 visual PASS claims were made.
- All 227 checklist results remain NOT_RUN.
- No screenshot was fabricated or captured as formal evidence.
- No final Step 7 completion report was created.
- Production code did not change.
- Official TS, schema, SPEC, dependencies, lockfile, packaging, installer, and version did not change.
- Step 8 was not started.
- Step 9 was not started.
- No distribution artifact, GitHub Release, commit, tag, push, reset, or checkout was created or executed.

STEP 7 MANUAL ACCEPTANCE PREPARATION COMPLETE — READY FOR EXTERNAL PREPARATION REVIEW
