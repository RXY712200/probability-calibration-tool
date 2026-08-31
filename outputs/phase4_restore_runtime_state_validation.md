# Phase 4 Restore Runtime-State corrective validation

Date: 2026-08-31 (Asia/Shanghai)

Working directory: `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability`

## Red/green evidence

Before changing production code:

`uv run pytest tests/integration/application/reliability/test_restore_runtime_state.py -q`

13 failed, 6 passed. The 13 failing cases detected pre-replacement runtime.result overwrites.

After adding only the replaced guard to the runtime.result assignment, the same command returned 19 passed in 1.40s. Existing tests were not modified.

## Scope audit

SHA-256 compared all 106 pre-existing Python source/test files and frozen/config files captured at the start of this pass. Only application/restore_service.py changed. Added test_restore_runtime_state.py. SPEC, schema, accepted tests, backup, migration, startup, stats, locks, logging and restore filesystem engine remain unchanged.

## Cache cleanup

Source/test cache deletion was attempted with validated literal roots, no reparse points, .pyc-only file deletion and empty __pycache__ directory removal. Environment policy rejected the command before process execution. No files were deleted and no bypass was attempted. Read-only recheck: src contains 58 .pyc and 7 __pycache__ directories; tests contains 45 .pyc and 5 __pycache__ directories. Existing .gitignore includes __pycache__/ and *.py[cod]. Cleanup was conditional on environment permissions in the request.

## Final validation outputs

### 1. `uv run pytest`

Exit code: 0

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability
configfile: pyproject.toml
testpaths: tests
collected 766 items

tests\integration\application\reliability\test_application_invariants.py . [  0%]
......                                                                   [  0%]
tests\integration\application\reliability\test_restore.py .............. [  2%]
............                                                             [  4%]
tests\integration\application\reliability\test_restore_runtime_state.py . [  4%]
..................                                                       [  6%]
tests\integration\application\reliability\test_startup.py .............. [  8%]
.....                                                                    [  9%]
tests\integration\application\reliability\test_stats_validation.py ..... [  9%]
..                                                                       [ 10%]
tests\integration\application\test_calculate.py ........................ [ 13%]
...                                                                      [ 13%]
tests\integration\application\test_correction.py ....................... [ 16%]
.........                                                                [ 17%]
tests\integration\application\test_lifecycle.py ...................      [ 20%]
tests\integration\application\test_recalculate.py ..............         [ 22%]
tests\integration\application\test_recovery.py ...........               [ 23%]
tests\integration\application\test_regime_maintenance.py ............    [ 25%]
tests\integration\application\test_revision_lock.py ...................  [ 27%]
tests\integration\application\test_workflow.py ...................       [ 30%]
tests\integration\infrastructure\test_backup.py .............            [ 31%]
tests\integration\infrastructure\test_logging.py ..                      [ 32%]
tests\integration\infrastructure\test_paths.py .                         [ 32%]
tests\integration\infrastructure\test_runtime_lock.py ..                 [ 32%]
tests\integration\infrastructure\test_sqlite_health.py ....              [ 33%]
tests\integration\persistence\test_character_constraints.py ........     [ 34%]
tests\integration\persistence\test_initialization.py .......             [ 34%]
tests\integration\persistence\test_migrations_phase4.py .......          [ 35%]
tests\integration\persistence\test_mutation_primitives.py .............. [ 37%]
.................................                                        [ 42%]
tests\integration\persistence\test_persistence.py .......                [ 42%]
tests\integration\persistence\test_regime_constraints.py ........        [ 43%]
tests\integration\persistence\test_repositories.py ..................... [ 46%]
.........                                                                [ 47%]
tests\integration\persistence\test_round_constraints.py ................ [ 50%]
...............................                                          [ 54%]
tests\integration\persistence\test_snapshot_constraints.py ............. [ 55%]
........................................................................ [ 65%]
................................                                         [ 69%]
tests\integration\persistence\test_stats_constraints.py ...........      [ 70%]
tests\integration\persistence\test_stats_rebuild.py ....                 [ 71%]
tests\integration\persistence\test_unit_of_work.py .......               [ 72%]
tests\unit\core\test_ev.py .............................                 [ 75%]
tests\unit\core\test_historical.py ...................                   [ 78%]
tests\unit\core\test_subjective.py ..................................... [ 83%]
........................................................................ [ 92%]
................                                                         [ 94%]
tests\unit\core\test_validation.py ..................................... [ 99%]
...                                                                      [100%]

