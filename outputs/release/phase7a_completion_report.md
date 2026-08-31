# Phase 7A Release Candidate Report

The automated Release Candidate is ready for Phase 7B manual acceptance. It is NOT final 1.0 release acceptance. The first artifact was rejected after a real launch failure; the final artifact below passed after the minimal packaging-only correction, full regression and clean rebuild.

## Baseline before Phase 7

`uv run pytest` before any Phase 7 edits: **992 passed in 50.45s**, 0 failed, 0 skipped, 0 xfailed, 0 xpassed.

## Files created

Source/build/QA files (13 exact paths):

- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/packaging/ProbabilityCalibrationTool.spec`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/packaging/pyinstaller_entry.py`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tools/__init__.py`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tools/packaged_smoke.py`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tools/prepare_manual_history.py`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tools/release_performance.py`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tools/release_verify.py`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/release/__init__.py`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/release/conftest.py`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/release/test_manual_history_fixture.py`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/release/test_performance_100k.py`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/release/test_release_artifact.py`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/release/test_release_verify.py`

Release evidence (22 exact paths):

- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/analysis_audit.json`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/artifact_audit.json`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/automated_integrity_100k.json`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/automated_integrity_packaged_daily.json`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/automated_integrity_packaged.json`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/FINAL_RELEASE_GATE_1.0.md`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/packaged_smoke.json`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/performance_100k.json`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/performance_50k.json`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/PHASE_7B_MANUAL_ACCEPTANCE_CHECKLIST.md`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_completion_report.md`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_packaging_audit.md`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_packaging_first_failure.md`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_performance_100k.md`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_validation_commands.md`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pyinstaller_build_failed.log`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pyinstaller_build.log`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pyinstaller_warnings_failed.txt`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pyinstaller_warnings.txt`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pytest_final.log`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pytest_pre_packaging_fix.log`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/source_integrity.json`

Generated artifact directory: `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\dist\ProbabilityCalibrationTool`; all 298 exact relative file paths, sizes and hashes are enumerated in [artifact_audit.json](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/artifact_audit.json). Final EXE path is given below. PyInstaller intermediate files are generated under `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/build/ProbabilityCalibrationTool`, excluded from source tracking. These generated directories are not additional product source.

Isolated diagnostic databases/backups and runtime files remain under `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/work/phase7a-perf-50k`, `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/work/phase7a-perf-100k` and the external smoke root below; exact verified DB paths are listed under Final automated integrity checks. Pytest also creates disposable temporary fixtures, including the verified 19/1 manual-fixture preparation test. No data was added inside the distributable.

## Files modified

- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/pyproject.toml`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/uv.lock`
- `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/.gitignore`

No source files were removed. Rejected generated build/dist were moved, not deleted, to `C:\Users\rxy71\AppData\Local\Temp\PCT Phase7A rejected build 20260831`; the rejected first external copy is also preserved. Do not distribute those rejected copies. Python/build caches remain ignored rather than source-controlled.

## Accepted production-source modifications

none. SHA-256 comparison preserves 159 accepted source/test/SPEC files. All 175 final tested source/config files still match after build. See [source_integrity.json](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/source_integrity.json).

## Schema

Schema v1 unchanged

No table, migration or version change. SPEC SHA-256 remains AEE4EB200BEA8EC1A652A65A2076645613E6057C37D6280A9A0787CC5B040FC4. Schema implementation SHA-256 remains FB457C818780A94EF62AB53A3ED02FC0779FF1C4B0001734FBD67D56486F9315.

## Dependencies

PyInstaller **6.22.2** added to dev/build dependency group as >=6.22.2,<7; uv.lock regenerated with `uv lock`, then `uv sync`. Build lock additions include pyinstaller-hooks-contrib 2026.7, altgraph 0.17.5, pefile 2024.8.26, pywin32-ctypes 0.2.3, setuptools 84.0.0 and platform-conditional macholib 1.16.4. No new product runtime dependency. Accepted SciPy **1.18.1**, PySide6 **6.11.2** and Python **3.13.14** unchanged.

## PyInstaller entrypoint

`C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/packaging/pyinstaller_entry.py` is a thin absolute-import adapter calling the accepted probability_calibration_tool.bootstrap.main, then SystemExit. No business logic, second bootstrap, hidden test mode, or change to python -m probability_calibration_tool.

## PyInstaller spec

`C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/packaging/ProbabilityCalibrationTool.spec` creates whole-folder **onedir**, with EXE exclude_binaries=True plus COLLECT, name ProbabilityCalibrationTool, **console=False**, explicit SPECPATH-derived project/src path. Normal Qt/PySide6/SciPy hooks only; explicit hiddenimports/data/binaries are empty. No collect_all or custom runtime hook. The structure follows the [PyInstaller spec documentation](https://pyinstaller.org/en/stable/spec-files.html).

The first build's inherited native PATH selected an incompatible Poppler ICU. The final spec limits native search PATH to Windows/System32 and Windows before Analysis. This is a build-environment correction, not a product formula/UI/source change. Regression proves a poisoned Poppler PATH is excluded.

## Clean build

`uv run pyinstaller --clean --noconfirm packaging/ProbabilityCalibrationTool.spec`

Final build succeeded (~39.4s) AFTER final pytest/Ruff. Old targets were archived and build/dist verified absent before rebuilding. Exact PowerShell guard/logging invocation and both build histories are in [phase7a_validation_commands.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_validation_commands.md) and [pyinstaller_build.log](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pyinstaller_build.log). No source/config edits followed the final build.

## Release Candidate artifact

Directory:

`C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\dist\ProbabilityCalibrationTool`

EXE:

`C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\dist\ProbabilityCalibrationTool\ProbabilityCalibrationTool.exe`

**298 files / 223,928,257 bytes / 213.55 MiB**. AMD64 PE32+, Windows GUI subsystem. EXE SHA-256:

`d45ebba5acd758b05401c1bd6b146af815517605fe8dacb7426120d9b2baeaf1`

Distribute the ENTIRE onedir folder, not the EXE alone. No installer, signing or updater work.

## PyInstaller warnings

Reviewed, not blanket-ignored:

- scipy.special._cdflib: normal hook requests a module absent from accepted SciPy 1.18.1. Installed Beta PPF uses _ufuncs._beta_ppf and CDF uses betainc; required native modules are collected and loaded in the final EXE. Actual history-visible GUI calculation remains manual pending.
- Numerical function/type reexports: 220 warning names resolve as attributes, not modules. Optional _fblas_64/_flapack_64 guarded by HAS_ILP64=False; accepted LP64 variants loaded.
- collections.abc is an explicit Python 3.13 alias to collected _collections_abc. No required product/PySide6/SQLite module missing.
- Remaining warnings are conditional non-Windows/alternate-Python, optional backend, plotting, docs, test/development or site-override branches; dispositions and full warning output retained.

Detailed categories/evidence: [phase7a_packaging_audit.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_packaging_audit.md); raw [pyinstaller_warnings.txt](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pyinstaller_warnings.txt). The blocking first-build QtWidgets import error was caused by wrong native ICU, now fixed; final EXE actually loads Windows system ICU. No application source change was needed.

## Artifact audit

PASS. No project/user DB, log, backup, lock, pytest cache, screenshots/reports, copied project src/tests or .venv. Normal vendor testing support is not project leakage. Analysis confirms 84 product modules and 83 SciPy extension/binary entries; no developer Poppler/libheif or project tests/tools/work/outputs sources. [artifact_audit.json](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/artifact_audit.json) and [analysis_audit.json](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/analysis_audit.json).

## Outside-repo test

PASS. Only the complete onedir artifact was copied to:

`C:\Users\rxy71\AppData\Local\Temp\Probability Calibration Tool RC dgajh1ad\Probability Calibration Tool`

Contains spaces, outside repository/source/.venv. File-by-file SHA-256 matches. No source/tests/.venv copied or needed; no loaded process module under the repository.

## Working-directory independence

PASS. Absolute external EXE launched with cwd:

`C:\Users\rxy71\AppData\Local\Temp\Probability Calibration Tool RC dgajh1ad\unrelated working directory`

The cwd remained empty before/after smoke. Package hashes also stayed unchanged.

## Isolated LOCALAPPDATA

`C:\Users\rxy71\AppData\Local\Temp\Probability Calibration Tool RC dgajh1ad\isolated LOCALAPPDATA`

Persistent files appeared only beneath its ProbabilityCalibrationTool child: data/probability.db, logs/app.log, runtime/application.lock and one Daily backup. Not in dist, external artifact or cwd; real personal production root not used. Exact file list and native module origins: [packaged_smoke.json](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/packaged_smoke.json).

## Packaged launch smoke

PASS. A PID 35208 reached the accepted normal window title and initialized healthy Schema v1. Real Windows qwindows.dll, QtWidgets, bundled Python/SQLite and SciPy _ufuncs/_stats loaded; not offscreen. PYTHONPATH/VIRTUAL_ENV removed and PATH restricted to C:\Windows\System32;C:\Windows. Saved child processes terminated only after observations. Termination is NOT normal GUI-close, Recovery, full-round or manual DPI acceptance.

## Packaged single-instance

**PENDING manual dismissal/exit confirmation.** Automated evidence: A owns the exclusive lock; B PID 31536 shows only ALREADY_RUNNING notification, not a second normal business window; A remains alive. Modal deliberately was not clicked. No production test hook was introduced. Both saved child processes were terminated after the smoke, and no longer run.

## 100k dataset

Exactly **100,000 completed, eligible rounds / 100,000 full snapshots / 70,000 wins / 30,000 losses**, all character 1/current regime regime-1-1. Deterministic timestamp ordering, reverse-lexical valid UUIDs, valid facts and FK relationships. Each full snapshot uses accepted prior-history Core computation; no incomplete fake DB or production bulk-import feature.

## 100k correctness

PASS: integrity=ok, FK clean, source/snapshot/eligible counts exact, stats 100000/70000/30000 and chronological last ID correct. Deliberate cache version 99 is rebuilt by real StartupService to version 1; healthy startup and 34-character Maintenance query verified. Real Calculate freezes n=100000; Include completion makes live n=100001 while the complete prediction snapshot remains unchanged. [performance_100k.json](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/performance_100k.json).

## 100k performance observations

Diagnostic seconds: fixture **13.6902**; invariant inspection **2.3042**; stats validation/rebuild **1.0043**; startup including repair/Daily **5.5789**; Calculate **1.1345**; completion **0.0302**; Online Backup **2.2351**. Stats time is already included in startup. 50k comparison shows approximately linear main paths; one I/O-sensitive backup ratio is 3.01×, explained and retained rather than hidden. No arbitrary millisecond gate. [phase7a_performance_100k.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_performance_100k.md).

## 100k memory observations

Windows process metrics: baseline working set **94.57 MiB**, peak **579.66 MiB**, final **109.44 MiB**. Repeated retained working sets after GC: **107.52 / 107.68 / 108.23 MiB**. Pre-fixture private commit ~1545.83 MiB already exists after imports; final ~1561.42 MiB, not equivalent to resident RAM. No obvious runaway accumulation in three repeats; accepted invariant inspection intentionally materializes source rows/snapshots and scales in transient memory. This is not a long-duration leak proof or a fixed MB acceptance gate.

## Large backup smoke

PASS. Real production SQLite Online Backup of the completed 100k smoke preserves **100001 completed rounds / 100001 snapshots**, schema 1, pending 0, integrity=ok and no FK violations. No new backup mode or semantics. Exact path:

`C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\work\phase7a-perf-100k\backups\recent\recent_20260831T051721.818104Z_dfdebfd4-30ad-47e0-8f50-8a4f1c3a0997.db`

## Automated regression

`uv run pytest`: **1013 passed in 83.55s; 0 failed; 0 skipped; 0 xfailed; 0 xpassed** after every source/config fix, before final clean RC. [pytest_final.log](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pytest_final.log).

## Phase 1-6 regressions

All accepted groups rerun unchanged in the final unfiltered suite: Phase 1 **213**; Phase 2 **293**; Phase 3 **153**; Phase 4 **107**; Phase 5 **106**; Phase 6 **120**. Accepted total **992**, plus **21** Phase 7A regressions. Fresh/recovery E2E, migrations, Safety/Recent/correction chains, restore failure boundaries/stale Session revocation and anti-anchoring paths are explicitly mapped in [phase7a_validation_commands.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_validation_commands.md).

## Ruff

- `uv run ruff check .`: **All checks passed!**, exit 0.
- `uv run ruff format --check .`: **189 files already formatted**, exit 0, before final build; **193 files already formatted** after the evidence reports were added. Evidence-only additions do not alter packaged source/config. Final hash/inventory recheck confirms 175 tested source/config files and both 298-file artifact copies unchanged.

## Final automated integrity checks

Independent mode=ro/query_only=ON verifier; no startup/repair/migration in verification. All of the following returned **integrity=ok**, schema 1, no FK violations and matching round/snapshot counts:

| Exact checked path | Final completed / pending |
|---|---:|
| C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\work\phase7a-perf-100k\data\probability.db | 100001 / 0 |
| C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\work\phase7a-perf-100k\backups\recent\recent_20260831T051721.818104Z_dfdebfd4-30ad-47e0-8f50-8a4f1c3a0997.db | 100001 / 0 |
| C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\work\phase7a-perf-50k\data\probability.db | 50001 / 0 |
| C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\work\phase7a-perf-50k\backups\recent\recent_20260831T051639.779015Z_829fc969-4427-49a9-9dae-c3475d85b3e0.db | 50001 / 0 |
| C:\Users\rxy71\AppData\Local\Temp\Probability Calibration Tool RC dgajh1ad\isolated LOCALAPPDATA\ProbabilityCalibrationTool\data\probability.db | 0 / 0 |
| C:\Users\rxy71\AppData\Local\Temp\Probability Calibration Tool RC dgajh1ad\isolated LOCALAPPDATA\ProbabilityCalibrationTool\backups\daily\daily_2026-08-31_20260831T053058.126832Z_6804479a-5801-4fa2-baec-2aaa7805fe2e.db | 0 / 0 |

Both large source DBs were also checked before their extra completion at exactly 50000/100000 records. Disposable regression fixtures separately pass their own integrity assertions, including the 19/1 preparation helper. Artifact and external-copy inventories were checked before/after launching and match; final source hashes match the tested state. Automated integrity does NOT close gate 18 for the yet-unexecuted post-manual workflow DB.

## Final Release Gate Matrix

**13 PASS / 0 FAIL / 5 PENDING.** Full evidence: [FINAL_RELEASE_GATE_1.0.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/FINAL_RELEASE_GATE_1.0.md).

| # | Requirement | Status | Evidence / remaining work |
|---:|---|---|---|
| 1 | release-blocking tests pass | PASS | 1013 passed, all failure/skip/xfail/xpass counts 0. [pytest_final.log](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pytest_final.log) |
| 2 | Ruff check passes | PASS | uv run ruff check . — All checks passed, before final clean build. [phase7a_validation_commands.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_validation_commands.md) |
| 3 | Ruff format check passes | PASS | uv run ruff format --check . — 189 files already formatted, before final clean build. [phase7a_validation_commands.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_validation_commands.md) |
| 4 | no unexplained skip/xfail | PASS | 0 skipped, 0 xfailed, 0 xpassed; accepted tests preserved by SHA-256. [source_integrity.json](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/source_integrity.json) |
| 5 | fresh DB E2E | PASS | Accepted real StartupService/DesktopHost end-to-end test rerun in full suite (source/offscreen). [pytest_final.log](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pytest_final.log) |
| 6 | pending recovery E2E | PASS | Real source close/start/explicit Continue/same frozen snapshot/completion/New Round test rerun. [pytest_final.log](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pytest_final.log) |
| 7 | backup/restore E2E | PASS | Normal/emergency restore, pre/post replacement failures, stale Session revocation, Safety/Recent rerun. [phase7a_validation_commands.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_validation_commands.md) |
| 8 | migration | PASS | 7 frozen migration tests rerun, Schema v1 unchanged. [pytest_final.log](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pytest_final.log) |
| 9 | correction | PASS | Safety-before-write, immutable correction chain/no branch and Recent checks rerun. [phase7a_validation_commands.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_validation_commands.md) |
| 10 | anti-anchoring | PASS | No pre-lock/reference=false/no_history/insufficient history leakage, non-directional admin and exposure-before-render tests rerun. [phase7a_validation_commands.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_validation_commands.md) |
| 11 | 100k smoke | PASS | 100,000 eligible under one current regime; real repair/Calculate/complete/backup; frozen n=100000 while live n=100001. [phase7a_performance_100k.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_performance_100k.md) |
| 12 | Windows 125% DPI | PENDING | Phase 7B manual acceptance. No real Windows DPI acceptance performed. [PHASE_7B_MANUAL_ACCEPTANCE_CHECKLIST.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/PHASE_7B_MANUAL_ACCEPTANCE_CHECKLIST.md) |
| 13 | Windows 150% DPI | PENDING | Phase 7B manual acceptance. No real Windows DPI acceptance performed. [PHASE_7B_MANUAL_ACCEPTANCE_CHECKLIST.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/PHASE_7B_MANUAL_ACCEPTANCE_CHECKLIST.md) |
| 14 | PyInstaller onedir | PASS | Clean build; whole folder, AMD64 Windows GUI, 298 files. [artifact_audit.json](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/artifact_audit.json) |
| 15 | packaged app outside PyCharm/.venv | PASS | Full copy outside repo with spaces, absolute EXE, unrelated cwd and sanitized environment; actual qwindows/SQLite/SciPy native load. [packaged_smoke.json](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/packaged_smoke.json) |
| 16 | packaged app completes full test round | PENDING | Phase 7B manual packaged full round and controlled history-valid/SciPy UI path. Launch is not full-round acceptance. |
| 17 | packaged app survives close/reopen correctly | PENDING | Phase 7B manual A/B/C normal-close/Recovery test. Automated child termination does not satisfy this gate. |
| 18 | final PRAGMA integrity_check returns ok | PENDING | Final post-Phase-7B packaged-workflow DB required. Automated 100k/backup/fresh DB checks passed but do not close this gate. |

## Phase 7B Manual Acceptance Checklist

Prepared, NOT executed: [PHASE_7B_MANUAL_ACCEPTANCE_CHECKLIST.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/PHASE_7B_MANUAL_ACCEPTANCE_CHECKLIST.md).

It contains exact isolated-root/EXE commands and:

1. Windows 125% and 150% separately: close app → change Windows scaling → fresh launch; inspect all ten required states and exact layout blockers, with genuine screenshot filenames planned.
2. Packaged A/B/C workflow: fresh no-reference Calculate → normal close → same-root Recovery and explicit Continue → same prediction → explicit result/include → Confirm Save → Completed Notice/Recent/New Round → normal close → next launch DRAFT.
3. Fresh controlled 19-win/1-loss helper root → packaged Use history Calculate → subjective lock/exposure-safe historical rendering, sample size/Jeffreys values, no SciPy DLL error.
4. Single-instance A/B modal dismissal and PID exit confirmation.
5. After normal closure, exact read-only --final-manual command against final workflow DB and actual Recent backup; require integrity ok, schema 1, pending 0 and completed exists.

No fake screenshots, manual sign-off or packaged numerical/full-round claim.

## Manual DPI

Windows 125%: **PENDING — Phase 7B manual acceptance**.

Windows 150%: **PENDING — Phase 7B manual acceptance**.

No manual DPI acceptance performed. Structural/offscreen tests are not substitutes.

## SPEC deviations

none

## SPEC concerns

Retained accepted concern: Application still has no void-only completed-record service for incorrect pre-run facts. This optional capability remains unexposed; no new mutation path or replacement prediction was invented.

## Incomplete automated work

none for required Phase 7A automated preparation. Single-instance modal dismissal is the explicitly allowed manual-pending exception; all required automated blockers pass on the final artifact.

## Manual work remaining

125% DPI; 150% DPI; packaged full round; normal close/reopen Recovery; controlled history-valid SciPy GUI path; second-instance modal dismissal/exit; final post-manual workflow DB/Recent integrity and human sign-off. Gate rows 12,13,16,17,18 stay PENDING.

## Known release risks

- Manual Windows layout/workflow/normal shutdown/numerical GUI behavior has not yet been accepted on the packaged RC.
- Approximately 580 MiB transient resident peak at 100k is a capacity observation, not a hidden constant-space claim; longer-duration leak behavior is not established by three repeats.
- Windows 11 x64 is the verified target; no other OS or clean separate machine has been accepted. Keep all onedir files together.
- Unsigned PyInstaller distribution may encounter machine-specific SmartScreen/security policy. No installer/signing/auto-update or antivirus-zero-false-positive gate was added. No local security setting was changed.
- The final package still emits documented optional/static-analysis SciPy warnings. Real manual history-valid UI remains an explicit pending check.

## Final status

Phase 7A automated Release Candidate preparation complete. Manual Phase 7B acceptance remains pending.
