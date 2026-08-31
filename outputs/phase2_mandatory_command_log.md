# Phase 2 mandatory completion — literal shell command log

Commands appear in execution order. Repeated commands are retained.

1.
```powershell
Get-Content -Raw -LiteralPath 'C:\Users\rxy71\.codex\attachments\d9c238a7-c66a-4307-885b-ed31b95a3fcb\pasted-text.txt'
```

2.
```powershell
rg --files -g '!**/__pycache__/**' -g '!work/**' -g '!outputs/**' -g '!uv.lock'
```

3.
```powershell
Get-Content -Raw -LiteralPath '.\src\probability_calibration_tool\domain\records.py'
```

4.
```powershell
Get-Content -Raw -LiteralPath '.\tests\integration\persistence\test_persistence.py'
```

5.
```powershell
Get-Content -Raw -LiteralPath '.\src\probability_calibration_tool\persistence\unit_of_work.py'
```

6.
```powershell
Get-Content -Raw -LiteralPath '.\src\probability_calibration_tool\persistence\repositories\snapshots.py'
```

7.
```powershell
Get-Content -Raw -LiteralPath '.\pyproject.toml'
```

8.
```powershell
Get-Content -LiteralPath '.\src\probability_calibration_tool\persistence\repositories\characters.py', '.\src\probability_calibration_tool\persistence\repositories\regimes.py', '.\src\probability_calibration_tool\persistence\repositories\rounds.py', '.\src\probability_calibration_tool\persistence\repositories\stats.py', '.\src\probability_calibration_tool\persistence\repositories\meta.py'
```

9.
```powershell
Get-Content -LiteralPath '.\src\probability_calibration_tool\persistence\database.py', '.\src\probability_calibration_tool\persistence\migrations.py', '.\src\probability_calibration_tool\persistence\schema.py'
```

10.
```powershell
$paths = @('SPEC_1.0.md', 'pyproject.toml', 'uv.lock') + @(Get-ChildItem -LiteralPath '.\src', '.\tests\unit' -File -Recurse -Filter '*.py' | Select-Object -ExpandProperty FullName); $paths | ForEach-Object { Get-FileHash -Algorithm SHA256 -LiteralPath $_ } | Select-Object Path, Hash | ConvertTo-Json -Depth 3
```

11.
```powershell
uv run pytest tests/integration/persistence -q
```

12.
```powershell
uv run ruff format tests/integration/persistence src/probability_calibration_tool/domain/records.py src/probability_calibration_tool/persistence/repositories/snapshots.py
```

13.
```powershell
uv run pytest
```

14.
```powershell
uv run ruff check .
```

15.
```powershell
uv run ruff format --check .
```

16.
```powershell
uv run pytest tests/integration/persistence --collect-only -q
```

17.
```powershell
uv run pytest
```

18.
```powershell
uv run ruff check .
```

19.
```powershell
uv run ruff format --check .
```

20.
```powershell
$paths = @('SPEC_1.0.md', 'pyproject.toml', 'uv.lock') + @(Get-ChildItem -LiteralPath '.\src', '.\tests\unit' -File -Recurse -Filter '*.py' | Select-Object -ExpandProperty FullName); $paths | ForEach-Object { Get-FileHash -Algorithm SHA256 -LiteralPath $_ } | Select-Object Path, Hash | ConvertTo-Json -Depth 3
```

## Initial regression result

`uv run pytest tests/integration/persistence -q`: 13 failed, 220 passed. All failures exposed lost snapshot Enum types. Tests retained; production snapshot Enum restoration fixed.

## Final full-suite output

```
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability
configfile: pyproject.toml
testpaths: tests
collected 446 items

tests\integration\persistence\test_character_constraints.py ........     [  1%]
tests\integration\persistence\test_initialization.py .......             [  3%]
tests\integration\persistence\test_persistence.py .......                [  4%]
tests\integration\persistence\test_regime_constraints.py ........        [  6%]
tests\integration\persistence\test_repositories.py ..................... [ 11%]
.........                                                                [ 13%]
tests\integration\persistence\test_round_constraints.py ................ [ 17%]
.....................                                                    [ 21%]
tests\integration\persistence\test_snapshot_constraints.py ............. [ 24%]
........................................................................ [ 40%]
................................                                         [ 47%]
tests\integration\persistence\test_stats_constraints.py ...........      [ 50%]
tests\integration\persistence\test_stats_rebuild.py ....                 [ 51%]
tests\integration\persistence\test_unit_of_work.py ....                  [ 52%]
tests\unit\core\test_ev.py .............................                 [ 58%]
tests\unit\core\test_historical.py ...................                   [ 63%]
tests\unit\core\test_subjective.py ..................................... [ 71%]
........................................................................ [ 87%]
................                                                         [ 91%]
tests\unit\core\test_validation.py ..................................... [ 99%]
...                                                                      [100%]

============================= 446 passed in 5.53s =============================
```

## Final Ruff

```
All checks passed!
44 files already formatted
```

## Persistence collection

`uv run pytest tests/integration/persistence --collect-only -q`

- tests/integration/persistence/test_character_constraints.py: 8
- tests/integration/persistence/test_initialization.py: 7
- tests/integration/persistence/test_persistence.py: 7
- tests/integration/persistence/test_regime_constraints.py: 8
- tests/integration/persistence/test_repositories.py: 30
- tests/integration/persistence/test_round_constraints.py: 37
- tests/integration/persistence/test_snapshot_constraints.py: 117
- tests/integration/persistence/test_stats_constraints.py: 11
- tests/integration/persistence/test_stats_rebuild.py: 4
- tests/integration/persistence/test_unit_of_work.py: 4

233 tests collected in 0.10s

