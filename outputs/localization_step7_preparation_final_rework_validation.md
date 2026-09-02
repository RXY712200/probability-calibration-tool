# Localization Step 7 Manual Acceptance Preparation Final Consistency Rework Validation

Status: `STEP 7 MANUAL ACCEPTANCE PREPARATION FINAL CONSISTENCY REWORK COMPLETE — READY FOR EXTERNAL FINAL REVIEW`

All commands ran from the project root. Offscreen launches validate mechanics only; they are not human visual acceptance.

## Traceability and safety

```powershell
uv run python tools/localization_step7_prepare.py traceability-check
uv run python tools/localization_step7_prepare.py safety-check
```

Both exited 0. Traceability reported 235 rows/235 unique IDs, 227 mandatory, 8 N/A-allowed, 235 NOT_RUN, 0 PASS/FAIL/selected-N/A, 227/227 mandatory traceability, 26/26 critical bilingual routes, and 18/18 Effective=zh_CN DPI routes. Safety reported all eight refusal/containment checks true and used then removed an isolated junction.

## Tool and scenario preparation

```powershell
uv run ruff format tools/localization_step7_prepare.py
uv run python -m py_compile tools/localization_step7_prepare.py
uv run python tools/localization_step7_prepare.py --help
uv run python tools/localization_step7_prepare.py compile-qm
uv run python tools/localization_step7_prepare.py prepare all
$probes=@('healthy_en','healthy_zh','correction_en','correction','restore_normal_en','restore_normal','recovery_localization_fallback','data_safety_en','data_safety'); foreach($scenario in $probes){ uv run python tools/localization_step7_prepare.py probe $scenario *> $null; if($LASTEXITCODE -ne 0){throw "probe failed: $scenario"}; "probe PASS $scenario" }
```

All exited 0. Exactly 45 scenarios were rebuilt. All nine representative probes passed. The strict QM audit reported 225 active/finished, 0 unfinished, QTranslator loaded, 225/225 matches, 19,429 bytes, and SHA-256 `712747514fccce8f3f5e610dbdddf07187f9167b22d33365f97ca06a4d9b5547`.

## Affected real-entrypoint and fault smokes

```powershell
$smokes=@('recovery_zh','recovery_no_pending_zh','multiple_pending_zh','data_safety_en','data_safety','data_safety_fallback','data_safety_warning_en','data_safety_warning_zh','correction_en','restore_normal_en','unexpected_warning_en','unexpected_warning_zh','save_failure','unexpected_en','unexpected_zh','backup_warning','recovery_stale_en','recovery_stale_zh','correction_warning_en','correction_warning_zh','over_retention_en','over_retention_zh','quarantine_warning_en','quarantine_warning_zh'); foreach($scenario in $smokes){ uv run python tools/localization_step7_prepare.py smoke-launch $scenario *> $null; if($LASTEXITCODE -ne 0){throw "smoke failed: $scenario"}; "smoke PASS $scenario" }; uv run python tools/localization_step7_prepare.py probe-save-failure *> $null; if($LASTEXITCODE -ne 0){throw 'probe-save-failure failed'}; 'probe-save-failure PASS'
```

All 24 smoke launches and the save-failure probe exited 0. A final `uv run python tools/localization_step7_prepare.py prepare all` restored the 45 scenario roots to clean initial state.

## Fresh extraction

```powershell
$target=(Resolve-Path -LiteralPath 'outputs/localization_step7_runtime/_qa_artifacts').Path + '\fresh_production_extraction.ts'
$approved=(Resolve-Path -LiteralPath 'outputs/localization_step7_runtime/_qa_artifacts').Path
if([IO.Path]::GetDirectoryName($target) -ne $approved){throw 'Fresh extraction target escaped QA artifacts.'}
if(Test-Path -LiteralPath $target){Remove-Item -LiteralPath $target}
uv run pyside6-lupdate -extensions py src -ts outputs/localization_step7_runtime/_qa_artifacts/fresh_production_extraction.ts
uv run python -c "import xml.etree.ElementTree as E; from pathlib import Path; key=lambda p:{(c.findtext('name'),m.findtext('source') or '',m.get('numerus','')) for c in E.parse(p).getroot().findall('context') for m in c.findall('message') if (m.find('translation') is None or m.find('translation').get('type') not in {'obsolete','vanished'})}; a=key(Path('translations/probability_calibration_tool_zh_CN.ts')); b=key(Path('outputs/localization_step7_runtime/_qa_artifacts/fresh_production_extraction.ts')); contexts={x[0] for x in b}; print({'official_active':len(a),'production_active':len(b),'contexts':len(contexts),'missing':len(a-b),'extra':len(b-a)}); raise SystemExit(0 if len(a)==len(b)==225 and len(contexts)==12 and a==b else 1)"
```

