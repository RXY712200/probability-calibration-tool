# Localization Step 4 — Validation Commands and Evidence

Date: 2026-09-01. All commands ran from:
`C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability`

Final status: **IMPLEMENTATION COMPLETE — READY FOR EXTERNAL STEP 4 REVIEW**.
This records implementation evidence only, not external acceptance.

## Final validation commands

| Literal command | Result |
|---|---|
| `uv run pytest` | exit 0; 1286 passed in 139.39s (0:02:19) |
| `uv run pytest tests/localization -q` | exit 0; 273 passed in 20.82s |
| `uv run pytest tests/localization/test_architecture.py tests/localization/test_presentation_architecture.py tests/ui/test_architecture_formatting.py -q` | exit 0; 45 passed in 2.02s |
| `uv run pytest tests/localization/test_presentation.py tests/localization/test_presentation_integration.py tests/localization/test_language_ui.py -q` | exit 0; 97 passed in 10.93s |
| `uv run pytest tests/localization/test_presentation.py::test_real_extraction_exact_contexts_sources_and_placeholder_signatures -q` | exit 0; 1 passed in 1.69s |
| `uv run ruff check .` | exit 0; All checks passed! |
| `uv run ruff format --check .` | exit 0; 212 files already formatted after report creation (210 before) |
| `git diff --check` | exit 0; no output |

Every final pytest invocation above had **0 failed, 0 errors, 0 skipped, 0 xfailed, 0 xpassed**. Scope counts overlap; do not sum them.

## Real Qt extraction

Literal PowerShell command:

```powershell
$step4AuditDirectory = Join-Path ([IO.Path]::GetTempPath()) ('pct-step4-audit-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $step4AuditDirectory | Select-Object -ExpandProperty FullName
uv run pyside6-lupdate -extensions py src -ts (Join-Path $step4AuditDirectory 'step4-extraction.ts')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
[xml]$step4Catalog = Get-Content -LiteralPath (Join-Path $step4AuditDirectory 'step4-extraction.ts') -Raw
$step4Catalog.TS.context | ForEach-Object { [pscustomobject]@{ Context = $_.name; Sources = @($_.message).Count } } | Format-Table -AutoSize
```

Exit 0. Artifact:
`C:/Users/rxy71/AppData/Local/Temp/pct-step4-audit-831847d9-646c-4b0a-9e8b-854c82201ca0/step4-extraction.ts`

Output: **Found 230 source text(s) (230 new and 0 already existing)**.

Exact context/source counts:
Analysis 25; AppShell 9; Characters 36; Correction 11; DomainLabels 19; Errors 37; Localization 21; Maintenance 13; Recovery 7; Restore 17; Round 29; StartupSafety 6.

The dedicated pytest audit also invokes the actual `.venv/Scripts/pyside6-lupdate.exe` with `-extensions py`, production src and a pytest temporary TS path. No production catalog is created.

Installed-tool inspection commands:

```text
uv run pyside6-lupdate -version
uv run pyside6-lupdate -help
uv run python -c "from PySide6.QtCore import QT_TRANSLATE_NOOP; print(QT_TRANSLATE_NOOP('Example','source'))"
```

Version 6.11.2. NOOP returns its English source without translation lookup. The installed directory-scan default extensions omit Python; `-extensions py` is required and was used in all successful extraction audits.

## Actual schema inspection

Literal corrected command:

```powershell
uv run python -c "import sys; sys.path.insert(0, 'src'); from probability_calibration_tool.persistence.database import create_connection; from probability_calibration_tool.persistence.schema import initialize_v1; db=create_connection(':memory:'); initialize_v1(db); print('PRAGMA user_version:', db.execute('PRAGMA user_version').fetchone()[0]); print('Tables:', sorted(row[0] for row in db.execute('SELECT name FROM sqlite_master WHERE type=?', ('table',)))); db.close()"
```

Exit 0:

```text
PRAGMA user_version: 1
Tables: ['character_stats', 'characters', 'history_regimes', 'meta', 'round_analysis_snapshots', 'rounds']
```

This initializes the actual production DDL in an isolated in-memory test database. The paired English/marker integration additionally verifies every table and row of real on-disk databases/backups through Recovery, Correction and Restore.

The first standalone schema command omitted the src import path:

```powershell
uv run python -c "from probability_calibration_tool.persistence.database import create_connection; from probability_calibration_tool.persistence.schema import initialize_v1; db=create_connection(':memory:'); initialize_v1(db); print('PRAGMA user_version:', db.execute('PRAGMA user_version').fetchone()[0]); print('Tables:', sorted(row[0] for row in db.execute('SELECT name FROM sqlite_master WHERE type=?', ('table',)))); db.close()"
```

It exited 1 with ModuleNotFoundError because this checkout relies on pytest's src-path configuration rather than an editable installed package. Only the inspection invocation was corrected with sys.path.insert; no dependencies, packaging or production source was changed for this diagnostic.

## Git and scope inspection

Literal commands included:

```text
git status --short
git rev-parse HEAD
git diff --stat
git diff --numstat
git diff --check
git diff -- src/probability_calibration_tool/bootstrap.py src/probability_calibration_tool/core src/probability_calibration_tool/application/restore_service.py src/probability_calibration_tool/infrastructure/backup.py src/probability_calibration_tool/infrastructure/restore_engine.py src/probability_calibration_tool/persistence/repositories/rounds.py
git diff -- src/probability_calibration_tool/application src/probability_calibration_tool/ui tests/integration/desktop tests/ui tests/integration/infrastructure/test_logging.py
git diff -- src/probability_calibration_tool/ui/analysis_panel.py src/probability_calibration_tool/ui/close_guard.py src/probability_calibration_tool/ui/post_run_panel.py src/probability_calibration_tool/ui/pre_run_panel.py src/probability_calibration_tool/ui/main_window.py src/probability_calibration_tool/ui/maintenance_page.py
rg --files src packaging -g '*.ts' -g '*.qm'
```

