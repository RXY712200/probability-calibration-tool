# Localization Step 6 Validation Commands

## Baseline

Working directory:

`C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability`

Literal commands:

```powershell
git status --short
git rev-parse HEAD
```

Baseline HEAD:

```text
00bd24b9fdc509809962ace4412b1e233b7c6598
```

Baseline status showed the already-uncommitted/untracked accepted Step 3–5 tree. The protected baseline was captured after the initial Step 6 test-only files existed, but before any protected edit; Step 6 never edited a protected file. Baseline status categories were 45 tracked modifications plus prior untracked Step 3–5 output/production/test/tool/translation paths and the already-untracked `tests/localization/` directory.

Protected hash capture command:

```powershell
$ErrorActionPreference = 'Stop'
$root = (Get-Location).Path
$protected = @()
$protected += Get-ChildItem -LiteralPath (Join-Path $root 'src') -Recurse -File
foreach ($literal in @('SPEC_1.0.md','pyproject.toml','uv.lock')) {
    $p = Join-Path $root $literal
    if (Test-Path -LiteralPath $p) { $protected += Get-Item -LiteralPath $p }
}
foreach ($dir in @('packaging','installer')) {
    $p = Join-Path $root $dir
    if (Test-Path -LiteralPath $p) {
        $protected += Get-ChildItem -LiteralPath $p -Recurse -File
    }
}
$ts = Join-Path $root 'translations\probability_calibration_tool_zh_CN.ts'
$protected += Get-Item -LiteralPath $ts
$hashes = [ordered]@{}
foreach ($file in ($protected | Sort-Object FullName -Unique)) {
    $rel = [IO.Path]::GetRelativePath($root, $file.FullName).Replace('\','/')
    $hashes[$rel] = (Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash.ToLowerInvariant()
}
```

Baseline result: 182 protected files. Official TS SHA-256 was `82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257`.

## Final fresh extraction and catalog equality

Literal command:

```powershell
$ErrorActionPreference = 'Stop'
$finalRoot = 'C:\Users\rxy71\AppData\Local\Temp\pct-step6-final'
if (-not (Test-Path -LiteralPath $finalRoot)) { New-Item -ItemType Directory -Path $finalRoot | Out-Null }
uv run pyside6-lupdate -extensions py src -ts C:\Users\rxy71\AppData\Local\Temp\pct-step6-final\probability_calibration_tool_zh_CN.ts
```

Exit: 0

```text
Scanning directory 'src'...
Updating '../../../../AppData/Local/Temp/pct-step6-final/probability_calibration_tool_zh_CN.ts'...
    Found 225 source text(s) (225 new and 0 already existing)
```

Literal semantic comparison command:

```powershell
$ErrorActionPreference = 'Stop'
[xml]$official = Get-Content -LiteralPath 'translations\probability_calibration_tool_zh_CN.ts' -Raw -Encoding UTF8
[xml]$fresh = Get-Content -LiteralPath 'C:\Users\rxy71\AppData\Local\Temp\pct-step6-final\probability_calibration_tool_zh_CN.ts' -Raw -Encoding UTF8
$officialKeys = @($official.TS.context | ForEach-Object { $context = [string]$_.name; @($_.message) | ForEach-Object { "$context`u{001F}$([string]$_.source)`u{001F}$([string]$_.numerus)" } })
$freshKeys = @($fresh.TS.context | ForEach-Object { $context = [string]$_.name; @($_.message) | ForEach-Object { "$context`u{001F}$([string]$_.source)`u{001F}$([string]$_.numerus)" } })
$missing = @($officialKeys | Where-Object { $_ -notin $freshKeys })
$extra = @($freshKeys | Where-Object { $_ -notin $officialKeys })
$contexts = @($fresh.TS.context | ForEach-Object { [string]$_.name } | Sort-Object -Unique)
[ordered]@{ official_active=$officialKeys.Count; production_active=$freshKeys.Count; contexts=$contexts.Count; missing=$missing.Count; extra=$extra.Count; exact=($missing.Count -eq 0 -and $extra.Count -eq 0 -and $officialKeys.Count -eq 225 -and $freshKeys.Count -eq 225) } | ConvertTo-Json
if ($missing.Count -ne 0 -or $extra.Count -ne 0) { exit 1 }
```

Exit: 0

```json
{
  "official_active": 225,
  "production_active": 225,
  "contexts": 12,
  "missing": 0,
  "extra": 0,
  "exact": true
}
```

Official TS SHA-256:

```text
82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257
```

## Final strict QM and direct QTranslator audit

Literal command:

```powershell
uv run pyside6-lrelease translations\probability_calibration_tool_zh_CN.ts -qm C:\Users\rxy71\AppData\Local\Temp\pct-step6-final\probability_calibration_tool_zh_CN.qm -fail-on-unfinished -fail-on-invalid
```

Exit: 0; stderr: empty.

```text
Updating 'C:\Users\rxy71\AppData\Local\Temp\pct-step6-final\probability_calibration_tool_zh_CN.qm'...
    Generated 225 translation(s) (225 finished and 0 unfinished)
```

