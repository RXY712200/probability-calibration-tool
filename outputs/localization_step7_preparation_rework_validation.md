# Localization Step 7 Manual Acceptance Preparation Narrow Rework Validation

Status: `STEP 7 MANUAL ACCEPTANCE PREPARATION NARROW REWORK COMPLETE — READY FOR EXTERNAL RE-REVIEW`

All commands ran from the project root. Offscreen launches below validate mechanics only; they are not human visual acceptance and never set a checklist result.

## QA artifact

Commands:

```powershell
uv run python tools/localization_step7_prepare.py compile-qm
$target=(Resolve-Path -LiteralPath 'outputs/localization_step7_runtime/_qa_artifacts/fresh_production_extraction.ts').Path
$approved=(Resolve-Path -LiteralPath 'outputs/localization_step7_runtime/_qa_artifacts').Path
if([IO.Path]::GetDirectoryName($target) -ne $approved){throw 'Fresh extraction target escaped QA artifacts.'}
Remove-Item -LiteralPath $target
uv run pyside6-lupdate -extensions py src -ts outputs/localization_step7_runtime/_qa_artifacts/fresh_production_extraction.ts
uv run python -c "import xml.etree.ElementTree as E; from pathlib import Path; key=lambda p:{(c.findtext('name'),m.findtext('source') or '',m.get('numerus','')) for c in E.parse(p).getroot().findall('context') for m in c.findall('message') if (m.find('translation') is None or m.find('translation').get('type') not in {'obsolete','vanished'})}; a=key(Path('translations/probability_calibration_tool_zh_CN.ts')); b=key(Path('outputs/localization_step7_runtime/_qa_artifacts/fresh_production_extraction.ts')); contexts={x[0] for x in b}; print({'official_active':len(a),'production_active':len(b),'contexts':len(contexts),'missing':len(a-b),'extra':len(b-a)}); raise SystemExit(0 if len(a)==len(b)==225 and len(contexts)==12 and a==b else 1)"
```

Results:

- official TS SHA-256: `82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257` (unchanged)
- fresh lupdate: 225 source texts, 225 new, 0 existing
- official active: 225
- fresh production active: 225
- contexts: 12
- missing: 0
- extra: 0
- strict lrelease: 225 finished / 0 unfinished
- QTranslator: loaded=true, nonempty, exact 225/225
- QA QM: 19,429 bytes
- QA QM SHA-256: `712747514fccce8f3f5e610dbdddf07187f9167b22d33365f97ca06a4d9b5547`

## Preparation tool static and help

Commands:

```powershell
uv run python -m py_compile tools/localization_step7_prepare.py
uv run python tools/localization_step7_prepare.py --help
uv run ruff check tools/localization_step7_prepare.py
uv run ruff format --check tools/localization_step7_prepare.py
```

Final results: all exit 0; Ruff check passed; tool format check passed; help lists compile-qm, prepare, reset, show, launch, probe, smoke-launch, mutate, safety-check, traceability-check, and probe-save-failure.

## Safety self-test

Command:

```powershell
uv run python tools/localization_step7_prepare.py safety-check
$env:LOCALAPPDATA=(Resolve-Path 'outputs/localization_step7_runtime/healthy_en/localappdata').Path
uv run python tools/localization_step7_prepare.py show healthy_en
```

Result: exit 0.

```text
unknown_name_rejected=true
unauthorized_mutation_rejected=true
runtime_is_project_controlled=true
scenario_reparse_escape_rejected=true
nested_languages_reparse_rejected=true
nested_backup_reparse_rejected=true
nested_data_reparse_rejected=true
qa_artifact_reparse_escape_rejected=true
reparse_mechanism=junction
```

The disposable self-test root was removed after the checks. The real user application root was never a self-test target.

The final overridden-environment probe also exited 0 and returned the controlled `healthy_en` paths. This proves a shell-level scenario `LOCALAPPDATA` override does not replace the independently discovered real-default-root guard.

