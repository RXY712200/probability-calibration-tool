# Localization Step 5 Narrow Rework Validation

## Baseline

Commands:

```powershell
git status --short
git rev-parse HEAD
Get-FileHash -Algorithm SHA256 <every file under src, plus SPEC_1.0.md, pyproject.toml, uv.lock, and packaging>
```

Results: accepted dirty Step 3–5 tree recorded; HEAD `00bd24b9fdc509809962ace4412b1e233b7c6598`; 181 protected files hashed before rework.

## Focused translation checks

Command:

```powershell
uv run ruff format tests/localization/test_step5_catalog.py
uv run ruff check tests/localization/test_step5_catalog.py
uv run pytest tests/localization/test_step5_catalog.py -q
```

Results: one edited test file formatted; Ruff passed; pytest exit 0, 5 passed in 0.98s. The exact map contains 135 keys, the frozen Errors map 23, and character/header checks 36, for 194 literal frozen-Chinese assertions.

Command:

```powershell
uv run python tools/localization_step5_inventory.py translations/probability_calibration_tool_zh_CN.ts outputs/localization_step5_translation_inventory.md
```

Result: exit 0; inventory regenerated from final TS; active units 225; contexts 12; represented TS SHA-256 `82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257`.

## Runtime and regression tests

Command:

```powershell
uv run pytest tests/localization/test_step5_runtime.py -q
```

Result: exit 0; 5 passed in 0.99s; failed/errors/skipped/xfailed/xpassed all 0.

Command:

```powershell
uv run pytest tests/localization -q
```

Result: exit 0; 298 passed in 16.08s; failed/errors/skipped/xfailed/xpassed all 0.

Command:

```powershell
uv run pytest
```

Result: exit 0; collected 1311; 1311 passed in 108.44s; failed 0, errors 0, skipped 0, xfailed 0, xpassed 0.

## Fresh production extraction

Command:

```powershell
uv run pyside6-lupdate -extensions py src -ts C:\Users\rxy71\AppData\Local\Temp\pct-step5-rework-final-2e59139053d246efa2efb8e72ac8dc8f\production-extraction.ts
```

Result: exit 0; `Found 225 source text(s)`; production active 225; official active 225; exactly 12 contexts; missing 0; extra 0; key equality true.

## Strict candidate rebuild

The prior exact-name generated candidate was moved to a unique OS-temporary path, proving the build target absent before compilation.

Command:

```powershell
uv run pyside6-lrelease translations/probability_calibration_tool_zh_CN.ts -qm build/localization/probability_calibration_tool_zh_CN.qm -fail-on-unfinished -fail-on-invalid
```

Result: exit 0.

Stdout:

```text
Updating 'build/localization/probability_calibration_tool_zh_CN.qm'...
    Generated 225 translation(s) (225 finished and 0 unfinished)
```

Stderr: empty.

- TS SHA-256: `82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257`
- QM SHA-256: `712747514fccce8f3f5e610dbdddf07187f9167b22d33365f97ca06a4d9b5547`
- QM size: 19,429 bytes

## Direct catalog/QTranslator audit

Command:

```powershell
uv run python - <final TS/QM integrity and direct-QTranslator audit>
```

Result: exit 0:

```text
ACTIVE=225
CONTEXT_COUNT=12
UNFINISHED=0
EMPTY=0
WHITESPACE_ONLY=0
VANISHED=0
OBSOLETE=0
DUPLICATES=0
NUMERUS=0
PLACEHOLDER_MISMATCH=0
NFC=True
QM_LOAD=True
QM_EMPTY=False
QM_LANGUAGE=zh_CN
QM_EXACT_MATCHES=225/225
PRE_RESTORE_EXACT=True
OVER_RETENTION_EXACT=True
```

## Step 3 runtime smoke

Command:

```powershell
$env:PYTHONPATH='src'; $env:QT_QPA_PLATFORM='offscreen'; uv run python - <isolated final-candidate preflight/init and 12-context smoke>
```

Result: exit 0:

```text
PREFLIGHT=valid
PREFERRED=zh_CN
EFFECTIVE=zh_CN
AVAILABLE=en,zh_CN
FALLBACK=none
APP_TRANSLATOR_OWNED=True
QT_TRANSLATION_STATUS=loaded
CONTEXT_SMOKE=12/12
```

The permanent runtime tests also passed the real widget smoke, canonical English fallback, and Preferred zh_CN with missing-pack fallback.

## Schema and static checks

Commands and results:

```powershell
$env:PYTHONPATH='src'; uv run python - <isolated ensure_schema and SQLite inspection>
# PRAGMA user_version=1
# TABLE_COUNT=6
# TABLES=character_stats,characters,history_regimes,meta,round_analysis_snapshots,rounds
# exit 0

uv run ruff check .
# All checks passed!; exit 0

uv run ruff format --check .
# 221 files already formatted; exit 0

git diff --check
# no output; exit 0
```

## Protected-file comparison

Command:

```powershell
Get-FileHash -Algorithm SHA256 <the same 181 protected files captured before rework>
```

Result: baseline 181; final 181; missing 0; added 0; changed 0; unchanged true.

## Final Git/scope commands

```powershell
git status --short
git diff --stat
git rev-parse HEAD
```

Final HEAD remained `00bd24b9fdc509809962ace4412b1e233b7c6598`. No reset, checkout, commit, tag, production-source change, packaging/version change, or Step 6–9 work occurred. The original rejected Step 5 completion and validation reports were not modified.