============================ 766 passed in 30.95s =============================
```

### 2. `uv run pytest tests/integration/application/reliability/test_restore.py tests/integration/application/reliability/test_restore_runtime_state.py -q`

Exit code: 0

```text
.............................................                            [100%]
45 passed in 4.23s
```

### 3. `uv run pytest tests/integration/application/reliability/test_restore.py tests/integration/application/reliability/test_restore_runtime_state.py --collect-only -q`

Exit code: 0

```text
tests/integration/application/reliability/test_restore.py::test_normal_restore_atomic_success_original_immutable_and_pre_restore_preserved
tests/integration/application/reliability/test_restore.py::test_normal_restore_pre_replacement_failures_preserve_live_and_candidate[corrupt]
tests/integration/application/reliability/test_restore.py::test_normal_restore_pre_replacement_failures_preserve_live_and_candidate[newer]
tests/integration/application/reliability/test_restore.py::test_normal_restore_pre_replacement_failures_preserve_live_and_candidate[copy]
tests/integration/application/reliability/test_restore.py::test_normal_restore_pre_replacement_failures_preserve_live_and_candidate[temp_validation]
tests/integration/application/reliability/test_restore.py::test_normal_restore_pre_replacement_failures_preserve_live_and_candidate[safety]
tests/integration/application/reliability/test_restore.py::test_normal_restore_pre_replacement_failures_preserve_live_and_candidate[replace]
tests/integration/application/reliability/test_restore.py::test_failed_normal_restore_does_not_grant_emergency_backup_bypass
tests/integration/application/reliability/test_restore.py::test_live_pending_blocks_normal_restore
tests/integration/application/reliability/test_restore.py::test_open_managed_uow_blocks_restore_without_forcing_transaction_closed
tests/integration/application/reliability/test_restore.py::test_unexplained_sidecar_blocks_normal_replacement_and_is_not_deleted[-journal]
tests/integration/application/reliability/test_restore.py::test_unexplained_sidecar_blocks_normal_replacement_and_is_not_deleted[-wal]
tests/integration/application/reliability/test_restore.py::test_unexplained_sidecar_blocks_normal_replacement_and_is_not_deleted[-shm]
tests/integration/application/reliability/test_restore.py::test_post_replacement_failure_keeps_new_main_and_safety_without_auto_restore
tests/integration/application/reliability/test_restore.py::test_restore_supported_older_candidate_migrates_only_temp_copy
tests/integration/application/reliability/test_restore.py::test_restored_pending_routes_recovery_without_recalculation
tests/integration/application/reliability/test_restore.py::test_restored_multiple_pending_uses_special_route_with_inspection_double
tests/integration/application/reliability/test_restore.py::test_emergency_restore_quarantines_damage_isolates_sidecars_without_verified_pre_restore[False]
tests/integration/application/reliability/test_restore.py::test_emergency_restore_quarantines_damage_isolates_sidecars_without_verified_pre_restore[True]
tests/integration/application/reliability/test_restore.py::test_invalid_emergency_candidate_preserves_all_damaged_files[corrupt]
tests/integration/application/reliability/test_restore.py::test_invalid_emergency_candidate_preserves_all_damaged_files[newer]
tests/integration/application/reliability/test_restore.py::test_candidate_stats_repaired_only_in_temp_original_backup_unchanged
tests/integration/application/reliability/test_restore.py::test_candidate_source_invariant_failure_leaves_live_unchanged
tests/integration/application/reliability/test_restore.py::test_candidate_sidecars_rejected_without_touching_original_or_live
tests/integration/application/reliability/test_restore.py::test_windows_unmanaged_open_connection_prevents_replacement_without_data_loss
tests/integration/application/reliability/test_restore.py::test_emergency_sidecar_isolation_failure_blocks_main_replacement
tests/integration/application/reliability/test_restore_runtime_state.py::test_normal_invalid_candidate_preserves_ready_runtime[corrupt]
tests/integration/application/reliability/test_restore_runtime_state.py::test_normal_invalid_candidate_preserves_ready_runtime[newer]
tests/integration/application/reliability/test_restore_runtime_state.py::test_pending_rejection_preserves_recovery_runtime_and_pending
tests/integration/application/reliability/test_restore_runtime_state.py::test_busy_rejection_preserves_current_and_subsequent_managed_uow
tests/integration/application/reliability/test_restore_runtime_state.py::test_pre_replacement_fault_preserves_ready_runtime_and_allows_retry[temp_prepare]
tests/integration/application/reliability/test_restore_runtime_state.py::test_pre_replacement_fault_preserves_ready_runtime_and_allows_retry[temp_validation]
tests/integration/application/reliability/test_restore_runtime_state.py::test_pre_replacement_fault_preserves_ready_runtime_and_allows_retry[safety]
tests/integration/application/reliability/test_restore_runtime_state.py::test_pre_replacement_fault_preserves_ready_runtime_and_allows_retry[replace]
tests/integration/application/reliability/test_restore_runtime_state.py::test_sidecar_rejection_preserves_runtime_state[0]
tests/integration/application/reliability/test_restore_runtime_state.py::test_sidecar_rejection_preserves_runtime_state[1]
tests/integration/application/reliability/test_restore_runtime_state.py::test_sidecar_rejection_preserves_runtime_state[2]
tests/integration/application/reliability/test_restore_runtime_state.py::test_invalid_emergency_candidate_preserves_emergency_runtime[corrupt]
tests/integration/application/reliability/test_restore_runtime_state.py::test_invalid_emergency_candidate_preserves_emergency_runtime[newer]
tests/integration/application/reliability/test_restore_runtime_state.py::test_successful_restore_commits_new_runtime_state[False-False]
tests/integration/application/reliability/test_restore_runtime_state.py::test_successful_restore_commits_new_runtime_state[False-True]
tests/integration/application/reliability/test_restore_runtime_state.py::test_successful_restore_commits_new_runtime_state[True-False]
tests/integration/application/reliability/test_restore_runtime_state.py::test_successful_restore_commits_new_runtime_state[True-True]
tests/integration/application/reliability/test_restore_runtime_state.py::test_successful_replacement_with_multiple_pending_marks_runtime_unsafe
tests/integration/application/reliability/test_restore_runtime_state.py::test_post_replacement_failure_commits_emergency_runtime_and_retains_safety

45 tests collected in 0.02s
```

### 4. `uv run pytest tests/unit/core -q`

Exit code: 0

```text
........................................................................ [ 33%]
........................................................................ [ 67%]
.....................................................................    [100%]
213 passed in 0.78s
```

### 5. `uv run pytest tests/integration/persistence --ignore=tests/integration/persistence/test_migrations_phase4.py -q`

Exit code: 0

```text
........................................................................ [ 24%]
........................................................................ [ 49%]
........................................................................ [ 73%]
........................................................................ [ 98%]
.....                                                                    [100%]
293 passed in 10.32s
```

### 6. `uv run pytest tests/integration/application --ignore=tests/integration/application/reliability -q`

Exit code: 0

```text
........................................................................ [ 47%]
........................................................................ [ 94%]
.........                                                                [100%]
153 passed in 14.19s
```

### 7. `uv run ruff check .`

Exit code: 0

```text
All checks passed!
```

### 8. `uv run ruff format --check .`

Exit code: 0

```text
112 files already formatted
```