No TS/QM matches (rg exit 1 means no matches, not a failed validation). HEAD is unchanged:
`00bd24b9fdc509809962ace4412b1e233b7c6598`.

Final tracked diff: 45 files, 681 insertions, 246 deletions. The separate pre-edit hash inventory distinguishes incoming untracked Step 3 files from the 8 Step 4 additions. See section K of the completion report for actual final status and section B for all exact file links/purposes.

Literal baseline/final SHA-256 inventory command:

```powershell
$stageFiles = @(rg --files --hidden -g '!.git' -g '!.venv' -g '!__pycache__' -g '!*.pyc' -g '!build' -g '!dist' -g '!work' -g '!.pytest_cache' -g '!.ruff_cache' src tests tools packaging outputs)
$stageFiles += @('SPEC_1.0.md', 'pyproject.toml', 'uv.lock', '.gitignore')
$stageFiles | Sort-Object -Unique | ForEach-Object { Get-FileHash -LiteralPath $_ -Algorithm SHA256 } | Select-Object Path,Hash | ConvertTo-Json
```

225 baseline paths were captured before edits. Comparing their final bytes yields 45 modified, 180 unchanged, 0 removed; the final inventory additionally has 8 new Step 4 files. Protected source/spec/dependency/packaging/Step 3 groups match their incoming hashes. No reset, checkout, commit, tag or history replacement was used.

## English-source inventory

Literal read-only AST comparison against Git HEAD UI sources:

```powershell
uv run python -c "import ast, pathlib, subprocess; root=pathlib.Path('src/probability_calibration_tool/ui'); current={n.value for p in root.glob('*.py') for n in ast.walk(ast.parse(p.read_text(encoding='utf-8'))) if isinstance(n,ast.Constant) and isinstance(n.value,str)}; files=subprocess.check_output(['git','ls-files',str(root)],text=True).splitlines(); old={n.value for p in files if p.endswith('.py') for n in ast.walk(ast.parse(subprocess.check_output(['git','show','HEAD:'+p],text=True,encoding='utf-8'))) if isinstance(n,ast.Constant) and isinstance(n.value,str)}; print('\n'.join(repr(s) for s in sorted(old-current) if ' ' in s and len(s)>8))"
```

Exit 0. Missing literal pieces were dynamic fragments (Error ID, Current regime, Subjective/odds/calculated facts, thresholds, sample counts, percentage clamp notice and the Unavailable separator) now represented by complete fixed templates. No existing static UI sentence disappeared. Semantic error-message changes and authorized new Language UI copy are explicitly enumerated in completion report section I.

## Development correction cycles (not final gate totals)

Earlier failures are recorded rather than presenting an uninterrupted green run:

| Literal command | Earlier outcome / correction |
|---|---|
| `uv run pytest tests/ui tests/integration/desktop tests/localization -q` | 1 failed, 386 passed; old injected diagnostic expectation intentionally migrated to safe semantic current-state source. |
| `uv run pytest tests/localization/test_presentation.py -q` | First 11 failed, 23 passed: new test fixture used a nonexistent list_active method (correct method list_all); initial extraction directory scan omitted -extensions py. Corrected test fixture/tool invocation, then 34 passed in 4.81s. A further warning test is included in the final 35-case file. |
| `uv run pytest tests/localization/test_language_ui.py -q` | First 1 failed, 23 passed: synthetic radio-button center click missed its active text/indicator. Used standard button click; 24 passed in 1.42s. Final file has 29 cases. |
| `uv run pytest tests/localization/test_presentation_integration.py -q` | 1 failed, 30 passed: independent stats/meta wall clocks made otherwise equal rows differ. Froze that additional clock in the test without omitting timestamp comparisons; then 31 passed in 4.30s. Final file has 33 cases. |
| `uv run pytest` | First full run: 2 failed, 1265 passed in 130.61s. Old ErrorPresentation exact-fields test needed the frozen code field; old synthetic backup categories used display strings instead of real category identity. Narrow migrations documented in completion report D. Final rerun: 1286 passed. |
| `uv run pytest tests/localization -q` | Interim 1 failed, 271 passed: the new static audit incorrectly treated QPushButton.setDefault as QLocale.setDefault. Scoped the audit to QLocale; generic widgets/production unchanged. Final rerun: 273 passed. |
| `uv run pytest tests/localization tests/ui/test_startup_pages.py tests/integration/infrastructure/test_logging.py -q` | 283 passed in 18.75s before the last two new composition/priority cases and removal of a new stage-only catalog-ban test. Stage-only no-catalog compliance is recorded as an audit, not a permanent rule blocking Step 5. |

Formatting/import cleanup commands included:

```text
uv run ruff check . --fix
uv run ruff format .
uv run ruff check tests/localization --fix
uv run ruff format tests/localization
uv run ruff format tests/localization tests/integration/infrastructure/test_logging.py
```

Final lint/format/diff checks were rerun after the completion documents were created. No old tests were removed, skipped, xfailed or mathematically weakened. New architecture tests preserve legitimate future UI translation.

**IMPLEMENTATION COMPLETE — READY FOR EXTERNAL STEP 4 REVIEW**