Literal direct-audit command:

```powershell
uv run python -c "import hashlib, PySide6; from pathlib import Path; from PySide6.QtCore import QLibraryInfo, QTranslator, qVersion; from tests.localization.step5_support import load_catalog; qm=Path(r'C:\Users\rxy71\AppData\Local\Temp\pct-step6-final\probability_calibration_tool_zh_CN.qm'); units=load_catalog()[1]; translator=QTranslator(); loaded=translator.load(str(qm),'','',''); matched=sum(translator.translate(unit.context,unit.source)==unit.translation for unit in units); print({'loaded':loaded,'matched':matched,'total':len(units),'size':qm.stat().st_size,'sha256':hashlib.sha256(qm.read_bytes()).hexdigest(),'PySide6':PySide6.__version__,'Qt':qVersion(),'qt_translations':QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)}); raise SystemExit(0 if loaded and matched==len(units)==225 else 1)"
```

Exit: 0

```text
{'loaded': True, 'matched': 225, 'total': 225, 'size': 19429, 'sha256': '712747514fccce8f3f5e610dbdddf07187f9167b22d33365f97ca06a4d9b5547', 'PySide6': '6.11.2', 'Qt': '6.11.2', 'qt_translations': 'C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/.venv/Lib/site-packages/PySide6/translations'}
```

## Automated test gates

Step 6-specific:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; uv run pytest tests/localization/test_bilingual_business_parity.py tests/localization/test_bilingual_failure_parity.py tests/localization/test_localization_drift_guardrails.py -q
```

Final rerun exit 0: `29 passed in 3.56s`; failed/errors/skipped/xfailed/xpassed = 0/0/0/0/0.

Architecture/static:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; uv run pytest tests/localization/test_architecture.py tests/localization/test_presentation_architecture.py tests/localization/test_localization_drift_guardrails.py -q
```

Final rerun exit 0: `44 passed in 6.19s`; failed/errors/skipped/xfailed/xpassed = 0/0/0/0/0.

All localization:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; uv run pytest tests/localization -q
```

Final rerun exit 0: `327 passed in 21.10s`; failed/errors/skipped/xfailed/xpassed = 0/0/0/0/0.

The final rerun of those three gates was issued as one literal PowerShell line after strengthening the production `report_unexpected` call-count evidence:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; uv run pytest tests/localization/test_bilingual_business_parity.py tests/localization/test_bilingual_failure_parity.py tests/localization/test_localization_drift_guardrails.py -q; uv run pytest tests/localization/test_architecture.py tests/localization/test_presentation_architecture.py tests/localization/test_localization_drift_guardrails.py -q; uv run pytest tests/localization -q
```

