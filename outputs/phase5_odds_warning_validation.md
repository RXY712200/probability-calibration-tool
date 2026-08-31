# Phase 5 Odds-Combination Warning corrective validation

Working directory: `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability`

## Scope

Only existing source file changed: src/probability_calibration_tool/ui/analysis_panel.py. Added tests/ui/test_odds_combination_warning.py. Hash audit of 135 baseline source/test/config files confirms all other accepted files unchanged, including SPEC, schema, Workflow, Core, persistence and reliability. No accepted test was edited.

The warning is a separate QLabel selected only by OddsCombinationStatus.DOUBLE_POSITIVE_WINDOW. It is cleared before each render, coexists with endpoint notes, and uses committed analysis during edits.

## Red/green evidence

Before implementation:

`uv run pytest tests/ui/test_odds_combination_warning.py -q -k test_double_positive_window_has_explicit_timing_warning`

1 failed, 11 deselected: the warning presentation was absent. After implementation all 12 new tests pass; no skip/xfail was added.

## Manual DPI

Actual Windows 125%: not performed.

Actual Windows 150%: not performed.

manual DPI acceptance pending; offscreen tests are not manual display-scaling acceptance.

## Final validation

### 1. `uv run pytest tests/ui/test_odds_combination_warning.py -q`

Exit code: 0

```text
............                                                             [100%]
12 passed in 1.07s
```

### 2. `uv run pytest tests/ui/test_odds_combination_warning.py --collect-only -q`

Exit code: 0

```text
tests/ui/test_odds_combination_warning.py::test_double_positive_window_has_explicit_timing_warning
tests/ui/test_odds_combination_warning.py::test_other_odds_status_has_no_double_positive_warning[1.50-normal_overlap]
tests/ui/test_odds_combination_warning.py::test_other_odds_status_has_no_double_positive_warning[2.00-critical]
tests/ui/test_odds_combination_warning.py::test_endpoint_note_and_odds_warning_coexist[0-1]
tests/ui/test_odds_combination_warning.py::test_endpoint_note_and_odds_warning_coexist[100-99]
tests/ui/test_odds_combination_warning.py::test_stale_odds_warning_is_cleared_from_hidden_and_visible_widgets[no_analysis]
tests/ui/test_odds_combination_warning.py::test_stale_odds_warning_is_cleared_from_hidden_and_visible_widgets[completed_new_draft]
tests/ui/test_odds_combination_warning.py::test_stale_odds_warning_is_cleared_from_hidden_and_visible_widgets[void_new_draft]
tests/ui/test_odds_combination_warning.py::test_stale_odds_warning_is_cleared_from_hidden_and_visible_widgets[safety]
tests/ui/test_odds_combination_warning.py::test_modify_warning_uses_committed_odds_until_recalculate[1.50-normal_overlap]
tests/ui/test_odds_combination_warning.py::test_modify_warning_uses_committed_odds_until_recalculate[2.00-critical]
tests/ui/test_odds_combination_warning.py::test_warning_mapping_uses_authoritative_enum_not_input_odds

12 tests collected in 0.01s
```

### 3. `uv run pytest tests/ui -q`

Exit code: 0

```text
........................................................................ [ 70%]
..............................                                           [100%]
102 passed in 7.79s
```

### 4. `uv run pytest`

Exit code: 0

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability
configfile: pyproject.toml
testpaths: tests
collected 872 items

