# Localization Step 7 Manual Acceptance Contract Rebaseline Validation

Status: `STEP 7 MANUAL ACCEPTANCE CONTRACT REBASELINED TO 150% — READY FOR EXTERNAL REVIEW`

All commands ran from the project root. Preparation, probes, and offscreen checks validate mechanics only; human visual acceptance remains paused.

## Contract and safety gates

```powershell
uv run python tools/localization_step7_prepare.py traceability-check
uv run python tools/localization_step7_prepare.py safety-check
```

Both exited 0. Traceability returned:

```text
checklist_rows=212
unique_ids=212
MANDATORY=204
N/A_ALLOWED=8
NOT_RUN=212
PASS=0
FAIL=0
selected_NA=0
formal_scaling=150%
legacy_100_routes=0
legacy_125_routes=0
deleted_dpi_ids_present=0
```

It also retained 204/204 mandatory traceability, 26/26 critical bilingual Effective=en + Effective=zh_CN routing, fallback-not-counted-as-zh_CN, CR-SAFE-03, and CR-SAFE-04 checks. Safety reported all eight refusal/containment checks true.

## Preparation and representative probes

```powershell
uv run ruff format tools/localization_step7_prepare.py
uv run python tools/localization_step7_prepare.py compile-qm
uv run python tools/localization_step7_prepare.py prepare all
$probes=@('healthy_en','healthy_zh','correction_en','correction','restore_normal_en','restore_normal','recovery_localization_fallback','data_safety_en','data_safety'); foreach($scenario in $probes){uv run python tools/localization_step7_prepare.py probe $scenario *> $null;if($LASTEXITCODE -ne 0){throw "probe failed: $scenario"};"probe PASS $scenario"}
```

All exited 0. All nine probes passed; 45 scenario roots were rebuilt. The strict official-QM audit reported 225 active/finished, 0 unfinished, QTranslator loaded, 225 matches, 19,429 bytes, and SHA-256 `712747514fccce8f3f5e610dbdddf07187f9167b22d33365f97ca06a4d9b5547`.

## Fresh extraction

```powershell
$target=(Resolve-Path -LiteralPath 'outputs/localization_step7_runtime/_qa_artifacts').Path + '\fresh_production_extraction.ts'
$approved=(Resolve-Path -LiteralPath 'outputs/localization_step7_runtime/_qa_artifacts').Path
if([IO.Path]::GetDirectoryName($target) -ne $approved){throw 'Fresh extraction target escaped QA artifacts.'}
if(Test-Path -LiteralPath $target){Remove-Item -LiteralPath $target}
uv run pyside6-lupdate -extensions py src -ts outputs/localization_step7_runtime/_qa_artifacts/fresh_production_extraction.ts
uv run python -c "import xml.etree.ElementTree as E; from pathlib import Path; key=lambda p:{(c.findtext('name'),m.findtext('source') or '',m.get('numerus','')) for c in E.parse(p).getroot().findall('context') for m in c.findall('message') if (m.find('translation') is None or m.find('translation').get('type') not in {'obsolete','vanished'})}; a=key(Path('translations/probability_calibration_tool_zh_CN.ts')); b=key(Path('outputs/localization_step7_runtime/_qa_artifacts/fresh_production_extraction.ts')); contexts={x[0] for x in b}; print({'official_active':len(a),'production_active':len(b),'contexts':len(contexts),'missing':len(a-b),'extra':len(b-a)}); raise SystemExit(0 if len(a)==len(b)==225 and len(contexts)==12 and a==b else 1)"
```

Result: 225 new source texts; official_active=225, production_active=225, contexts=12, missing=0, extra=0.

## Regression

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest tests/localization/test_bilingual_business_parity.py tests/localization/test_bilingual_failure_parity.py tests/localization/test_localization_drift_guardrails.py -q
```

Result: `29 passed in 4.45s`.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest tests/localization/test_architecture.py tests/localization/test_presentation_architecture.py tests/localization/test_localization_drift_guardrails.py -q
```

Result: `44 passed in 2.57s`.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest tests/localization -q
```

Result: `327 passed in 22.68s`.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest
```

Result: `1340 passed in 107.95s (0:01:47)`.

For all pytest commands: failed=0, errors=0, skipped=0, xfailed=0, xpassed=0.

## Schema and static checks

```powershell
$env:PYTHONPATH='src'
uv run python -c 'from pathlib import Path; from probability_calibration_tool.persistence.database import create_connection; from probability_calibration_tool.persistence.migrations import ensure_schema; path=Path(r"outputs/localization_step7_runtime/_qa_artifacts/schema_gate.db"); path.unlink(missing_ok=True); c=create_connection(path); ensure_schema(c); version=c.execute("PRAGMA user_version").fetchone()[0]; tables=tuple(r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type=''table'' AND name NOT LIKE ''sqlite_%'' ORDER BY name")); columns={t:tuple(r[1] for r in c.execute(f"PRAGMA table_info({t})")) for t in tables}; forbidden=sorted({n for names in columns.values() for n in names if n in {"language","locale","translation","localized"}}); print({"user_version":version,"tables":tables,"localization_columns":forbidden}); c.close(); raise SystemExit(0 if version==1 and tables==("character_stats","characters","history_regimes","meta","round_analysis_snapshots","rounds") and not forbidden else 1)'
uv run ruff check .
uv run ruff format --check .
git diff --check
```

Results: schema user_version=1 with the expected six tables and no localization business columns; Ruff check passed; final format check reported 251 files already formatted; Git whitespace check exited 0 with no output.

## Protected scope

Protected before/after: 340 files; normalized aggregate SHA-256 unchanged:

`d5e2e732833744864a1bc675aae29f2e8f35e7dbccfff6a41867f00299b036df` → `d5e2e732833744864a1bc675aae29f2e8f35e7dbccfff6a41867f00299b036df`

Production code changes=0; protected changes=0; all prior preparation/rework reports remained unchanged.

## Boundary

- Human 150% formal acceptance has NOT resumed.
- All 212 formal rows are NOT_RUN.
- Prior 100% observation is out of scope; no PASS is carried forward.
- Step 7 completion report is absent.
- Step 8 and Step 9 are NOT started.
- No commit/tag/push/reset/checkout/release/distribution build occurred.
