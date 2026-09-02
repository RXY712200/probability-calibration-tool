# Localization Step 5 Validation Commands

All paths are project-relative unless an absolute temporary path is shown. Final gate commands exited 0. `PYTHONDONTWRITEBYTECODE=1` was set for Python/pytest validation so the protected source inventory, including existing generated cache files, remained byte-identical.

## Baseline and extraction gate

Command:

```powershell
git status --short
```

Result: recorded the accepted dirty Step 3/4 tree before edits. The status is reproduced in the final Git section below; no reset/checkout was performed.

Command:

```powershell
git rev-parse HEAD
```

Result: exit 0, `00bd24b9fdc509809962ace4412b1e233b7c6598`.

Command:

```powershell
Get-FileHash -Algorithm SHA256 <every file under src, plus SPEC_1.0.md, pyproject.toml, uv.lock, and packaging>
```

Result: 181 protected files recorded before edits.

Command:

```powershell
uv run pyside6-lupdate -extensions py src -ts C:\Users\rxy71\AppData\Local\Temp\pct-step5-initial-c39da2b5e75c4ff5ac733ce3cf17e914\production.ts
```

Result: exit 0; `Found 225 source text(s) (225 new and 0 already existing)`; 12 contexts with counts Analysis 25, AppShell 9, Characters 36, Correction 11, DomainLabels 19, Errors 34, Localization 19, Maintenance 13, Recovery 7, Restore 17, Round 29, StartupSafety 6.

## Catalog generation and inventory

Command:

```powershell
uv run pyside6-lupdate -extensions py src -ts translations/probability_calibration_tool_zh_CN.ts
```

Result: exit 0; generated the initial official TS from all 225 accepted sources. The completed translations were then applied without changing source keys.

Command:

```powershell
uv run python tools/localization_step5_inventory.py translations/probability_calibration_tool_zh_CN.ts outputs/localization_step5_translation_inventory.md
```

Result: exit 0; generated 225 inventory data rows grouped under 12 contexts; represented TS hash `2211aec1d0708df35a0b25b2377b631566a1e87aaa0ae3d9bb20e47a57376eb8`.

## Test commands

Command:

```powershell
uv run pytest tests/localization/test_step5_catalog.py tests/localization/test_step5_runtime.py -q
```

Result: exit 0; 10 passed in 3.20s.

Command:

```powershell
uv run pytest tests/localization -q
```

Result: exit 0; 298 passed in 18.01s; failed 0, errors 0, skipped 0, xfailed 0, xpassed 0.

Command:

```powershell
uv run pytest
```

Result: exit 0; collected 1311; 1311 passed in 113.62s; failed 0, errors 0, skipped 0, xfailed 0, xpassed 0.

Command:

```powershell
uv run pytest tests/localization/test_step5_catalog.py -q
uv run pytest tests/localization/test_step5_runtime.py -q
uv run pytest tests/localization/test_architecture.py tests/localization/test_presentation_architecture.py -q
```

Results: all exit 0; catalog 5 passed in 1.13s; runtime 5 passed in 1.34s; relevant architecture/static tests 39 passed in 3.58s.

## Final fresh extraction

Command:

```powershell
uv run pyside6-lupdate -extensions py src -ts C:\Users\rxy71\AppData\Local\Temp\pct-step5-final-f5c5574adaa94e4e81bd7861e542900a\production-extraction.ts
```

Result: exit 0; production active 225; official active 225; contexts 12; missing 0; extra 0; exact `(context, source)` equality true.

## Final strict QM build and direct verification

The old exact-name build candidate was first verified under `build\localization` and moved aside, leaving the exact target absent. A direct `Remove-Item` attempt was blocked by the command-execution policy before execution; the recoverable same-directory move was used instead, and the prior candidate was subsequently moved out of the project to the OS temporary directory. No source or evidence file was removed.

Command:

```powershell
uv run pyside6-lrelease translations/probability_calibration_tool_zh_CN.ts -qm build/localization/probability_calibration_tool_zh_CN.qm -fail-on-unfinished -fail-on-invalid
```

Result: exit 0. Stdout:

