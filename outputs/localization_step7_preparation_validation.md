# Localization Step 7 Preparation Validation

Status: `MANUAL ACCEPTANCE NOT STARTED`

All automated results below validate preparation mechanics or frozen regressions only. None is a visual/manual PASS.

## 1. Baseline and protected scope

Initial commands:

```powershell
git status --short
git rev-parse HEAD
```

Initial HEAD: `00bd24b9fdc509809962ace4412b1e233b7c6598`.

Initial status already contained the accepted, uncommitted/untracked Localization Steps 3–6 implementation and reports. Step 7 did not attribute those earlier changes to itself.

Protected hash capture/comparison command shape:

```powershell
$ErrorActionPreference='Stop'
$root=(Get-Location).Path
$protected=@()
$protected += Get-ChildItem -LiteralPath (Join-Path $root 'src') -Recurse -File
foreach($literal in @('SPEC_1.0.md','pyproject.toml','uv.lock')){
  $p=Join-Path $root $literal
  if(Test-Path -LiteralPath $p){$protected += Get-Item -LiteralPath $p}
}
foreach($dir in @('packaging','installer')){
  $p=Join-Path $root $dir
  if(Test-Path -LiteralPath $p){
    $protected += Get-ChildItem -LiteralPath $p -Recurse -File
  }
}
$protected += Get-Item -LiteralPath (Join-Path $root 'translations\probability_calibration_tool_zh_CN.ts')
foreach($file in ($protected|Sort-Object FullName -Unique)){
  $rel=[IO.Path]::GetRelativePath($root,$file.FullName).Replace('\','/')
  $hash=(Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash.ToLowerInvariant()
  "$rel`t$hash"
}
```

Exact comparison:

```json
{
  "before_count": 182,
  "after_count": 182,
  "missing": [],
  "added": [],
  "changed": [],
  "ts_hash": "82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257"
}
```

Protected scope result: PASS; missing/added/changed = 0/0/0.

## 2. Real entrypoint discovery

Commands:

```powershell
uv run python -c "import probability_calibration_tool, pathlib; print(pathlib.Path(probability_calibration_tool.__file__).resolve())"
Push-Location src
uv run python -c "import probability_calibration_tool, pathlib; print(pathlib.Path(probability_calibration_tool.__file__).resolve())"
Pop-Location
$env:PYTHONPATH='src'
uv run python -c "import probability_calibration_tool, pathlib; print(pathlib.Path(probability_calibration_tool.__file__).resolve())"
Remove-Item Env:PYTHONPATH
```

Results:

- Root command without `PYTHONPATH`: exit 1, `ModuleNotFoundError`.
- From `src`: exit 0 and resolved the real source package.
- Root with `PYTHONPATH=src`: exit 0 and resolved the real source package.
- Canonical real module: `python -m probability_calibration_tool`.
- Exact isolated launch form is recorded in the execution guide and each manifest row.

The failed root import was a preparation command-construction issue, not a production defect.

## 3. QA artifacts

Final fresh extraction:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pyside6-lupdate -extensions py src -ts outputs/localization_step7_runtime/_qa_artifacts/fresh_production_extraction.ts
uv run python -c "import xml.etree.ElementTree as E; from pathlib import Path; key=lambda p:{(c.findtext('name'),m.findtext('source') or '',m.get('numerus','')) for c in E.parse(p).getroot().findall('context') for m in c.findall('message') if (m.find('translation') is None or m.find('translation').get('type') not in {'obsolete','vanished'})}; a=key(Path('translations/probability_calibration_tool_zh_CN.ts')); b=key(Path('outputs/localization_step7_runtime/_qa_artifacts/fresh_production_extraction.ts')); contexts={x[0] for x in b}; print({'official_active':len(a),'production_active':len(b),'contexts':len(contexts),'missing':len(a-b),'extra':len(b-a)}); raise SystemExit(0 if len(a)==len(b)==225 and len(contexts)==12 and a==b else 1)"
```

Result:

```text
Found 225 source text(s) (225 new and 0 already existing)
official_active=225
production_active=225
contexts=12
missing=0
extra=0
```