Result: 225 source texts, 225 new, 0 existing; official_active=225, production_active=225, contexts=12, missing=0, extra=0.

## Regression

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest tests/localization/test_bilingual_business_parity.py tests/localization/test_bilingual_failure_parity.py tests/localization/test_localization_drift_guardrails.py -q
```

Result: `29 passed in 4.28s`.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest tests/localization/test_architecture.py tests/localization/test_presentation_architecture.py tests/localization/test_localization_drift_guardrails.py -q
```

Result: `44 passed in 3.17s`.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest tests/localization -q
```

Result: `327 passed in 24.11s`.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest
```

Result: `1340 passed in 116.99s (0:01:56)`.

For all four pytest commands: failed=0, errors=0, skipped=0, xfailed=0, xpassed=0. No accepted test was added, deleted, skipped, xfailed, or weakened.

## Schema

```powershell
$env:PYTHONPATH='src'
uv run python -c 'from pathlib import Path; from probability_calibration_tool.persistence.database import create_connection; from probability_calibration_tool.persistence.migrations import ensure_schema; path=Path(r"outputs/localization_step7_runtime/_qa_artifacts/schema_gate.db"); path.unlink(missing_ok=True); c=create_connection(path); ensure_schema(c); version=c.execute("PRAGMA user_version").fetchone()[0]; tables=tuple(r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type=''table'' AND name NOT LIKE ''sqlite_%'' ORDER BY name")); columns={t:tuple(r[1] for r in c.execute(f"PRAGMA table_info({t})")) for t in tables}; forbidden=sorted({n for names in columns.values() for n in names if n in {"language","locale","translation","localized"}}); print({"user_version":version,"tables":tables,"localization_columns":forbidden}); c.close(); raise SystemExit(0 if version==1 and tables==("character_stats","characters","history_regimes","meta","round_analysis_snapshots","rounds") and not forbidden else 1)'
```

Result: user_version=1; exact six production tables; localization_columns=[].

## Static and Git whitespace

```powershell
uv run ruff check .
uv run ruff format --check .
git diff --check
```

Final results: all exited 0; Ruff check printed `All checks passed!`; format check printed `249 files already formatted`; Git whitespace check produced no output.

## Protected scope and preserved reports

Protected before/after count: 340/340. Normalized aggregate SHA-256:

`d5e2e732833744864a1bc675aae29f2e8f35e7dbccfff6a41867f00299b036df` → `d5e2e732833744864a1bc675aae29f2e8f35e7dbccfff6a41867f00299b036df`

Preserved report SHA-256 values:

- `outputs/localization_step7_preparation_report.md`: `d5013f88ceb0fa793640019613c9accd876b20a8bb0640ddd5f66d1ec7d13a0a`
- `outputs/localization_step7_preparation_validation.md`: `a8677a68bb7852d5c3cb62e9bcce2b46e78b45b91f623abf9f4e359d500c3972`
- `outputs/localization_step7_preparation_rework_report.md`: `64e9ed48ad306919c3ffb416378103a00be6c91aa9fe54abdc4861450cb39373`
- `outputs/localization_step7_preparation_rework_validation.md`: `aaee11dce88394d9a718228a45e0a0ed528b0b6afb5eff298b400883dac1cdb5`

Production code changes: 0. Official TS, SPEC, dependencies, packaging, schema/version, business logic, accepted Step 3–6 assets, and prior reports were unchanged.

## Boundary

- Human visual acceptance: NOT performed.
- All 235 checklist rows: NOT_RUN.
- Screenshots judged PASS: 0.
- Step 7 completion report: absent.
- Step 8: NOT started.
- Step 9: NOT started.
- Commit/tag/push/reset/checkout/release/distribution build: none.
