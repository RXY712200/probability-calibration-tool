# Phase 4 validation commands

Working directory: `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability`

Final validation: Windows / Python 3.13.14 / pytest 9.1.1.

These are the literal final validation commands and captured outputs; this is not a transcript of every exploratory read or intermediate debugging command.

## 1. `uv run pytest`

Exit code: 0

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability
configfile: pyproject.toml
testpaths: tests
collected 747 items

tests\integration\application\reliability\test_application_invariants.py . [  0%]
......                                                                   [  0%]
tests\integration\application\reliability\test_restore.py .............. [  2%]
............                                                             [  4%]
tests\integration\application\reliability\test_startup.py .............. [  6%]
.....                                                                    [  6%]
tests\integration\application\reliability\test_stats_validation.py ..... [  7%]
..                                                                       [  7%]
tests\integration\application\test_calculate.py ........................ [ 11%]
...                                                                      [ 11%]
tests\integration\application\test_correction.py ....................... [ 14%]
.........                                                                [ 15%]
tests\integration\application\test_lifecycle.py ...................      [ 18%]
tests\integration\application\test_recalculate.py ..............         [ 20%]
tests\integration\application\test_recovery.py ...........               [ 21%]
tests\integration\application\test_regime_maintenance.py ............    [ 23%]
tests\integration\application\test_revision_lock.py ...................  [ 25%]
tests\integration\application\test_workflow.py ...................       [ 28%]
tests\integration\infrastructure\test_backup.py .............            [ 30%]
tests\integration\infrastructure\test_logging.py ..                      [ 30%]
tests\integration\infrastructure\test_paths.py .                         [ 30%]
tests\integration\infrastructure\test_runtime_lock.py ..                 [ 30%]
tests\integration\infrastructure\test_sqlite_health.py ....              [ 31%]
tests\integration\persistence\test_character_constraints.py ........     [ 32%]
tests\integration\persistence\test_initialization.py .......             [ 33%]
tests\integration\persistence\test_migrations_phase4.py .......          [ 34%]
tests\integration\persistence\test_mutation_primitives.py .............. [ 36%]
.................................                                        [ 40%]
tests\integration\persistence\test_persistence.py .......                [ 41%]
tests\integration\persistence\test_regime_constraints.py ........        [ 42%]
tests\integration\persistence\test_repositories.py ..................... [ 45%]
.........                                                                [ 46%]
tests\integration\persistence\test_round_constraints.py ................ [ 48%]
...............................                                          [ 52%]
tests\integration\persistence\test_snapshot_constraints.py ............. [ 54%]
........................................................................ [ 64%]
................................                                         [ 68%]
tests\integration\persistence\test_stats_constraints.py ...........      [ 70%]
tests\integration\persistence\test_stats_rebuild.py ....                 [ 70%]
tests\integration\persistence\test_unit_of_work.py .......               [ 71%]
tests\unit\core\test_ev.py .............................                 [ 75%]
tests\unit\core\test_historical.py ...................                   [ 77%]
tests\unit\core\test_subjective.py ..................................... [ 82%]
........................................................................ [ 92%]
................                                                         [ 94%]
tests\unit\core\test_validation.py ..................................... [ 99%]
...                                                                      [100%]