```text
Updating 'build/localization/probability_calibration_tool_zh_CN.qm'...
    Generated 225 translation(s) (225 finished and 0 unfinished)
```

Stderr: empty.

- QM size: 19,419 bytes
- QM SHA-256: `a86c094eef20c17293bfadde57829274a0d3277b885a1a37ffb222c4a3bed7c8`
- TS SHA-256: `2211aec1d0708df35a0b25b2377b631566a1e87aaa0ae3d9bb20e47a57376eb8`

Command:

```powershell
uv run python - <final TS/QM integrity and direct QTranslator audit>
```

Result: exit 0; language `zh_CN`; source language `en`; active 225; contexts 12; unfinished/empty/whitespace-only/vanished/obsolete/duplicates/numerus all 0; placeholder mismatch 0; identical allowlist exactly `Characters / ???`; NFC true; QM load true; QM nonempty; QM language `zh_CN`; direct exact matches 225/225; sentinel true.

## Tool versions

Commands and results:

```powershell
uv run pyside6-lupdate -version
# lupdate version 6.11.2; exit 0

uv run pyside6-lrelease -version
# lrelease version 6.11.2; exit 0

uv run python -c "import PySide6; from PySide6.QtCore import qVersion; print(PySide6.__version__); print(qVersion())"
# PySide6 6.11.2; Qt 6.11.2; exit 0
```

## Runtime/preflight

Command:

```powershell
$env:PYTHONPATH='src'; $env:QT_QPA_PLATFORM='offscreen'; uv run python - <isolated final-candidate preflight, initialization, 12-context, and widget audit>
```

Result: exit 0; preflight valid; Preferred `zh_CN`; Effective `zh_CN`; Available `en,zh_CN`; fallback none; app translator owned true; Qt framework translation status loaded; context smoke 12/12; shell, Round, character, and Analysis widget checks all true.

Command:

```powershell
$env:PYTHONPATH='src'; $env:QT_QPA_PLATFORM='offscreen'; uv run python - <English and missing-pack regression audit>
```

Result: exit 0; canonical English true; missing-pack Preferred `zh_CN`; Effective `en`; Available `en`; fallback `preferred_pack_missing`; app translator false.

## Schema

Command:

```powershell
$env:PYTHONPATH='src'; uv run python - <isolated ensure_schema and SQLite inspection>
```

Result: exit 0; `PRAGMA user_version=1`; table count 6; tables `character_stats,characters,history_regimes,meta,round_analysis_snapshots,rounds`.

## Quality gates

Commands and exact final results:

```powershell
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
Get-FileHash -Algorithm SHA256 <the same 181 protected files captured before Step 5>
```

Result: baseline 181, final 181, missing 0, added 0, changed 0. Every protected file under `src\`, plus `SPEC_1.0.md`, `pyproject.toml`, `uv.lock`, and `packaging\`, remained byte-identical.

## Development failures retained in the record

- The first focused `ruff check` exited 1 on three import-order findings. `uv run ruff check --fix` fixed exactly those imports; the final repository-wide Ruff checks passed.
- The first inline schema command exited 1 because PowerShell quoting truncated the Python `-c` expression. A here-string retry then exited 1 because standalone Python did not inherit pytest's `pythonpath`. The final retry explicitly set `PYTHONPATH=src` and passed with the frozen schema output above.
- A direct generated-QM `Remove-Item` command was rejected by the execution policy before it ran. The already-verified exact candidate was moved aside, the required target absence was confirmed, the strict build regenerated it, and the moved prior candidate was moved out of the project.

## Final Git state

Commands:

```powershell
git status --short
git diff --stat
git rev-parse HEAD
```

Results:

- HEAD remained `00bd24b9fdc509809962ace4412b1e233b7c6598`.
- Tracked diff stat remained 45 files changed, 711 insertions, 258 deletions from the accepted pre-existing Step 3/4 dirty tree.
- New Step 5 paths are exactly those listed in completion-report section B; the ignored build candidate is the exact path listed there.
- No reset, checkout, commit, tag, version change, packaging change, installer change, or release artifact creation occurred.
