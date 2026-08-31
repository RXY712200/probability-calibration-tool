# Phase 2 final corrective pass — exact commands and evidence

Commands in execution order:

1.
```powershell
Get-Content -Raw -LiteralPath 'C:\Users\rxy71\.codex\attachments\00945640-156a-4d7a-a9fc-f5a150ea4a02\pasted-text.txt'
```

2.
```powershell
Get-Content -LiteralPath '.\src\probability_calibration_tool\persistence\unit_of_work.py', '.\src\probability_calibration_tool\persistence\database.py', '.\src\probability_calibration_tool\persistence\repositories\rounds.py', '.\src\probability_calibration_tool\persistence\repositories\regimes.py', '.\src\probability_calibration_tool\persistence\repositories\stats.py'
```

3.
```powershell
Get-Content -LiteralPath '.\tests\integration\persistence\test_unit_of_work.py', '.\tests\integration\persistence\test_repositories.py', '.\tests\integration\persistence\conftest.py', '.\.gitignore'
```

4.
```powershell
$paths = @('SPEC_1.0.md', 'pyproject.toml', 'uv.lock', '.gitignore') + @(Get-ChildItem -LiteralPath '.\src', '.\tests' -File -Recurse -Filter '*.py' | Select-Object -ExpandProperty FullName); $paths | ForEach-Object { Get-FileHash -Algorithm SHA256 -LiteralPath $_ } | Select-Object Path, Hash | ConvertTo-Json -Depth 3
```

5.
```powershell
uv run pytest tests/integration/persistence/test_mutation_primitives.py tests/integration/persistence/test_unit_of_work.py tests/integration/persistence/test_round_constraints.py -q --tb=short
```

6.
```powershell
uv run pytest
```

7.
```powershell
uv run ruff format src/probability_calibration_tool/persistence tests/integration/persistence
```

8.
```powershell
uv run pytest
```

9.
```powershell
uv run pytest tests/integration/persistence --collect-only -q
```

10.
```powershell
uv run ruff check .
```

11.
```powershell
uv run ruff format --check .
```

12.
```powershell
$paths = @('SPEC_1.0.md', 'pyproject.toml', 'uv.lock', '.gitignore') + @(Get-ChildItem -LiteralPath '.\src', '.\tests' -File -Recurse -Filter '*.py' | Select-Object -ExpandProperty FullName); $paths | ForEach-Object { Get-FileHash -Algorithm SHA256 -LiteralPath $_ } | Select-Object Path, Hash | ConvertTo-Json -Depth 3
```

13.
```powershell
Get-ChildItem -LiteralPath '.\src', '.\tests' -Recurse -Force | Where-Object { ($_.PSIsContainer -and $_.Name -eq '__pycache__') -or (-not $_.PSIsContainer -and $_.Extension -eq '.pyc') } | Select-Object FullName, PSIsContainer, Attributes | ConvertTo-Json -Depth 3
```

14.
```powershell
$ErrorActionPreference = 'Stop'
$cleanupFiles = @('C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\core\__pycache__\__init__.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\core\__pycache__\errors.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\core\__pycache__\ev.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\core\__pycache__\historical.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\core\__pycache__\model_specs.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\core\__pycache__\subjective.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\core\__pycache__\validation.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\domain\__pycache__\__init__.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\domain\__pycache__\dto.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\domain\__pycache__\enums.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\domain\__pycache__\records.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\__pycache__\__init__.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\__pycache__\characters.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\__pycache__\meta.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\__pycache__\regimes.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\__pycache__\rounds.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\__pycache__\snapshots.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\__pycache__\stats.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\__pycache__\__init__.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\__pycache__\database.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\__pycache__\errors.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\__pycache__\migrations.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\__pycache__\schema.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\__pycache__\seed.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\__pycache__\unit_of_work.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\__pycache__\__init__.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\__pycache__\__init__.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\__pycache__\conftest.cpython-313-pytest-9.1.1.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\__pycache__\helpers.cpython-313.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\__pycache__\test_character_constraints.cpython-313-pytest-9.1.1.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\__pycache__\test_initialization.cpython-313-pytest-9.1.1.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\__pycache__\test_mutation_primitives.cpython-313-pytest-9.1.1.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\__pycache__\test_persistence.cpython-313-pytest-9.1.1.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\__pycache__\test_regime_constraints.cpython-313-pytest-9.1.1.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\__pycache__\test_repositories.cpython-313-pytest-9.1.1.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\__pycache__\test_round_constraints.cpython-313-pytest-9.1.1.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\__pycache__\test_snapshot_constraints.cpython-313-pytest-9.1.1.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\__pycache__\test_stats_constraints.cpython-313-pytest-9.1.1.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\__pycache__\test_stats_rebuild.cpython-313-pytest-9.1.1.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\__pycache__\test_unit_of_work.cpython-313-pytest-9.1.1.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\unit\core\__pycache__\test_ev.cpython-313-pytest-9.1.1.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\unit\core\__pycache__\test_historical.cpython-313-pytest-9.1.1.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\unit\core\__pycache__\test_subjective.cpython-313-pytest-9.1.1.pyc',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\unit\core\__pycache__\test_validation.cpython-313-pytest-9.1.1.pyc')
$cleanupDirectories = @('C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\__pycache__',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\core\__pycache__',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\domain\__pycache__',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\__pycache__',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\__pycache__',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\__pycache__',
'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\unit\core\__pycache__')
$cleanupSourceRoot = 'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\'
$cleanupTestRoot = 'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\'
foreach ($cleanupTarget in ($cleanupFiles + $cleanupDirectories)) {
    $resolvedCleanupPath = (Resolve-Path -LiteralPath $cleanupTarget).Path
    if (-not ($resolvedCleanupPath.StartsWith($cleanupSourceRoot, [StringComparison]::OrdinalIgnoreCase) -or $resolvedCleanupPath.StartsWith($cleanupTestRoot, [StringComparison]::OrdinalIgnoreCase))) { throw 'Cleanup target outside source/test directories' }
    $cleanupItem = Get-Item -LiteralPath $resolvedCleanupPath -Force
    if (($cleanupItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Reparse point refused' }
}
foreach ($cleanupDirectory in $cleanupDirectories) {
    foreach ($cleanupChild in (Get-ChildItem -LiteralPath $cleanupDirectory -Force)) {
        if ($cleanupChild.PSIsContainer -or $cleanupChild.FullName -notin $cleanupFiles) { throw 'Unexpected cache directory contents; deletion refused' }
    }
}
foreach ($cleanupFile in $cleanupFiles) { Remove-Item -LiteralPath $cleanupFile }
foreach ($cleanupDirectory in $cleanupDirectories) { Remove-Item -LiteralPath $cleanupDirectory }
'Removed {0} bytecode files and {1} empty cache directories.' -f $cleanupFiles.Count, $cleanupDirectories.Count
```