## Scenario preparation and state probes

Commands:

```powershell
uv run python tools/localization_step7_prepare.py prepare all
$new=@('recovery_zh','recovery_no_pending_zh','multiple_pending_zh','data_safety_en','data_safety','data_safety_fallback','data_safety_warning_en','data_safety_warning_zh','correction_en','restore_normal_en','unexpected_warning_en','unexpected_warning_zh')
foreach($scenario in $new){ uv run python tools/localization_step7_prepare.py probe $scenario; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE} }
$additional=@('recovery_stale_en','recovery_stale_zh','correction_warning_en','correction_warning_zh','over_retention_en','over_retention_zh','quarantine_warning_en','quarantine_warning_zh')
foreach($scenario in $additional){ uv run python tools/localization_step7_prepare.py probe $scenario; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE} }
```

Results:

- 45 declared scenarios / 45 prepared scenario roots.
- missing scenarios: 0; extra scenarios: 0; scenario.json spec mismatches: 0.
- `recovery_zh`, `recovery_no_pending_zh`: ready_recovery, preferred=zh_CN, valid pack, one pending/one snapshot.
- `multiple_pending_zh`: recovery_error, preferred=zh_CN, valid pack, two pending/two snapshots.
- `data_safety_en`, `data_safety`, `data_safety_fallback`, `data_safety_warning_en`, `data_safety_warning_zh`: data_safety_error.
- `data_safety_fallback`: preferred=zh_CN, pack=missing, Effective=en by frozen fallback behavior.
- `correction_en`, `restore_normal_en`, `unexpected_warning_en`, `unexpected_warning_zh`: ready_draft with the expected preference/pack/fixture.
- `recovery_stale_en` / `recovery_stale_zh`: ready_recovery with one pending row and one snapshot before the reversible mutation.
- `correction_warning_en` / `correction_warning_zh`: ready_draft with a real correction candidate.
- `over_retention_en` / `over_retention_zh` and `quarantine_warning_en` / `quarantine_warning_zh`: ready_draft with the matching effective language.
- all commands exit 0.

## Reversible mutations

Commands:

```powershell
uv run python tools/localization_step7_prepare.py mutate recovery_no_pending_zh remove-pending
uv run python tools/localization_step7_prepare.py prepare recovery_no_pending_zh
uv run python tools/localization_step7_prepare.py probe recovery_no_pending_zh
uv run python tools/localization_step7_prepare.py prepare confirm_pack_loss
uv run python tools/localization_step7_prepare.py mutate confirm_pack_loss remove-pack
uv run python tools/localization_step7_prepare.py prepare confirm_pack_loss
uv run python tools/localization_step7_prepare.py prepare missing_pack
uv run python tools/localization_step7_prepare.py mutate missing_pack restore-pack
uv run python tools/localization_step7_prepare.py prepare missing_pack
uv run python tools/localization_step7_prepare.py prepare restore_invalid
uv run python tools/localization_step7_prepare.py mutate restore_invalid expire-candidate
uv run python tools/localization_step7_prepare.py prepare restore_invalid
uv run python tools/localization_step7_prepare.py prepare emergency_invalid
uv run python tools/localization_step7_prepare.py mutate emergency_invalid expire-candidate
uv run python tools/localization_step7_prepare.py prepare emergency_invalid
uv run python tools/localization_step7_prepare.py prepare recovery_no_pending
uv run python tools/localization_step7_prepare.py mutate recovery_no_pending remove-pending
uv run python tools/localization_step7_prepare.py prepare recovery_no_pending
uv run python tools/localization_step7_prepare.py mutate recovery_stale_en remove-recovery-snapshot
uv run python tools/localization_step7_prepare.py prepare recovery_stale_en
uv run python tools/localization_step7_prepare.py mutate recovery_stale_zh remove-recovery-snapshot
uv run python tools/localization_step7_prepare.py prepare recovery_stale_zh
```