tests\integration\application\reliability\test_application_invariants.py . [  0%]
......                                                                   [  0%]
tests\integration\application\reliability\test_restore.py .............. [  2%]
............                                                             [  3%]
tests\integration\application\reliability\test_restore_runtime_state.py . [  3%]
..................                                                       [  5%]
tests\integration\application\reliability\test_startup.py .............. [  7%]
.....                                                                    [  8%]
tests\integration\application\reliability\test_stats_validation.py ..... [  8%]
..                                                                       [  8%]
tests\integration\application\test_calculate.py ........................ [ 11%]
...                                                                      [ 12%]
tests\integration\application\test_correction.py ....................... [ 14%]
.........                                                                [ 15%]
tests\integration\application\test_lifecycle.py ...................      [ 17%]
tests\integration\application\test_presentation_capabilities.py ....     [ 18%]
tests\integration\application\test_recalculate.py ..............         [ 19%]
tests\integration\application\test_recovery.py ...........               [ 21%]
tests\integration\application\test_regime_maintenance.py ............    [ 22%]
tests\integration\application\test_revision_lock.py ...................  [ 24%]
tests\integration\application\test_workflow.py ...................       [ 26%]
tests\integration\infrastructure\test_backup.py .............            [ 28%]
tests\integration\infrastructure\test_logging.py ..                      [ 28%]
tests\integration\infrastructure\test_paths.py .                         [ 28%]
tests\integration\infrastructure\test_runtime_lock.py ..                 [ 29%]
tests\integration\infrastructure\test_sqlite_health.py ....              [ 29%]
tests\integration\persistence\test_character_constraints.py ........     [ 30%]
tests\integration\persistence\test_initialization.py .......             [ 31%]
tests\integration\persistence\test_migrations_phase4.py .......          [ 31%]
tests\integration\persistence\test_mutation_primitives.py .............. [ 33%]
.................................                                        [ 37%]
tests\integration\persistence\test_persistence.py .......                [ 38%]
tests\integration\persistence\test_regime_constraints.py ........        [ 39%]
tests\integration\persistence\test_repositories.py ..................... [ 41%]
.........                                                                [ 42%]
tests\integration\persistence\test_round_constraints.py ................ [ 44%]
...............................                                          [ 47%]
tests\integration\persistence\test_snapshot_constraints.py ............. [ 49%]
........................................................................ [ 57%]
................................                                         [ 61%]
tests\integration\persistence\test_stats_constraints.py ...........      [ 62%]
tests\integration\persistence\test_stats_rebuild.py ....                 [ 63%]
tests\integration\persistence\test_unit_of_work.py .......               [ 63%]
tests\ui\test_analysis_safety.py ..........                              [ 65%]
tests\ui\test_architecture_formatting.py ......                          [ 65%]
tests\ui\test_close_guard.py .......................                     [ 68%]
tests\ui\test_dpi_structure.py ..                                        [ 68%]
tests\ui\test_maintenance.py ..                                          [ 68%]
tests\ui\test_odds_combination_warning.py ............                   [ 70%]
tests\ui\test_pre_run.py ........................                        [ 72%]
tests\ui\test_recovery_ui.py ......                                      [ 73%]
tests\ui\test_startup_pages.py .........                                 [ 74%]
tests\ui\test_workflow_contract.py ........                              [ 75%]
tests\unit\core\test_ev.py .............................                 [ 78%]
tests\unit\core\test_historical.py ...................                   [ 81%]
tests\unit\core\test_subjective.py ..................................... [ 85%]
........................................................................ [ 93%]
................                                                         [ 95%]
tests\unit\core\test_validation.py ..................................... [ 99%]
...                                                                      [100%]

============================ 872 passed in 41.53s =============================
```

### 5. `uv run pytest tests/unit/core tests/integration --ignore=tests/integration/application/test_presentation_capabilities.py -q`

Exit code: 0

```text
........................................................................ [  9%]
........................................................................ [ 18%]
........................................................................ [ 28%]
........................................................................ [ 37%]
........................................................................ [ 46%]
........................................................................ [ 56%]
........................................................................ [ 65%]
........................................................................ [ 75%]
........................................................................ [ 84%]
........................................................................ [ 93%]
..............................................                           [100%]
766 passed in 32.95s
```

### 6. `uv run ruff check .`

Exit code: 0

```text
All checks passed!
```

### 7. `uv run ruff format --check .`

Exit code: 0

```text
144 files already formatted
```