15.
```powershell
$remainingCache = @(Get-ChildItem -LiteralPath '.\src', '.\tests' -Recurse -Force | Where-Object { ($_.PSIsContainer -and $_.Name -eq '__pycache__') -or (-not $_.PSIsContainer -and $_.Extension -eq '.pyc') }); 'Remaining cache artifacts: {0}' -f $remainingCache.Count; $ignoreRules = Get-Content -LiteralPath '.\.gitignore'; foreach ($rule in @('.venv/', '__pycache__/', '*.py[cod]')) { '{0}: {1}' -f $rule, ($ignoreRules -contains $rule) }; (Get-FileHash -Algorithm SHA256 -LiteralPath '.\SPEC_1.0.md').Hash
```

## Initial regression evidence

Focused tests before production fixes: 56 failed, 45 passed. Failures reproduced missing primitives, direct repository autocommit, post-commit durability leakage, and all six hybrid voided states. Regression tests were retained.

The first full run after production fixes: 505 passed, 1 failed. The snapshot-update no-commit test's preparation needed an explicit setup.commit() under the new transaction contract; all its behavioral assertions were retained.

## Final full test suite

```
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability
configfile: pyproject.toml
testpaths: tests
collected 506 items

tests\integration\persistence\test_character_constraints.py ........     [  1%]
tests\integration\persistence\test_initialization.py .......             [  2%]
tests\integration\persistence\test_mutation_primitives.py .............. [  5%]
.................................                                        [ 12%]
tests\integration\persistence\test_persistence.py .......                [ 13%]
tests\integration\persistence\test_regime_constraints.py ........        [ 15%]
tests\integration\persistence\test_repositories.py ..................... [ 19%]
.........                                                                [ 21%]
tests\integration\persistence\test_round_constraints.py ................ [ 24%]
...............................                                          [ 30%]
tests\integration\persistence\test_snapshot_constraints.py ............. [ 33%]
........................................................................ [ 47%]
................................                                         [ 53%]
tests\integration\persistence\test_stats_constraints.py ...........      [ 55%]
tests\integration\persistence\test_stats_rebuild.py ....                 [ 56%]
tests\integration\persistence\test_unit_of_work.py .......               [ 57%]
tests\unit\core\test_ev.py .............................                 [ 63%]
tests\unit\core\test_historical.py ...................                   [ 67%]
tests\unit\core\test_subjective.py ..................................... [ 74%]
........................................................................ [ 88%]
................                                                         [ 92%]
tests\unit\core\test_validation.py ..................................... [ 99%]
...                                                                      [100%]

============================= 506 passed in 6.15s =============================
```

## Collected persistence items

- tests/integration/persistence/test_character_constraints.py: 8
- tests/integration/persistence/test_initialization.py: 7
- tests/integration/persistence/test_mutation_primitives.py: 47
- tests/integration/persistence/test_persistence.py: 7
- tests/integration/persistence/test_regime_constraints.py: 8
- tests/integration/persistence/test_repositories.py: 30
- tests/integration/persistence/test_round_constraints.py: 47
- tests/integration/persistence/test_snapshot_constraints.py: 117
- tests/integration/persistence/test_stats_constraints.py: 11
- tests/integration/persistence/test_stats_rebuild.py: 4
- tests/integration/persistence/test_unit_of_work.py: 7

293 tests collected in 0.03s

## Ruff

```
All checks passed!
47 files already formatted
```

## Hygiene verification

```
Remaining cache artifacts: 0
.venv/: True
__pycache__/: True
*.py[cod]: True
AEE4EB200BEA8EC1A652A65A2076645613E6057C37D6280A9A0787CC5B040FC4
```