Strict fresh QM:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run python tools/localization_step7_prepare.py compile-qm
```

The tool executes the equivalent strict compiler invocation:

```powershell
pyside6-lrelease translations\probability_calibration_tool_zh_CN.ts -qm outputs\localization_step7_runtime\_qa_artifacts\step7_qa_probability_calibration_tool_zh_CN.qm -fail-on-unfinished -fail-on-invalid
```

Result:

```text
Generated 225 translation(s) (225 finished and 0 unfinished)
QTranslator loaded=true
exact matches=225/225
official TS SHA-256=82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257
QA QM SHA-256=712747514fccce8f3f5e610dbdddf07187f9167b22d33365f97ca06a4d9b5547
QA QM size=19429
PySide6=6.11.2
Qt=6.11.2
```

QA artifact result: PASS. The QM is a Step 7 QA artifact, not a Step 8 distribution artifact.

## 4. Checklist contract

Command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run python -c "import re,pathlib; contract=pathlib.Path(r'C:\Users\rxy71\.codex\attachments\b0190862-7bc6-4954-84a1-696e8830906b\pasted-text.txt').read_text(encoding='utf-8'); checklist=pathlib.Path('outputs/localization_step7_manual_checklist.md').read_text(encoding='utf-8'); pat=r'(?<![A-Z0-9])(?:ENV|EN|ZH|LC|CR)-[A-Z0-9-]+(?=`|\s)'; expected=set(re.findall(pat,contract)); actual=set(re.findall(pat,checklist)); print({'contract_unique':len(expected),'checklist_unique':len(actual),'missing':sorted(expected-actual),'extra':sorted(actual-expected),'not_run_rows':sum(1 for line in checklist.splitlines() if line.startswith('| ') and ' | NOT_RUN | ' in line)}); raise SystemExit(0 if expected==actual and len(actual)==227 else 1)"
```

Result:

```text
contract_unique=227
checklist_unique=227
missing=[]
extra=[]
not_run_rows=227
```

Checklist result: PASS as a preparation contract. Manual result state remains NOT_RUN.

## 5. Manual tool syntax, lint, help, safety, and launch smoke

Final commands:

```powershell
uv run ruff format tools/localization_step7_prepare.py
uv run ruff check tools/localization_step7_prepare.py
uv run ruff format --check tools/localization_step7_prepare.py
$env:PYTHONDONTWRITEBYTECODE='1'
uv run python -c "import ast, pathlib; p=pathlib.Path('tools/localization_step7_prepare.py'); ast.parse(p.read_text(encoding='utf-8')); print('SYNTAX=PASS')"
uv run python tools/localization_step7_prepare.py --help
uv run python tools/localization_step7_prepare.py safety-check
uv run python tools/localization_step7_prepare.py probe-save-failure
foreach($scenario in @('healthy_en','healthy_zh','unexpected_en','unexpected_zh','save_failure','backup_warning')){
  uv run python tools/localization_step7_prepare.py smoke-launch $scenario
  if($LASTEXITCODE -ne 0){throw "final smoke failed: $scenario"}
}
```

Final results:

- syntax/help/import: PASS.
- tool Ruff lint/format: PASS.
- safety check: unknown scenario rejected; unauthorized mutation rejected; approved root proven project-controlled.
- healthy English real-entrypoint offscreen smoke: exit 0.
- healthy zh_CN real-entrypoint offscreen smoke: exit 0.
- unexpected EN/zh_CN launcher smoke: exit 0; printed test-only banner and `RoundService.calculate` seam.
- generic settings-save launcher smoke: exit 0; printed settings-writer seam.
- Recent-backup launcher smoke: exit 0; printed `BackupService.create(RECENT)` seam.
- real `LanguageDialog` save-failure probe displayed the frozen failure message, remained open, and preserved `en → en`.

The offscreen runs checked launch/injection mechanics only. They are not screenshots and are not visual PASS evidence.

## 6. Scenario reset, preparation, state, and reversible mutation smoke

Preparation:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run python tools/localization_step7_prepare.py prepare all
```

Result: 26 isolated scenario roots and 26 `scenario.json` files. Final rebuild left zero scenario log files and zero lock files. Runtime state is ready for future human launches.

Representative state probe command:

```powershell
$scenarios=@('healthy_en','healthy_zh','lifecycle','missing_pack','corrupt_pack','wrong_filename','wrong_location','invalid_preference','confirm_pack_loss','save_failure','recovery','recovery_localization_fallback','multiple_pending','data_safety','already_running','correction','restore_normal','restore_invalid','restore_corrupt','emergency_restore','emergency_invalid','emergency_missing_pack','unexpected_en','unexpected_zh','backup_warning')
foreach($scenario in $scenarios){
  uv run python tools/localization_step7_prepare.py probe $scenario
}
```

Observed dispositions:

- healthy/lifecycle/fallback/correction/restore/fault-prep scenarios: `ready_draft`.
- single pending Recovery scenarios: `ready_recovery`.
- multiple pending: `recovery_error`.
- missing required snapshot: `data_safety_error`.
- damaged live DB Emergency scenarios: `emergency_recovery`.
- pack states: valid→`valid`; absent/wrong filename/wrong location→`missing`; corrupt→`load_failed`.
- invalid preference remained `saved_invalid`.

Reset/mutation commands exercised:

```powershell
uv run python tools/localization_step7_prepare.py reset confirm_pack_loss
uv run python tools/localization_step7_prepare.py prepare confirm_pack_loss
uv run python tools/localization_step7_prepare.py mutate confirm_pack_loss remove-pack
uv run python tools/localization_step7_prepare.py prepare confirm_pack_loss
uv run python tools/localization_step7_prepare.py prepare missing_pack
uv run python tools/localization_step7_prepare.py mutate missing_pack restore-pack
uv run python tools/localization_step7_prepare.py prepare missing_pack
uv run python tools/localization_step7_prepare.py prepare recovery_no_pending
uv run python tools/localization_step7_prepare.py mutate recovery_no_pending remove-pending
uv run python tools/localization_step7_prepare.py prepare recovery_no_pending
uv run python tools/localization_step7_prepare.py prepare restore_invalid
uv run python tools/localization_step7_prepare.py mutate restore_invalid expire-candidate
uv run python tools/localization_step7_prepare.py prepare restore_invalid
uv run python tools/localization_step7_prepare.py prepare emergency_invalid
uv run python tools/localization_step7_prepare.py mutate emergency_invalid expire-candidate
uv run python tools/localization_step7_prepare.py prepare emergency_invalid
```

Results: reset target absent before reprepare; pack remove/restore verified; restored QM hash matched the audited hash; pending count became zero then scenario was rebuilt; selected-candidate files became absent then both scenarios were rebuilt. PASS.

Representative fixtures built and probed:

- healthy EN and healthy zh_CN rich history.
- one pending Recovery and Recovery+missing-pack.
- two-pending fail-closed fixture.
- Data Safety missing-snapshot fixture.
- Correction completed candidate.
- Normal Restore distinguishable live A/candidate B.
- corrupt/expired restore candidates.
- damaged live DB plus valid Emergency candidate.
- Emergency+missing-pack and expired Emergency candidate.
- unexpected EN/zh_CN and generic settings-save fault launchers.
- nonfatal Recent-backup warning launcher.

No real user root or data was read, reset, or mutated by the preparer.

## 7. Regression

Step 6-specific:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest tests/localization/test_bilingual_business_parity.py tests/localization/test_bilingual_failure_parity.py tests/localization/test_localization_drift_guardrails.py -q
```

Final result: `29 passed in 4.02s`.

Architecture/static:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest tests/localization/test_architecture.py tests/localization/test_presentation_architecture.py tests/localization/test_localization_drift_guardrails.py -q
```

Final result: `44 passed in 3.66s`.

All localization:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest tests/localization -q
```

Final result: `327 passed in 23.15s`.

Full suite:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest
```

Final result: `1340 passed in 103.40s (0:01:43)`.

No pytest tests were added, deleted, skipped, xfailed, or weakened. For every regression command:

- failed = 0
- errors = 0
- skipped = 0
- xfailed = 0
- xpassed = 0

## 8. Schema

