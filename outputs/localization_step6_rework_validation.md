# Localization Step 6 Narrow Rework Validation

## Baseline

Working directory:

`C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability`

```powershell
git status --short
git rev-parse HEAD
```

- Baseline HEAD: `00bd24b9fdc509809962ace4412b1e233b7c6598`
- Baseline protected files: 182.
- Baseline official TS SHA-256: `82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257`.
- The working tree already contained the uncommitted/untracked accepted Step 3–6 implementation and evidence. This rework preserves that state and only changes the files listed in the rework report.

## Focused rework gates

Literal final command:

```powershell
uv run ruff format --check tests/localization/test_bilingual_business_parity.py tests/localization/test_bilingual_failure_parity.py; uv run ruff check tests/localization/test_bilingual_business_parity.py tests/localization/test_bilingual_failure_parity.py; $env:PYTHONDONTWRITEBYTECODE='1'; uv run pytest tests/localization/test_bilingual_business_parity.py::test_p10_p11_formal_bilingual_restore_parity tests/localization/test_bilingual_failure_parity.py::test_p12_formal_bilingual_expected_validation_and_business_failure_parity tests/localization/test_bilingual_failure_parity.py::test_p13_formal_bilingual_unknown_and_stale_failure_parity tests/localization/test_bilingual_failure_parity.py::test_p14_formal_bilingual_commit_then_presentation_failure_is_never_retried -q; uv run pytest tests/localization/test_bilingual_business_parity.py tests/localization/test_bilingual_failure_parity.py tests/localization/test_localization_drift_guardrails.py -q
```

Exit 0:

```text
2 files already formatted
All checks passed!
10 passed in 2.80s
29 passed in 7.41s
```

All non-pass pytest categories: 0.

## Architecture and localization gates

Literal command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; uv run pytest tests/localization/test_architecture.py tests/localization/test_presentation_architecture.py tests/localization/test_localization_drift_guardrails.py -q; uv run pytest tests/localization -q
```

Exit 0:

```text
44 passed in 2.23s
327 passed in 19.70s
```

All non-pass pytest categories: 0.

## Full regression

Literal command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; uv run pytest
```

Exit 0:

```text
collected 1340 items
1340 passed in 108.79s (0:01:48)
```

Failed/errors/skipped/xfailed/xpassed: 0/0/0/0/0.

## Fresh production extraction

Literal command:

```powershell
$ErrorActionPreference='Stop'
$finalRoot='C:\Users\rxy71\AppData\Local\Temp\pct-step6-rework-final'
if(-not(Test-Path -LiteralPath $finalRoot)){New-Item -ItemType Directory -Path $finalRoot|Out-Null}
uv run pyside6-lupdate -extensions py src -ts C:\Users\rxy71\AppData\Local\Temp\pct-step6-rework-final\probability_calibration_tool_zh_CN.ts
[xml]$official=Get-Content -LiteralPath 'translations\probability_calibration_tool_zh_CN.ts' -Raw -Encoding UTF8
[xml]$fresh=Get-Content -LiteralPath 'C:\Users\rxy71\AppData\Local\Temp\pct-step6-rework-final\probability_calibration_tool_zh_CN.ts' -Raw -Encoding UTF8
$officialKeys=@($official.TS.context|ForEach-Object{$context=[string]$_.name;@($_.message)|ForEach-Object{"$context`u{001F}$([string]$_.source)`u{001F}$([string]$_.numerus)"}})
$freshKeys=@($fresh.TS.context|ForEach-Object{$context=[string]$_.name;@($_.message)|ForEach-Object{"$context`u{001F}$([string]$_.source)`u{001F}$([string]$_.numerus)"}})
$missing=@($officialKeys|Where-Object{$_ -notin $freshKeys})
$extra=@($freshKeys|Where-Object{$_ -notin $officialKeys})
$contexts=@($fresh.TS.context|ForEach-Object{[string]$_.name}|Sort-Object -Unique)
[ordered]@{official_active=$officialKeys.Count;production_active=$freshKeys.Count;contexts=$contexts.Count;missing=$missing.Count;extra=$extra.Count;exact=($missing.Count-eq 0-and $extra.Count-eq 0-and $officialKeys.Count-eq 225-and $freshKeys.Count-eq 225)}|ConvertTo-Json
if($missing.Count-ne 0-or $extra.Count-ne 0){exit 1}
```

Exit 0:

```text
Found 225 source text(s) (225 new and 0 already existing)
official_active: 225
production_active: 225
contexts: 12
missing: 0
extra: 0
exact: true
```

## Strict QM and direct QTranslator

Literal command:

```powershell
uv run pyside6-lrelease translations\probability_calibration_tool_zh_CN.ts -qm C:\Users\rxy71\AppData\Local\Temp\pct-step6-rework-final\probability_calibration_tool_zh_CN.qm -fail-on-unfinished -fail-on-invalid; uv run python -c "import hashlib, PySide6; from pathlib import Path; from PySide6.QtCore import QTranslator, qVersion; from tests.localization.step5_support import load_catalog; qm=Path(r'C:\Users\rxy71\AppData\Local\Temp\pct-step6-rework-final\probability_calibration_tool_zh_CN.qm'); units=load_catalog()[1]; translator=QTranslator(); loaded=translator.load(str(qm),'','',''); matched=sum(translator.translate(unit.context,unit.source)==unit.translation for unit in units); print({'loaded':loaded,'matched':matched,'total':len(units),'size':qm.stat().st_size,'sha256':hashlib.sha256(qm.read_bytes()).hexdigest(),'ts_sha256':hashlib.sha256(Path('translations/probability_calibration_tool_zh_CN.ts').read_bytes()).hexdigest(),'PySide6':PySide6.__version__,'Qt':qVersion()}); raise SystemExit(0 if loaded and matched==len(units)==225 else 1)"
```

Exit 0:

```text
Generated 225 translation(s) (225 finished and 0 unfinished)
loaded=True; matched=225; total=225
QM size=19429
QM SHA-256=712747514fccce8f3f5e610dbdddf07187f9167b22d33365f97ca06a4d9b5547
TS SHA-256=82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257
PySide6=6.11.2; Qt=6.11.2
```

## Schema

Literal command:

```powershell
$env:PYTHONPATH='src'; uv run python -c 'from pathlib import Path; from probability_calibration_tool.persistence.database import create_connection; from probability_calibration_tool.persistence.migrations import ensure_schema; path=Path(r"C:\Users\rxy71\AppData\Local\Temp\pct-step6-rework-final\schema-gate.db"); connection=create_connection(path); ensure_schema(connection); version=connection.execute("PRAGMA user_version").fetchone()[0]; tables=tuple(row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type=\"table\" AND name NOT LIKE \"sqlite_%\" ORDER BY name")); columns={table:tuple(row[1] for row in connection.execute(f"PRAGMA table_info({table})")) for table in tables}; forbidden={name for names in columns.values() for name in names if name in {"language","locale","translation","localized"}}; print({"user_version":version,"tables":tables,"localization_columns":sorted(forbidden)}); connection.close(); raise SystemExit(0 if version==1 and tables==("character_stats","characters","history_regimes","meta","round_analysis_snapshots","rounds") and not forbidden else 1)'
```

Exit 0:

```text
{'user_version': 1, 'tables': ('character_stats', 'characters', 'history_regimes', 'meta', 'round_analysis_snapshots', 'rounds'), 'localization_columns': []}
```

## Ruff and Git whitespace

```powershell
uv run ruff check .
uv run ruff format --check .
git diff --check
```

Results:

```text
All checks passed!
232 files already formatted
git diff --check: exit 0, no output
```

## Protected scope

The baseline protected-hash command was rerun against every file under `src/`, `SPEC_1.0.md`, `pyproject.toml`, `uv.lock`, `packaging/`, optional `installer/`, and the official TS.

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

## Development history

- The first focused run already passed all strengthened P10–P14 tests (`10 passed`) but Ruff identified one unused `asdict` import left from the replaced manual P14 helper. The import was removed; no production file changed.
- No product failure or frozen-stage defect was encountered.

## Final Git evidence

```powershell
git status --short
git diff --stat
git rev-parse HEAD
```

- Final HEAD: `00bd24b9fdc509809962ace4412b1e233b7c6598` (unchanged).
- Final status includes the pre-existing accepted localization work plus the two new rework reports; `tests/localization/` remains an untracked directory at Git's summary level, so its two modified rework test files are documented by exact path in the rework report.
- Final `git diff --stat`: `45 files changed, 711 insertions(+), 258 deletions(-)`; this is the pre-existing tracked localization work because Git does not include untracked Step 3–6 files in that statistic.
- Reset/checkout/commit/tag: none.

Final status: `STEP 6 NARROW REWORK COMPLETE — READY FOR EXTERNAL RE-REVIEW`
