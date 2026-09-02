# Localization Step 3 — Validation Commands and Evidence

## Working directory and environment

All shell commands below ran in:

```text
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability
```

Windows/Python 3.13.14, pytest 9.1.1, PySide6/Qt 6.11.2. Source/document edits used apply_patch; no dependency, version, packaging, Git commit/tag, or release-build command was issued.

## Original implementation baseline before edits

```powershell
git status --short
uv run pytest
```

Status was empty. Baseline output:

```text
1013 passed in 115.88s (0:01:55)
```

Exit 0; failed/errors/skipped/xfailed/xpassed all 0.

## Existing locked Qt toolchain

```powershell
uv run pyside6-lrelease -version
uv run python -c "import sys, shutil, PySide6; from PySide6.QtCore import QLibraryInfo; print('python=' + sys.executable); print('PySide6=' + PySide6.__version__); print('lrelease=' + str(shutil.which('pyside6-lrelease'))); print('Qt translations=' + QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath))"
```

Observed output:

```text
lrelease version 6.11.2
python=C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\.venv\Scripts\python.exe
PySide6=6.11.2
lrelease=C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\.venv\Scripts\pyside6-lrelease.EXE
Qt translations=C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/.venv/Lib/site-packages/PySide6/translations
```

The compile_qm fixture independently checks this executable is under the repository venv and installed PySide6 equals the pyside6 package version in uv.lock. It calls that absolute executable with temporary TS and QM paths, not an unrelated PATH compiler. Missing/mismatched tooling is an assertion failure, never skip/xfail. No dependency was changed.

## Development validation, including unsuccessful runs

Literal commands issued during development:

```powershell
uv run ruff format src/probability_calibration_tool/localization.py src/probability_calibration_tool/bootstrap.py
uv run ruff check src/probability_calibration_tool/localization.py src/probability_calibration_tool/bootstrap.py
uv run ruff format src/probability_calibration_tool/localization.py src/probability_calibration_tool/bootstrap.py tests/localization
uv run pytest tests/localization -q
uv run ruff format tests/localization
uv run ruff check .
uv run ruff check tests/localization --fix
uv run ruff format src/probability_calibration_tool/localization.py tests/localization
```

The focused pytest command was rerun after fixes/additions, with these chronological summaries:

| Iteration | Observed summary | Resolution |
| --- | --- | --- |
| First new-test run | 7 failed, 111 passed in 8.17s | Newly written fault fixture reused exception objects, whose tracebacks retained writer references; it also retriggered a set failure during restoration. The fixture now raises fresh exception instances and fails its initial set once. Teardown/rollback assertions were retained. |
| Corrected initial test set | 118 passed in 8.53s | No failures |
| Added bootstrap/DB/architecture tests | 145 passed, 8 errors in 10.03s | New populated-DB fixture used an unrecognized Safety-backup reason. Corrected to accepted pre_history_correction. Production backup rules were not changed. |
| Corrected expanded set | 153 passed in 9.05s | No failures |
| Final tests, including exact Qt suffix protection and framework RuntimeError | 155 passed in 9.69s | No failures |

Early Ruff checks reported one BLE001 at the draft rollback logging site and later three new-test I001 import-order issues. Explicit recognized exception logging and test-only import sorting resolved them. No rule was disabled and no existing test was changed. Final Ruff results follow below.

The installed Qt filename fallback was directly probed using already-generated temporary catalogs:

```powershell
uv run python -c "from pathlib import Path; from PySide6.QtCore import QCoreApplication,QTranslator; app=QCoreApplication([]); root=Path('C:/Users/rxy71/AppData/Local/Temp/pytest-of-rxy71/pytest-97'); paths=list(root.rglob('*.qm.qm')); print(paths); [(print(str(p),args,t.load(*args),t.filePath())) for p in paths for args in [(str(p)[:-3],),(str(p)[:-3],'','','')] for t in [QTranslator()]]"
```

Observed: the default overload could return True and load `.qm.qm`; the explicit empty directory/delimiters/suffix overload returned False for a missing/corrupt canonical QM instead of selecting that variant. Production now uses the explicit overload plus filePath verification. Real regression tests also prove valid canonical QM is not shadowed by a valid double-extension neighbor.

## Original implementation localization validation (historical)

```powershell
uv run pytest tests/localization -q
```

```text
155 passed in 9.69s
```

Exit 0; failed=0, errors=0, skipped=0, xfailed=0, xpassed=0.