Final command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONPATH='src'
uv run python -c 'from pathlib import Path; from probability_calibration_tool.persistence.database import create_connection; from probability_calibration_tool.persistence.migrations import ensure_schema; path=Path(r"outputs/localization_step7_runtime/_qa_artifacts/schema_gate.db"); path.unlink(missing_ok=True); c=create_connection(path); ensure_schema(c); version=c.execute("PRAGMA user_version").fetchone()[0]; tables=tuple(r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type=''table'' AND name NOT LIKE ''sqlite_%'' ORDER BY name")); columns={t:tuple(r[1] for r in c.execute(f"PRAGMA table_info({t})")) for t in tables}; forbidden=sorted({n for names in columns.values() for n in names if n in {"language","locale","translation","localized"}}); print({"user_version":version,"tables":tables,"localization_columns":forbidden}); c.close(); raise SystemExit(0 if version==1 and tables==("character_stats","characters","history_regimes","meta","round_analysis_snapshots","rounds") and not forbidden else 1)'
Remove-Item Env:PYTHONPATH
```

Result:

```text
user_version=1
tables=('character_stats','characters','history_regimes','meta','round_analysis_snapshots','rounds')
localization_columns=[]
```

Schema result: PASS.

## 9. Static and Git whitespace

Final exact commands:

```powershell
uv run ruff check .
uv run ruff format --check .
git diff --check
```

Results:

- `uv run ruff check .`: exit 0, `All checks passed!`.
- `uv run ruff format --check .`: exit 0, `245 files already formatted`.
- `git diff --check`: exit 0, no output.

## 10. Environment detected during preparation

Commands:

```powershell
Get-ComputerInfo | Select-Object WindowsProductName,WindowsEditionId,WindowsVersion,OsBuildNumber
Get-CimInstance Win32_VideoController | Select-Object Name,CurrentHorizontalResolution,CurrentVerticalResolution
Get-ItemProperty -LiteralPath 'HKCU:\Control Panel\Desktop\WindowMetrics' | Select-Object AppliedDPI
uv run python -c "import PySide6; from PySide6.QtCore import qVersion; print({'PySide6':PySide6.__version__,'Qt':qVersion()})"
```

Raw preparation observations:

- WindowsProductName=`Windows 10 Pro`; WindowsEditionId=`Professional`; WindowsVersion=`2009`; OsBuildNumber=`26200`.
- active NVIDIA adapter resolution=`2560×1600`; secondary AMD entry reported no current resolution.
- AppliedDPI=`144` (150% at observation time).
- PySide6=`6.11.2`; Qt=`6.11.2`.

These are preparation observations only; the future human must still execute and record the formal scaling matrix.

## 11. Development failure history

Preparation/tooling failures retained:

1. Root-level `uv run python -m probability_calibration_tool` initially failed with `ModuleNotFoundError`; adding the repository-required `PYTHONPATH=src` fixed the command. Production entrypoint was unchanged.
2. Initial tool Ruff reported import ordering, one simplification, and formatting issues. The test-only tool was corrected/formatted; no production file changed.
3. First fault-launcher smoke hung because the auto-exit timer was registered before `QApplication` existed. Process command lines were checked, and only the two verified Step 7 smoke PIDs were stopped. The timer moved into the injected event-loop callback; all final launcher smokes exited 0.
4. First save-failure probe was safely rejected because the guard compared against the already-overridden child-process `LOCALAPPDATA`. The tool now freezes the original default root at startup; final guard and dialog probes passed.
5. The first mutation smoke's SQLite count one-liner had PowerShell quoting that treated SQL `*` as a command. The already-isolated mutation was verified with corrected quoting, then the scenario was rebuilt. This was a validation-command error.
6. The first schema/static combined attempt omitted `PYTHONPATH=src`, so schema import did not execute; format check also found one new-tool line to reformat. After setting `PYTHONPATH` and formatting the test-only tool, schema and all static gates passed.
7. The first content/inventory audit used a PowerShell double-quoted Python one-liner; PowerShell consumed Markdown backticks and corrupted the regular expression before it ran. The final audit used a single-quoted, non-regex line parser and proved all 111 runtime files were listed exactly.

Frozen production defects discovered: none.

## 12. Git boundary

Final HEAD remains `00bd24b9fdc509809962ace4412b1e233b7c6598`.

No reset, checkout, commit, tag, push, release, or distribution build command was run. The working tree still includes the pre-existing accepted Steps 3–6 changes plus the exact Step 7 additions listed in the preparation report.

Manual visual acceptance was not performed. No Step 7 checklist row was marked PASS. Step 8 and Step 9 were not started.