============================ 747 passed in 38.59s =============================
```

## 2. `uv run pytest tests/integration/infrastructure --collect-only -q`

Exit code: 0

```text
tests/integration/infrastructure/test_backup.py::test_online_backup_verified_version_and_representative_source_data
tests/integration/infrastructure/test_backup.py::test_independent_retention_keeps_newest_valid[recent-5]
tests/integration/infrastructure/test_backup.py::test_independent_retention_keeps_newest_valid[safety-10]
tests/integration/infrastructure/test_backup.py::test_failed_candidate_preserves_previous_five_byte_for_byte[creation]
tests/integration/infrastructure/test_backup.py::test_failed_candidate_preserves_previous_five_byte_for_byte[integrity]
tests/integration/infrastructure/test_backup.py::test_failed_candidate_preserves_previous_five_byte_for_byte[version]
tests/integration/infrastructure/test_backup.py::test_inventory_preserves_corrupt_temp_quarantine_unrelated
tests/integration/infrastructure/test_backup.py::test_rotation_delete_failure_stops_immediately_and_overretains
tests/integration/infrastructure/test_backup.py::test_daily_local_date_once_corrupt_replacement_and_seven_distinct_days
tests/integration/infrastructure/test_backup.py::test_daily_uses_injected_local_calendar_not_utc_date
tests/integration/infrastructure/test_backup.py::test_nonfatal_backup_warning_does_not_revert_committed_main_data[recent]
tests/integration/infrastructure/test_backup.py::test_nonfatal_backup_warning_does_not_revert_committed_main_data[daily]
tests/integration/infrastructure/test_backup.py::test_safety_adapter_satisfies_existing_correction_port_without_wiring_changes
tests/integration/infrastructure/test_logging.py::test_bootstrap_does_not_open_rotating_log
tests/integration/infrastructure/test_logging.py::test_error_id_traceback_safe_presentation_and_real_rotation
tests/integration/infrastructure/test_paths.py::test_explicit_and_production_paths_are_isolated_and_creation_idempotent
tests/integration/infrastructure/test_runtime_lock.py::test_real_subprocess_forced_death_releases_os_lock
tests/integration/infrastructure/test_runtime_lock.py::test_stale_file_and_normal_release
tests/integration/infrastructure/test_sqlite_health.py::test_full_check_requires_exact_ok_result
tests/integration/infrastructure/test_sqlite_health.py::test_existing_probe_does_not_force_readonly_or_change_journal_mode
tests/integration/infrastructure/test_sqlite_health.py::test_empty_unrelated_sqlite_is_not_verified_backup
tests/integration/infrastructure/test_sqlite_health.py::test_native_hot_rollback_journal_is_recovered

22 tests collected in 0.01s
```

## 3. `uv run pytest tests/integration/application/reliability --collect-only -q`

Exit code: 0

```text
tests/integration/application/reliability/test_application_invariants.py::test_source_invariant_damage_is_reported_never_repaired[identity-identities]
tests/integration/application/reliability/test_application_invariants.py::test_source_invariant_damage_is_reported_never_repaired[no_active-active regime]
tests/integration/application/reliability/test_application_invariants.py::test_source_invariant_damage_is_reported_never_repaired[missing_snapshot-snapshot]
tests/integration/application/reliability/test_application_invariants.py::test_source_invariant_damage_is_reported_never_repaired[exposure-exposure]
tests/integration/application/reliability/test_application_invariants.py::test_supersede_cycle_and_branch_detection_with_controlled_inventory
tests/integration/application/reliability/test_application_invariants.py::test_accepted_correction_chain_and_inactive_regimes_pass_source_invariants
tests/integration/application/reliability/test_application_invariants.py::test_missing_cache_is_not_source_corruption
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
tests/integration/application/reliability/test_startup.py::test_fresh_temporary_initialization_then_daily_and_long_lived_context
tests/integration/application/reliability/test_startup.py::test_fresh_failure_never_installs_live_database[initializer]
tests/integration/application/reliability/test_startup.py::test_fresh_failure_never_installs_live_database[integrity]
tests/integration/application/reliability/test_startup.py::test_fresh_failure_never_installs_live_database[invariant]
tests/integration/application/reliability/test_startup.py::test_fresh_failure_never_installs_live_database[install]
tests/integration/application/reliability/test_startup.py::test_preexisting_empty_or_corrupt_is_never_fresh[zero_bytes]
tests/integration/application/reliability/test_startup.py::test_preexisting_empty_or_corrupt_is_never_fresh[empty_sqlite]
tests/integration/application/reliability/test_startup.py::test_preexisting_empty_or_corrupt_is_never_fresh[version_zero_table]
tests/integration/application/reliability/test_startup.py::test_preexisting_empty_or_corrupt_is_never_fresh[corrupt]
tests/integration/application/reliability/test_startup.py::test_newer_schema_rejected_before_seeding_stats_or_backup
tests/integration/application/reliability/test_startup.py::test_healthy_existing_routes_and_daily_failure_is_nonfatal[False]
tests/integration/application/reliability/test_startup.py::test_healthy_existing_routes_and_daily_failure_is_nonfatal[True]
tests/integration/application/reliability/test_startup.py::test_second_instance_does_not_open_full_log
tests/integration/application/reliability/test_startup.py::test_multiple_pending_precedes_generic_invariant_and_suppresses_daily
tests/integration/application/reliability/test_startup.py::test_source_invariant_failure_is_not_repaired_or_backed_up
tests/integration/application/reliability/test_startup.py::test_startup_repairs_cache_before_backup
tests/integration/application/reliability/test_startup.py::test_startup_stats_failure_is_safety_error_without_daily
tests/integration/application/reliability/test_startup.py::test_startup_strict_order_with_real_components_and_spies
tests/integration/application/reliability/test_startup.py::test_unsafe_runtime_cannot_create_business_uow
tests/integration/application/reliability/test_stats_validation.py::test_stats_drift_repaired_from_source_with_warning[missing]
tests/integration/application/reliability/test_stats_validation.py::test_stats_drift_repaired_from_source_with_warning[version]
tests/integration/application/reliability/test_stats_validation.py::test_stats_drift_repaired_from_source_with_warning[counts]
tests/integration/application/reliability/test_stats_validation.py::test_stats_drift_repaired_from_source_with_warning[wins_losses]
tests/integration/application/reliability/test_stats_validation.py::test_stats_drift_repaired_from_source_with_warning[last_id]
tests/integration/application/reliability/test_stats_validation.py::test_inactive_and_active_regimes_repaired_together
tests/integration/application/reliability/test_stats_validation.py::test_stats_batch_failure_rolls_back_missing_insert_and_all_repairs