```powershell
uv run pytest tests/localization/test_catalog.py::test_real_locked_toolchain_ts_qm_qtranslator_smoke -v
```

```text
tests/localization/test_catalog.py::test_real_locked_toolchain_ts_qm_qtranslator_smoke PASSED
1 passed in 0.90s
```

Exit 0. The test creates TS with language=zh_CN and sourcelanguage=en, compiles temporary QM using the existing locked tool, and checks real QTranslator load, metadata, nonempty catalog and Localization/Language sentinel. Production assets were not generated.

```powershell
uv run pytest tests/localization --collect-only -q
```

```text
155 tests collected in 0.85s
```

Collection alone is not represented as a passing execution; the actual focused/full executions above and below provide that evidence.

## Existing bootstrap/startup regression

```powershell
uv run pytest tests/integration/desktop/test_bootstrap.py tests/integration/desktop/test_startup_routing.py tests/integration/application/reliability/test_startup.py
```

```text
collected 33 items
33 passed in 2.12s
```

Exit 0; failed/errors/skipped/xfailed/xpassed all 0. These existing test files were not modified.

## Original implementation full regression (historical)

```powershell
uv run pytest
```

```text
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
collected 1168 items
1168 passed in 119.50s (0:01:59)
```

Exit 0; **passed=1168, failed=0, errors=0, skipped=0, xfailed=0, xpassed=0**. This equals 1013 unchanged baseline tests + 155 new localization tests.

## Ruff and diff hygiene

```powershell
uv run ruff check .
uv run ruff format --check .
git diff --check
```

```text
All checks passed!
204 files already formatted
```

Both Ruff commands exited 0. The pre-report format check counted 202 files; the final check after creating both reports counted 204. git diff --check exited 0 with no output.

## Scope and protected-file verification

Read-only commands executed for scope evidence:

```powershell
git status --short
git diff --stat
git diff --numstat
git diff --name-only
git diff -- src/probability_calibration_tool/bootstrap.py
git ls-files --others --exclude-standard
Get-FileHash -LiteralPath SPEC_1.0.md,pyproject.toml,uv.lock,packaging/ProbabilityCalibrationTool.spec -Algorithm SHA256 | Select-Object Path,Hash | ConvertTo-Json
rg --files -g AGENTS.md -g '*localization*' -g '*.ts' -g '*.qm' -g '!uv.lock'
```

The tracked diff names only bootstrap.py (15 insertions, 2 deletions). Added files are exactly the new module, eight localization test files, and the two requested reports. No project TS/QM was found. No project file was removed. SHA-256 was also rechecked for the 175 exact baseline paths captured before editing; only bootstrap.py differed.

Unchanged hashes (paths relative to the working directory above):

| File | SHA-256 |
| --- | --- |
| SPEC_1.0.md | AEE4EB200BEA8EC1A652A65A2076645613E6057C37D6280A9A0787CC5B040FC4 |
| pyproject.toml | D4CEB0A37136942917DE80AA8940F9F60F4E6DFC16E276060A2C5F7C696654E6 |
| uv.lock | CBA8022E7E8A309A6436ED0667D4D78D4907EC82030676E7183211CF2C072A58 |
| packaging/ProbabilityCalibrationTool.spec | 8F9E86CE89BB16872A025A267B37C4A5208759ECF70F6C7F02830B6F95D77018 |

Read-only discovery also used Get-Content/rg on the request and relevant existing source/tests. Three preliminary assumed paths did not exist (`tests/integration/test_bootstrap.py`, `tests/infrastructure/test_startup.py`, `ruff.toml`); actual test paths were resolved with rg. No file was added to compensate for those failed probes.

## Stop boundary

All G1–G20 gates pass; coverage mapping is in the completion report. Incomplete Step 3 work: none. Prompt/SPEC deviations: none. Step 4/5, formal Chinese pack, UI translation, schema changes, dependency changes, model changes, packaging, and release/version work were not started.

## Third-party review correction — latest validation

This is a narrow test-contract correction, not a new feature. The permanent UI/DesktopHost rule no longer forbids translation APIs, presentation-localization helpers/imports, or read-only context dependencies. It still forbids translator construction/installation/removal and process-context construction/initialization from UI/DesktopHost. The Core/Domain/Application/Persistence isolation check was not changed or weakened. Ten AST-only regression cases verify the allowed/prohibited boundary; they do not implement a UI or Step 4 helper.

Exact files changed in this corrective pass:

```text
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\localization\test_architecture.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\localization_step3_completion_report.md
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\localization_step3_validation_commands.md
```

Files created: none. Files removed: none. Production code did not change, including localization.py, bootstrap.py, UI/DesktopHost, and all business layers. Schema remains v1. SPEC, dependencies, packaging, version, and business/model logic are unchanged.

### Exact correction commands and observed results

The architecture file was read before editing and reread after editing. The single test file was formatted with:

```powershell
uv run ruff format tests/localization/test_architecture.py
```

Result: `1 file reformatted`, exit 0. All edits were restricted to the test and two reports; there was no production formatting command during this correction.

| Literal command | Observed result | Exit |
| --- | --- | --- |
| `uv run pytest tests/localization/test_architecture.py -q` | 28 passed in 2.27s | 0 |
| `uv run pytest tests/localization -q` | 165 passed in 11.36s | 0 |
| `uv run pytest` | 1178 passed in 124.33s (0:02:04) | 0 |
| `uv run ruff check .` | All checks passed! | 0 |
| `uv run ruff format --check .` | 204 files already formatted | 0 |
| `git diff --check` | No output | 0 |

Ruff/diff checks were repeated after report updates. Every correction validation command passed. Final full totals: **1178 passed, 0 failed, 0 errors, 0 skipped, 0 xfailed, 0 xpassed**. Focused totals: **165 passed**, likewise zero failures/errors/skips/xfails/xpasses. The architecture-specific run passed all **28** tests. No failing test was hidden or weakened to pass; only the third-party-identified UI over-constraint was corrected.

The full count is 1013 original tests + 155 initial localization tests + 10 new contract-regression cases. The historical 1168/155 summaries above describe the original implementation and are not the latest totals.

### Before/after scope verification

Git was already dirty from the original Step 3 implementation. Therefore Git status alone would not prove no new production edit. The following exact read-only command captured and rechecked 225 file hashes across source, tests, tooling, packaging, outputs, and protected root files:

```powershell
$reviewFiles = @(rg --files --hidden -g '!.git' -g '!.venv' -g '!__pycache__' -g '!*.pyc' -g '!build' -g '!dist' -g '!work' -g '!.pytest_cache' -g '!.ruff_cache' src tests tools packaging outputs)
$reviewFiles += @('SPEC_1.0.md', 'pyproject.toml', 'uv.lock', '.gitignore')
$reviewFiles | Sort-Object -Unique | ForEach-Object { Get-FileHash -LiteralPath $_ -Algorithm SHA256 } | Select-Object Path,Hash | ConvertTo-Json
```

Before report edits, only test_architecture.py differed. After report edits, only the three explicitly listed files differed. All 86 production-file hashes remained identical. No source/new-file deletion occurred. This separately preserves the pre-existing Step 3 bootstrap diff and localization module without attributing them to this test-only correction.

Additional exact audit commands:

```powershell
git status --short
git diff -- src/probability_calibration_tool/bootstrap.py
git diff --name-only -- src/probability_calibration_tool/ui src/probability_calibration_tool/core src/probability_calibration_tool/domain src/probability_calibration_tool/application src/probability_calibration_tool/persistence
Get-FileHash -LiteralPath src/probability_calibration_tool/localization.py,src/probability_calibration_tool/bootstrap.py,SPEC_1.0.md,pyproject.toml,uv.lock,packaging/ProbabilityCalibrationTool.spec -Algorithm SHA256 | Select-Object Path,Hash | ConvertTo-Json
rg --files src -g '*.ts' -g '*.qm'
```

The UI/business-layer diff was empty. The source TS/QM search found no files (rg exit 1 means no matches). The original bootstrap diff was unchanged. The reviewed production modules' before/after SHA-256 values are:

| Absolute path | Unchanged SHA-256 |
| --- | --- |
| C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\localization.py | A9E5716706FEFC25CF61093432F20DBF94A5F5A6EB90623B169673F428C00761 |
| C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\bootstrap.py | A7BF991BCA04E8D4BF50E77A1098E00D65C8C944ADAF13D74FDC2114C41C920A |

G20 remains a Step 3 scope audit (unchanged UI/business files, no formal production TS/QM, no Language dialog, no UI translation implementation), not a permanent architecture ban on future presentation translation.

**No production code change. No new feature. Step 4/5 were NOT started. No formal language pack, UI translation, commit, tag, release, or packaging work was performed. The narrow correction is complete; no further implementation was started.**
