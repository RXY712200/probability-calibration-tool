# Localization Step 4 — External Review Narrow Rework Validation

Date: 2026-09-01. Working directory:
`C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability`

## Final commands and outcomes

| Literal command | Outcome |
|---|---|
| `uv run pytest` | exit 0; 1301 passed in 128.31s |
| `uv run pytest tests/localization -q` | exit 0; 288 passed in 17.91s |
| `uv run pytest tests/localization/test_architecture.py tests/localization/test_presentation_architecture.py tests/ui/test_architecture_formatting.py -q` | exit 0; 45 passed in 0.88s |
| `uv run pytest tests/localization/test_presentation.py tests/localization/test_language_ui.py tests/localization/test_presentation_integration.py -q` | exit 0; 112 passed in 8.44s |
| `uv run pytest tests/localization/test_presentation.py::test_real_extraction_exact_contexts_sources_and_placeholder_signatures -q` | exit 0; 1 passed in 1.11s |
| `uv run ruff check .` | exit 0; All checks passed! |
| `uv run ruff format --check .` | exit 0; 214 files already formatted |
| `git diff --check` | exit 0; no output |

All final pytest rows have: 0 failed, 0 errors, 0 skipped, 0 xfailed, 0 xpassed. Scoped counts overlap.

## Temporary real extraction

Literal command:

```powershell
$reworkAuditDirectory = Join-Path ([IO.Path]::GetTempPath()) ('pct-step4-rework-audit-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $reworkAuditDirectory | Select-Object -ExpandProperty FullName
uv run pyside6-lupdate -extensions py src -ts (Join-Path $reworkAuditDirectory 'step4-rework-extraction.ts')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
[xml]$reworkCatalog = Get-Content -LiteralPath (Join-Path $reworkAuditDirectory 'step4-rework-extraction.ts') -Raw
$reworkCatalog.TS.context | ForEach-Object { [pscustomobject]@{ Context = $_.name; Sources = @($_.message).Count } } | Format-Table -AutoSize
```

Exit 0. Output:

```text
C:\Users\rxy71\AppData\Local\Temp\pct-step4-rework-audit-42c8b6d2-d5cf-4cf8-ba61-d3118309ef3f
Scanning directory 'src'...
Updating '../../../../AppData/Local/Temp/pct-step4-rework-audit-42c8b6d2-d5cf-4cf8-ba61-d3118309ef3f/step4-rework-extraction.ts'...
    Found 225 source text(s) (225 new and 0 already existing)

Context       Sources
-------       -------
Analysis           25
AppShell            9
Characters         36
Correction         11
DomainLabels       19
Errors             34
Localization       19
Maintenance        13
Recovery            7
Restore            17
Round              29
StartupSafety       6
```

The app-owned context set is exactly:
`Analysis, AppShell, Characters, Correction, DomainLabels, Errors, Localization, Maintenance, Recovery, Restore, Round, StartupSafety`.

Total: 225 sources. Temporary artifact is outside the project and is not a production Step 5 catalog.

## Schema inspection

Literal command:

```powershell
uv run python -c "import sys; sys.path.insert(0, 'src'); from probability_calibration_tool.persistence.database import create_connection; from probability_calibration_tool.persistence.schema import initialize_v1; db=create_connection(':memory:'); initialize_v1(db); print('PRAGMA user_version:', db.execute('PRAGMA user_version').fetchone()[0]); print('Tables:', sorted(row[0] for row in db.execute('SELECT name FROM sqlite_master WHERE type=?', ('table',)))); db.close()"
```

Exit 0:

```text
PRAGMA user_version: 1
Tables: ['character_stats', 'characters', 'history_regimes', 'meta', 'round_analysis_snapshots', 'rounds']
```

## Scope and source audits

Literal commands:

```text
git status --short
git rev-parse HEAD
git diff --stat
git diff --check
rg --files src packaging -g '*.ts' -g '*.qm'
```

The TS/QM search returned no matches. HEAD is unchanged:
`00bd24b9fdc509809962ace4412b1e233b7c6598`.

Literal pre/final SHA-256 inventory command:

```powershell
$reworkFiles = @(rg --files --hidden -g '!.git' -g '!.venv' -g '!__pycache__' -g '!*.pyc' -g '!build' -g '!dist' -g '!work' -g '!.pytest_cache' -g '!.ruff_cache' src tests tools packaging outputs)
$reworkFiles += @('SPEC_1.0.md', 'pyproject.toml', 'uv.lock', '.gitignore')
$reworkFiles | Sort-Object -Unique | ForEach-Object { Get-FileHash -LiteralPath $_ -Algorithm SHA256 } | Select-Object Path,Hash | ConvertTo-Json
```

Before reports, comparison to the 233-path rework baseline found only:

```text
src/probability_calibration_tool/ui/desktop_boundary.py
src/probability_calibration_tool/ui/language_dialog.py
src/probability_calibration_tool/ui/localization.py
src/probability_calibration_tool/ui/main_window.py
src/probability_calibration_tool/ui/safety_window.py
tests/localization/test_language_ui.py
tests/localization/test_presentation_integration.py
tests/localization/test_presentation.py
```

No baseline path was added or removed; 225 were byte-identical. The two required rework reports were then created. Final comparison must therefore be 8 modified, 2 added, 0 removed relative to the rework baseline.

Production scans also ran for the rejected alternative UI strings and found no matches in production UI/tests. No `str(exc)` error-display branch was introduced. The permanent architecture suite remained green.

## Development correction evidence

The first focused presentation/language/error invocation after changing the canonical copy reported 2 failures, 110 passes. Both were stale assertions for the rejected phrases (`Qt standard` and `Restart the application`), while the actual UI already showed the required new exact text. The assertions were updated to the frozen sources. Reruns passed 112/112 and the full suite passed 1301/1301.

No production bug or unrelated file was changed to address those assertion failures.

## Frozen boundaries

Verified unchanged relative to the rework baseline:

- all Core and Domain source;
- all Application, persistence and infrastructure source;
- bootstrap and DesktopHost;
- accepted top-level `localization.py`;
- SPEC_1.0.md;
- pyproject.toml and uv.lock;
- packaging and tools;
- schema/model/seed sources;
- existing completion/validation reports.

No official TS/QM, Step 5 implementation, version bump, dependency change, schema change, business-semantic change, test skip or Golden-value edit.

**STEP 4 NARROW REWORK COMPLETE — READY FOR EXTERNAL RE-REVIEW**