Full suite:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; uv run pytest
```

Final rerun exit 0: `1340 passed in 109.48s (0:01:49)`; failed/errors/skipped/xfailed/xpassed = 0/0/0/0/0.

## Schema gate

Final literal command:

```powershell
$env:PYTHONPATH='src'; uv run python -c 'from pathlib import Path; from probability_calibration_tool.persistence.database import create_connection; from probability_calibration_tool.persistence.migrations import ensure_schema; path=Path(r"C:\Users\rxy71\AppData\Local\Temp\pct-step6-final\schema-gate.db"); connection=create_connection(path); ensure_schema(connection); version=connection.execute("PRAGMA user_version").fetchone()[0]; tables=tuple(row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type=\"table\" AND name NOT LIKE \"sqlite_%\" ORDER BY name")); columns={table:tuple(row[1] for row in connection.execute(f"PRAGMA table_info({table})")) for table in tables}; forbidden={name for names in columns.values() for name in names if name in {"language","locale","translation","localized"}}; print({"user_version":version,"tables":tables,"localization_columns":sorted(forbidden)}); connection.close(); raise SystemExit(0 if version==1 and tables==("character_stats","characters","history_regimes","meta","round_analysis_snapshots","rounds") and not forbidden else 1)'
```

Exit: 0

```text
{'user_version': 1, 'tables': ('character_stats', 'characters', 'history_regimes', 'meta', 'round_analysis_snapshots', 'rounds'), 'localization_columns': []}
```

## Ruff and Git whitespace gate

```powershell
uv run ruff check .
```

Exit 0: `All checks passed!`

```powershell
uv run ruff format --check .
```

Final rerun exit 0: `230 files already formatted`

```powershell
git diff --check
```

Exit 0; stdout/stderr empty.

The final combined rerun was also executed literally as:

```powershell
uv run ruff check .; uv run ruff format --check .; git diff --check
```

It returned `All checks passed!`, `230 files already formatted`, and no `git diff --check` output.

## Final Git evidence

Literal commands:

```powershell
git status --short
git diff --stat
git rev-parse HEAD
```

Final HEAD:

```text
00bd24b9fdc509809962ace4412b1e233b7c6598
```

Final `git diff --stat` (untracked files are not represented by Git in this statistic):

```text
45 files changed, 711 insertions(+), 258 deletions(-)
```

Final `git status --short`:

```text
 M src/probability_calibration_tool/application/_checks.py
 M src/probability_calibration_tool/application/analysis_builder.py
 M src/probability_calibration_tool/application/backup_catalog_service.py
 M src/probability_calibration_tool/application/correction_query_service.py
 M src/probability_calibration_tool/application/correction_service.py
 M src/probability_calibration_tool/application/desktop_session.py
 M src/probability_calibration_tool/application/errors.py
 M src/probability_calibration_tool/application/recovery_service.py
 M src/probability_calibration_tool/application/reliability_views.py
 M src/probability_calibration_tool/application/restore_service.py
 M src/probability_calibration_tool/application/startup_service.py
 M src/probability_calibration_tool/application/workflow.py
 M src/probability_calibration_tool/bootstrap.py
 M src/probability_calibration_tool/core/errors.py
 M src/probability_calibration_tool/core/subjective.py
 M src/probability_calibration_tool/core/validation.py
 M src/probability_calibration_tool/desktop_host.py
 M src/probability_calibration_tool/infrastructure/backup.py
 M src/probability_calibration_tool/infrastructure/error_reporting.py
 M src/probability_calibration_tool/infrastructure/restore_engine.py
 M src/probability_calibration_tool/persistence/repositories/rounds.py
 M src/probability_calibration_tool/ui/analysis_panel.py
 M src/probability_calibration_tool/ui/banners.py
 M src/probability_calibration_tool/ui/character_matrix.py
 M src/probability_calibration_tool/ui/close_guard.py
 M src/probability_calibration_tool/ui/correction_page.py
 M src/probability_calibration_tool/ui/desktop_boundary.py
 M src/probability_calibration_tool/ui/desktop_window.py
 M src/probability_calibration_tool/ui/formatting.py
 M src/probability_calibration_tool/ui/main_window.py
 M src/probability_calibration_tool/ui/maintenance_page.py
 M src/probability_calibration_tool/ui/post_run_panel.py
 M src/probability_calibration_tool/ui/pre_run_panel.py
 M src/probability_calibration_tool/ui/presentation.py
 M src/probability_calibration_tool/ui/recovery_page.py
 M src/probability_calibration_tool/ui/restore_page.py
 M src/probability_calibration_tool/ui/round_page.py
 M src/probability_calibration_tool/ui/safety_window.py
 M src/probability_calibration_tool/ui/startup_pages.py
 M tests/integration/desktop/test_compound_failure_priority.py
 M tests/integration/desktop/test_correction_integration.py
 M tests/integration/infrastructure/test_logging.py
 M tests/ui/conftest.py
 M tests/ui/test_startup_pages.py
 M tests/ui/test_workflow_contract.py
?? outputs/localization_step3_completion_report.md
?? outputs/localization_step3_validation_commands.md
?? outputs/localization_step4_completion_report.md
?? outputs/localization_step4_rework_report.md
?? outputs/localization_step4_rework_validation.md
?? outputs/localization_step4_validation_commands.md
?? outputs/localization_step5_completion_report.md
?? outputs/localization_step5_rework_report.md
?? outputs/localization_step5_rework_validation.md
?? outputs/localization_step5_translation_inventory.md
?? outputs/localization_step5_validation_commands.md
?? outputs/localization_step6_completion_report.md
?? outputs/localization_step6_qa_matrix.md
?? outputs/localization_step6_validation_commands.md
?? src/probability_calibration_tool/localization.py
?? src/probability_calibration_tool/ui/language_dialog.py
?? src/probability_calibration_tool/ui/localization.py
?? tests/localization/
?? tools/localization_step5_inventory.py
?? translations/
```

No reset, checkout, commit, or tag command was executed.

## Final protected hash comparison

The same literal protected-hash command from the Baseline section was rerun and compared by exact project-relative key and SHA-256 value.

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

## Development failures retained

- Initial focused lint reported formatting/import issues in the new tests; those tests were formatted and imports corrected. No production file changed.
- Initial business-parity run was `8 failed, 8 passed`. The first-difference oracle showed only the non-injectable `character_stats.updated_at` wall-clock value. The comparator was corrected with the contract-permitted, explicitly documented single timestamp normalization; business IDs/values were not normalized. The next run was `16 passed`.
- Initial failure-parity lint found one unused test-helper import while the tests themselves were `8 passed`; the import was removed.
- An intermediate all-localization run was `327 passed` while format check still identified one newly added file; that file was formatted before final gates.
- Two schema one-liner attempts failed before execution of the gate: first due PowerShell quoting, then due missing `PYTHONPATH`. The final literal command above used `PYTHONPATH=src` and passed. These were command-construction errors, not product/schema failures.
- An early byte-level comparison of a freshly extracted untranslated TS candidate and the translated official TS differed, as expected. Final comparison correctly uses semantic source/context/numerus keys and passed 225/225 with missing=0 and extra=0.

No frozen-stage production defect was discovered.