All mutations exit 0 and affect only their allowlisted isolated target. Every mutated fixture was immediately rebuilt. Final `prepare all` restored the entire runtime tree to launch-ready initial state.

## Real-entrypoint and fault smoke

Command:

```powershell
$smokes=@('recovery_zh','recovery_no_pending_zh','multiple_pending_zh','data_safety_en','data_safety','data_safety_fallback','data_safety_warning_en','data_safety_warning_zh','correction_en','restore_normal_en','unexpected_warning_en','unexpected_warning_zh','save_failure','unexpected_en','unexpected_zh','backup_warning')
foreach($scenario in $smokes){ uv run python tools/localization_step7_prepare.py smoke-launch $scenario; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE} }
$additional=@('recovery_stale_en','recovery_stale_zh','correction_warning_en','correction_warning_zh','over_retention_en','over_retention_zh','quarantine_warning_en','quarantine_warning_zh')
foreach($scenario in $additional){ uv run python tools/localization_step7_prepare.py smoke-launch $scenario; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE} }
uv run python tools/localization_step7_prepare.py probe-save-failure
```

Results:

- all 24 offscreen real-entrypoint/fault smokes exited 0.
- both Data Safety warning launches printed the test-only banner and `RuntimeContext.result.warnings+WarningCode.BACKUP_OVER_RETENTION`.
- both unexpected+warning launches printed the warning seam and `RoundService.calculate`.
- existing settings-save, unexpected EN/zh_CN, and Recent-backup fault launchers also exited 0.
- stale-Recovery EN/zh_CN ordinary launches, Correction-warning EN/zh_CN, over-retention EN/zh_CN, and quarantine EN/zh_CN launches exited 0 and printed their exact seam where fault-injected.
- save-failure probe used the real `LanguageDialog`, kept the dialog open, displayed the production failure message, and preserved preference `en` -> `en`.

## Checklist traceability gate

Command:

```powershell
uv run python tools/localization_step7_prepare.py traceability-check
```

Result: exit 0.

```text
checklist_rows=235
unique_ids=235
MANDATORY=227
N/A_ALLOWED=8
NOT_RUN=235
PASS=0
FAIL=0
selected N/A=0
mandatory_traceability=227/227
critical_bilingual=26/26
zh_dpi_effective_zh_CN=18/18
fallback_counted_as_zh_CN=0
CR-SAFE-03=data_safety+localization_fallback
CR-SAFE-04=data_safety+operational_warning; en+zh_CN
```

The gate uses the corrected 235-row contract, not the rejected 227-row prompt.

Final runtime inventory audit: 45 declared/prepared scenarios, 187 listed files, 187 unique paths, 187 actual files, missing=0, extra=0, scenario-spec mismatch=0, and no log/lock/daily/uv-cache/self-test residue.

## Regression

Step 6-specific:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest tests/localization/test_bilingual_business_parity.py tests/localization/test_bilingual_failure_parity.py tests/localization/test_localization_drift_guardrails.py -q
```

Final result: `29 passed in 4.27s`.

Architecture/static:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest tests/localization/test_architecture.py tests/localization/test_presentation_architecture.py tests/localization/test_localization_drift_guardrails.py -q
```

Final result: `44 passed in 3.12s`.

All localization:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest tests/localization -q
```

Final result: `327 passed in 23.45s`.

Full suite:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest
```

Final result: `1340 passed in 107.91s (0:01:47)`.

For every pytest command:

- failed: 0
- errors: 0
- skipped: 0
- xfailed: 0
- xpassed: 0

No tests were added, removed, skipped, xfailed, or weakened, so accepted totals remain unchanged.

## Schema

Command:

```powershell
$env:PYTHONPATH='src'
uv run python -c 'from pathlib import Path; from probability_calibration_tool.persistence.database import create_connection; from probability_calibration_tool.persistence.migrations import ensure_schema; path=Path(r"outputs/localization_step7_runtime/_qa_artifacts/schema_gate.db"); path.unlink(missing_ok=True); c=create_connection(path); ensure_schema(c); version=c.execute("PRAGMA user_version").fetchone()[0]; tables=tuple(r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type=''table'' AND name NOT LIKE ''sqlite_%'' ORDER BY name")); columns={t:tuple(r[1] for r in c.execute(f"PRAGMA table_info({t})")) for t in tables}; forbidden=sorted({n for names in columns.values() for n in names if n in {"language","locale","translation","localized"}}); print({"user_version":version,"tables":tables,"localization_columns":forbidden}); c.close(); raise SystemExit(0 if version==1 and tables==("character_stats","characters","history_regimes","meta","round_analysis_snapshots","rounds") and not forbidden else 1)'
```

Result: user_version=1; exact tables `character_stats`, `characters`, `history_regimes`, `meta`, `round_analysis_snapshots`, `rounds`; localization business columns=[].

## Static and Git whitespace

Commands:

```powershell
uv run ruff check .
uv run ruff format --check .
git diff --check
```

Final results:

- `uv run ruff check .`: exit 0, `All checks passed!`
- `uv run ruff format --check .`: exit 0, `247 files already formatted`
- `git diff --check`: exit 0, no output

## Protected scope and preserved records

Before/after protected digest for the captured 337-file source/non-localization-test/config set:

`5ebb494bf19d40f34dd0b98981667f2326c59898e3318d18a0a1bfcc23c808cf` -> `5ebb494bf19d40f34dd0b98981667f2326c59898e3318d18a0a1bfcc23c808cf`

Official TS before/after:

`82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257` -> `82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257`

Protected comparison:

- missing: 0
- added: 0
- changed: 0

`packaging/ProbabilityCalibrationTool.spec` and `packaging/pyinstaller_entry.py` remained clean relative to the same HEAD before and after; `installer/` is absent. No distribution was built.

Rejected first-attempt report hashes remained unchanged:

- `outputs/localization_step7_preparation_report.md`: `d5013f88ceb0fa793640019613c9accd876b20a8bb0640ddd5f66d1ec7d13a0a`
- `outputs/localization_step7_preparation_validation.md`: `a8677a68bb7852d5c3cb62e9bcce2b46e78b45b91f623abf9f4e359d500c3972`

## Validation failure history

1. The first tool format check correctly reported the newly edited tool needed formatting; `uv run ruff format tools/localization_step7_prepare.py` fixed it, and all final format checks pass.
2. The first safety self-test could not create a symlink under the current Windows token and its initial PowerShell fallback did not bind arguments. The fallback was replaced with a disposable directory junction. All eight final guard assertions pass, and the junction was removed.
3. The first fresh-extraction command found 225 existing entries because the rejected attempt's QA extraction still existed. After validating the exact QA path and deleting only that file, the final fresh run reported 225 new / 0 existing.
4. The overridden-`LOCALAPPDATA` guard probe caused `uv` itself (before Python startup) to create six cache files inside the isolated `healthy_en` local-app-data tree. No live user data was touched. Repreparing exactly `healthy_en`, followed by the final scenario rebuild, removed the cache and restored the final clean 187-file inventory.
5. The first final-inventory audit one-liner used Markdown backticks inside a PowerShell double-quoted argument, so PowerShell corrupted the regular expression before Python ran. The corrected stdin script used a literal line parser and proved 187 listed/unique/actual paths with zero missing or extra.

These were test-only preparation/tooling issues. No production defect or production change resulted.

## Boundary

- human visual acceptance: NOT performed
- all 235 rows: NOT_RUN
- screenshots judged PASS: 0
- Step 7 completion report: absent
- production code changes in this rework: 0
- Step 8: NOT started
- Step 9: NOT started
- commit/tag/push/reset/checkout/release/distribution build: none