59 tests collected in 0.03s
```

## 4. `uv run pytest tests/integration/persistence/test_migrations_phase4.py --collect-only -q`

Exit code: 0

```text
tests/integration/persistence/test_migrations_phase4.py::test_ordered_synthetic_migrations_verify_safety_and_update_version_after_body
tests/integration/persistence/test_migrations_phase4.py::test_precommit_failure_rolls_back_schema_data_version_preserving_safety[body]
tests/integration/persistence/test_migrations_phase4.py::test_precommit_failure_rolls_back_schema_data_version_preserving_safety[precommit]
tests/integration/persistence/test_migrations_phase4.py::test_required_safety_failure_never_starts_migration_body
tests/integration/persistence/test_migrations_phase4.py::test_postcommit_failure_is_not_fake_rollback_and_startup_routes_emergency
tests/integration/persistence/test_migrations_phase4.py::test_direct_postcommit_failure_type
tests/integration/persistence/test_migrations_phase4.py::test_newer_schema_remains_unchanged_and_real_registry_has_no_product_v2

7 tests collected in 0.03s
```

## 5. `uv run pytest tests/unit/core -q`

Exit code: 0

```text
........................................................................ [ 33%]
........................................................................ [ 67%]
.....................................................................    [100%]
213 passed in 0.88s
```

## 6. `uv run pytest tests/integration/persistence -q`

Exit code: 0

```text
........................................................................ [ 24%]
........................................................................ [ 48%]
........................................................................ [ 72%]
........................................................................ [ 96%]
............                                                             [100%]
300 passed in 17.03s
```

## 7. `uv run pytest tests/integration/application -q`

Exit code: 0

```text
........................................................................ [ 33%]
........................................................................ [ 67%]
....................................................................     [100%]
212 passed in 30.78s
```

## 8. `uv run pytest tests/integration/persistence --ignore=tests/integration/persistence/test_migrations_phase4.py -q`

Exit code: 0

```text
........................................................................ [ 24%]
........................................................................ [ 49%]
........................................................................ [ 73%]
........................................................................ [ 98%]
.....                                                                    [100%]
293 passed in 15.30s
```

## 9. `uv run pytest tests/integration/application --ignore=tests/integration/application/reliability -q`

Exit code: 0

```text
........................................................................ [ 47%]
........................................................................ [ 94%]
.........                                                                [100%]
153 passed in 23.25s
```

## 10. `uv run ruff check .`

Exit code: 0

```text
All checks passed!
```

## 11. `uv run ruff format --check .`

Exit code: 0

```text
109 files already formatted
```

