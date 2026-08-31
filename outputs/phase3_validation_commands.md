# Phase 3 Validation Commands

Working directory: `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability`.

These are literal final validation commands and captured results after implementation. All six commands exited successfully.

## `uv run pytest tests/integration/application --collect-only -q`

Exit code: 0

```text
tests/integration/application/test_calculate.py::test_calculate_safe_history_matrix_golden_a_b_c[counts0-no_history-False]
tests/integration/application/test_calculate.py::test_calculate_safe_history_matrix_golden_a_b_c[counts0-no_history-True]
tests/integration/application/test_calculate.py::test_calculate_safe_history_matrix_golden_a_b_c[counts1-insufficient-False]
tests/integration/application/test_calculate.py::test_calculate_safe_history_matrix_golden_a_b_c[counts1-insufficient-True]
tests/integration/application/test_calculate.py::test_calculate_safe_history_matrix_golden_a_b_c[counts2-valid-False]
tests/integration/application/test_calculate.py::test_calculate_safe_history_matrix_golden_a_b_c[counts2-valid-True]
tests/integration/application/test_calculate.py::test_golden_c_exposure_and_snapshot_durable_before_view_construction
tests/integration/application/test_calculate.py::test_calculate_atomicity_and_no_official_release[snapshot_insert]
tests/integration/application/test_calculate.py::test_calculate_atomicity_and_no_official_release[commit]
tests/integration/application/test_calculate.py::test_core_validation_translated_to_field_errors_without_writes[changes0-subjective_probability]
tests/integration/application/test_calculate.py::test_core_validation_translated_to_field_errors_without_writes[changes1-subjective_probability]
tests/integration/application/test_calculate.py::test_core_validation_translated_to_field_errors_without_writes[changes2-subjective_probability]
tests/integration/application/test_calculate.py::test_core_validation_translated_to_field_errors_without_writes[changes3-subjective_probability]
tests/integration/application/test_calculate.py::test_core_validation_translated_to_field_errors_without_writes[changes4-win_odds]
tests/integration/application/test_calculate.py::test_core_validation_translated_to_field_errors_without_writes[changes5-win_odds]
tests/integration/application/test_calculate.py::test_core_validation_translated_to_field_errors_without_writes[changes6-win_odds]
tests/integration/application/test_calculate.py::test_core_validation_translated_to_field_errors_without_writes[changes7-win_odds]
tests/integration/application/test_calculate.py::test_core_validation_translated_to_field_errors_without_writes[changes8-lose_odds]
tests/integration/application/test_calculate.py::test_core_validation_translated_to_field_errors_without_writes[changes9-lose_odds]
tests/integration/application/test_calculate.py::test_core_validation_translated_to_field_errors_without_writes[changes10-reference_history]
tests/integration/application/test_calculate.py::test_core_validation_translated_to_field_errors_without_writes[changes11-character_id]
tests/integration/application/test_calculate.py::test_core_validation_translated_to_field_errors_without_writes[changes12-character_id]
tests/integration/application/test_calculate.py::test_core_boundary_normalization_not_reimplemented[0-1]
tests/integration/application/test_calculate.py::test_core_boundary_normalization_not_reimplemented[100-99]
tests/integration/application/test_calculate.py::test_pending_blocks_second_calculation_globally
tests/integration/application/test_calculate.py::test_history_eligibility_is_same_character_current_regime_and_completed_included
tests/integration/application/test_calculate.py::test_history_last_id_uses_prediction_chronology_not_uuid
tests/integration/application/test_correction.py::test_correction_exact_a_b_facts_timestamps_and_snapshot_without_math
tests/integration/application/test_correction.py::test_correction_rebuilds_source_stats_for_inclusion_changes[False-False]
tests/integration/application/test_correction.py::test_correction_rebuilds_source_stats_for_inclusion_changes[False-True]
tests/integration/application/test_correction.py::test_correction_rebuilds_source_stats_for_inclusion_changes[True-False]
tests/integration/application/test_correction.py::test_correction_rebuilds_source_stats_for_inclusion_changes[True-True]
tests/integration/application/test_correction.py::test_backup_failure_precedes_any_correction_transaction_or_id_generation
tests/integration/application/test_correction.py::test_verified_backup_finishes_before_first_mutation
tests/integration/application/test_correction.py::test_correction_rollback_restores_a_snapshot_and_stats_and_removes_b[after_A]
tests/integration/application/test_correction.py::test_correction_rollback_restores_a_snapshot_and_stats_and_removes_b[B_snapshot]
tests/integration/application/test_correction.py::test_correction_rollback_restores_a_snapshot_and_stats_and_removes_b[stats]
tests/integration/application/test_correction.py::test_correction_rollback_restores_a_snapshot_and_stats_and_removes_b[commit]
tests/integration/application/test_correction.py::test_correction_chains_allowed_but_branching_is_semantic_error
tests/integration/application/test_correction.py::test_prerun_correction_is_impossible_in_public_api[character_id]
tests/integration/application/test_correction.py::test_prerun_correction_is_impossible_in_public_api[p_h_raw]
tests/integration/application/test_correction.py::test_prerun_correction_is_impossible_in_public_api[win_odds_raw]
tests/integration/application/test_correction.py::test_prerun_correction_is_impossible_in_public_api[lose_odds_raw]
tests/integration/application/test_correction.py::test_prerun_correction_is_impossible_in_public_api[win_odds]
tests/integration/application/test_correction.py::test_prerun_correction_is_impossible_in_public_api[lose_odds]
tests/integration/application/test_correction.py::test_prerun_correction_is_impossible_in_public_api[reference_history]
tests/integration/application/test_correction.py::test_prerun_correction_is_impossible_in_public_api[snapshot]
tests/integration/application/test_correction.py::test_prerun_correction_is_impossible_in_public_api[history_regime_id]
tests/integration/application/test_correction.py::test_correction_requires_nonempty_text_reason[None]
tests/integration/application/test_correction.py::test_correction_requires_nonempty_text_reason[]
tests/integration/application/test_correction.py::test_correction_requires_nonempty_text_reason[ \t\n]
tests/integration/application/test_correction.py::test_correction_requires_nonempty_text_reason[123]
tests/integration/application/test_correction.py::test_correction_fact_validation[1-True-result]
tests/integration/application/test_correction.py::test_correction_fact_validation[True-None-include_character_history]
tests/integration/application/test_correction.py::test_pending_anywhere_blocks_correction_before_backup
tests/integration/application/test_correction.py::test_missing_correction_target_is_semantic_error
tests/integration/application/test_correction.py::test_correction_rechecks_pending_after_backup
tests/integration/application/test_correction.py::test_correction_of_old_regime_rebuilds_only_that_regime
tests/integration/application/test_correction.py::test_leakage_round21_stays_at_twenty_after_completion_and_later_correction
tests/integration/application/test_lifecycle.py::test_complete_included_atomically_updates_facts_and_stats_not_snapshot[False]
tests/integration/application/test_lifecycle.py::test_complete_included_atomically_updates_facts_and_stats_not_snapshot[True]
tests/integration/application/test_lifecycle.py::test_excluded_completion_preserves_audit_without_stats_or_future_history[False]
tests/integration/application/test_lifecycle.py::test_excluded_completion_preserves_audit_without_stats_or_future_history[True]
tests/integration/application/test_lifecycle.py::test_complete_rollback_restores_pending_postrun_nulls_and_stats[before_stats]
tests/integration/application/test_lifecycle.py::test_complete_rollback_restores_pending_postrun_nulls_and_stats[after_stats]
tests/integration/application/test_lifecycle.py::test_complete_rollback_restores_pending_postrun_nulls_and_stats[commit]
tests/integration/application/test_lifecycle.py::test_pending_void_is_terminal_and_preserves_snapshot[None]
tests/integration/application/test_lifecycle.py::test_pending_void_is_terminal_and_preserves_snapshot[Abandoned before the outcome]
tests/integration/application/test_lifecycle.py::test_void_commit_failure_preserves_pending
tests/integration/application/test_lifecycle.py::test_completion_requires_explicit_boolean_facts[1-True-result]
tests/integration/application/test_lifecycle.py::test_completion_requires_explicit_boolean_facts[None-True-result]
tests/integration/application/test_lifecycle.py::test_completion_requires_explicit_boolean_facts[win-True-result]
tests/integration/application/test_lifecycle.py::test_completion_requires_explicit_boolean_facts[True-0-include_character_history]
tests/integration/application/test_lifecycle.py::test_completion_requires_explicit_boolean_facts[True-None-include_character_history]
tests/integration/application/test_lifecycle.py::test_missing_round_is_semantic_error[complete]
tests/integration/application/test_lifecycle.py::test_missing_round_is_semantic_error[void]
tests/integration/application/test_lifecycle.py::test_missing_round_is_semantic_error[recalculate]
tests/integration/application/test_lifecycle.py::test_naive_clock_is_rejected_and_aware_offsets_are_normalized
tests/integration/application/test_recalculate.py::test_recalculate_preserves_identity_created_at_and_replaces_full_snapshot
tests/integration/application/test_recalculate.py::test_recalculate_rollback_then_retry_all_fields[snapshot_update-False]
tests/integration/application/test_recalculate.py::test_recalculate_rollback_then_retry_all_fields[snapshot_update-True]
tests/integration/application/test_recalculate.py::test_recalculate_rollback_then_retry_all_fields[commit-False]
tests/integration/application/test_recalculate.py::test_recalculate_rollback_then_retry_all_fields[commit-True]
tests/integration/application/test_recalculate.py::test_golden_d_odds_only_and_reference_only_do_not_compromise
tests/integration/application/test_recalculate.py::test_golden_e_f_old_exposure_compromise_is_irreversible[golden_E]
tests/integration/application/test_recalculate.py::test_golden_e_f_old_exposure_compromise_is_irreversible[golden_F]
tests/integration/application/test_recalculate.py::test_golden_g_first_exposure_same_recalc_uses_old_flag
tests/integration/application/test_recalculate.py::test_golden_h_first_timestamp_survives_off_on_and_history_status_change
tests/integration/application/test_recalculate.py::test_changed_character_uses_new_characters_active_regime_only
tests/integration/application/test_recalculate.py::test_actual_raw_change_not_clamped_probability_controls_compromise
tests/integration/application/test_recalculate.py::test_terminal_snapshots_cannot_be_recalculated[completed]
tests/integration/application/test_recalculate.py::test_terminal_snapshots_cannot_be_recalculated[voided]
tests/integration/application/test_recovery.py::test_recovery_zero_pending_has_no_analysis
tests/integration/application/test_recovery.py::test_recovery_same_round_same_snapshot_without_math_writes_or_new_id[False-counts0-hidden]
tests/integration/application/test_recovery.py::test_recovery_same_round_same_snapshot_without_math_writes_or_new_id[True-counts1-no_history]
tests/integration/application/test_recovery.py::test_recovery_same_round_same_snapshot_without_math_writes_or_new_id[True-counts2-insufficient]
tests/integration/application/test_recovery.py::test_recovery_same_round_same_snapshot_without_math_writes_or_new_id[True-counts3-visible]
tests/integration/application/test_recovery.py::test_multiple_pending_is_semantic_recovery_error_never_selects_one
tests/integration/application/test_recovery.py::test_multiple_pending_detected_again_on_continue
tests/integration/application/test_recovery.py::test_recovery_exposure_contradiction_fails_closed_without_history_release
tests/integration/application/test_recovery.py::test_pending_edit_crash_restores_old_inputs_and_snapshot
tests/integration/application/test_recovery.py::test_postrun_choices_lost_on_crash_without_persisting_result
tests/integration/application/test_recovery.py::test_missing_snapshot_fails_closed
tests/integration/application/test_regime_maintenance.py::test_regime_switch_preserves_old_history_reason_and_initializes_zero_cache
tests/integration/application/test_regime_maintenance.py::test_pending_blocks_regime_switch_for_every_character[1]
tests/integration/application/test_regime_maintenance.py::test_pending_blocks_regime_switch_for_every_character[2]
tests/integration/application/test_regime_maintenance.py::test_regime_switch_rollback[new_regime]
tests/integration/application/test_regime_maintenance.py::test_regime_switch_rollback[zero_stats]
tests/integration/application/test_regime_maintenance.py::test_regime_switch_rollback[commit]
tests/integration/application/test_regime_maintenance.py::test_maintenance_dto_is_structurally_nondirectional_before_lock
tests/integration/application/test_regime_maintenance.py::test_missing_active_regime_fails_as_application_invariant[calculate]
tests/integration/application/test_regime_maintenance.py::test_missing_active_regime_fails_as_application_invariant[regime]
tests/integration/application/test_regime_maintenance.py::test_missing_active_regime_fails_as_application_invariant[maintenance]
tests/integration/application/test_regime_maintenance.py::test_optional_reason_rejects_nontext[void]
tests/integration/application/test_regime_maintenance.py::test_optional_reason_rejects_nontext[regime]
tests/integration/application/test_workflow.py::test_states_are_memory_only_and_persistent_status_vocabulary_unchanged
tests/integration/application/test_workflow.py::test_transition_matrix_rejects_every_disallowed_origin[set_inputs-allowed0]
tests/integration/application/test_workflow.py::test_transition_matrix_rejects_every_disallowed_origin[calculate-allowed1]
tests/integration/application/test_workflow.py::test_transition_matrix_rejects_every_disallowed_origin[modify-allowed2]
tests/integration/application/test_workflow.py::test_transition_matrix_rejects_every_disallowed_origin[choose_result-allowed3]
tests/integration/application/test_workflow.py::test_transition_matrix_rejects_every_disallowed_origin[choose_include-allowed4]
tests/integration/application/test_workflow.py::test_transition_matrix_rejects_every_disallowed_origin[back-allowed5]
tests/integration/application/test_workflow.py::test_transition_matrix_rejects_every_disallowed_origin[confirm_save-allowed6]
tests/integration/application/test_workflow.py::test_transition_matrix_rejects_every_disallowed_origin[void_pending-allowed7]
tests/integration/application/test_workflow.py::test_transition_matrix_rejects_every_disallowed_origin[inspect_recovery-allowed8]
tests/integration/application/test_workflow.py::test_transition_matrix_rejects_every_disallowed_origin[continue_recovery-allowed9]
tests/integration/application/test_workflow.py::test_transition_matrix_rejects_every_disallowed_origin[dismiss_completed-allowed10]
tests/integration/application/test_workflow.py::test_successful_workflow_including_transient_states_and_back[False]
tests/integration/application/test_workflow.py::test_successful_workflow_including_transient_states_and_back[True]
tests/integration/application/test_workflow.py::test_calculation_failure_returns_to_correct_origin_and_keeps_committed_view[False]
tests/integration/application/test_workflow.py::test_calculation_failure_returns_to_correct_origin_and_keeps_committed_view[True]
tests/integration/application/test_workflow.py::test_completion_failure_returns_to_confirmation_and_allows_retry
tests/integration/application/test_workflow.py::test_void_workflow_returns_to_empty_draft
tests/integration/application/test_workflow.py::test_missing_inputs_and_invalid_choices_do_not_transition

134 tests collected in 0.04s
```

## `uv run ruff check .`

Exit code: 0

```text
All checks passed!
```

## `uv run ruff format --check .`

Exit code: 0

```text
74 files already formatted
```

## `uv run pytest`

Exit code: 0

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability
configfile: pyproject.toml
testpaths: tests
collected 640 items

tests\integration\application\test_calculate.py ........................ [  3%]
...                                                                      [  4%]
tests\integration\application\test_correction.py ....................... [  7%]
.........                                                                [  9%]
tests\integration\application\test_lifecycle.py ...................      [ 12%]
tests\integration\application\test_recalculate.py ..............         [ 14%]
tests\integration\application\test_recovery.py ...........               [ 16%]
tests\integration\application\test_regime_maintenance.py ............    [ 17%]
tests\integration\application\test_workflow.py ...................       [ 20%]
tests\integration\persistence\test_character_constraints.py ........     [ 22%]
tests\integration\persistence\test_initialization.py .......             [ 23%]
tests\integration\persistence\test_mutation_primitives.py .............. [ 25%]
.................................                                        [ 30%]
tests\integration\persistence\test_persistence.py .......                [ 31%]
tests\integration\persistence\test_regime_constraints.py ........        [ 32%]
tests\integration\persistence\test_repositories.py ..................... [ 36%]
.........                                                                [ 37%]
tests\integration\persistence\test_round_constraints.py ................ [ 40%]
...............................                                          [ 45%]
tests\integration\persistence\test_snapshot_constraints.py ............. [ 47%]
........................................................................ [ 58%]
................................                                         [ 63%]
tests\integration\persistence\test_stats_constraints.py ...........      [ 65%]
tests\integration\persistence\test_stats_rebuild.py ....                 [ 65%]
tests\integration\persistence\test_unit_of_work.py .......               [ 66%]
tests\unit\core\test_ev.py .............................                 [ 71%]
tests\unit\core\test_historical.py ...................                   [ 74%]
tests\unit\core\test_subjective.py ..................................... [ 80%]
........................................................................ [ 91%]
................                                                         [ 93%]
tests\unit\core\test_validation.py ..................................... [ 99%]
...                                                                      [100%]

============================ 640 passed in 16.71s =============================
```

## `uv run pytest tests/unit/core -q`

Exit code: 0

```text
........................................................................ [ 33%]
........................................................................ [ 67%]
.....................................................................    [100%]
213 passed in 0.64s
```

## `uv run pytest tests/integration/persistence -q`

Exit code: 0

```text
........................................................................ [ 24%]
........................................................................ [ 49%]
........................................................................ [ 73%]
........................................................................ [ 98%]
.....                                                                    [100%]
293 passed in 6.24s
```

## Intermediate checks

- Baseline `uv run pytest`: 506 passed.
- Incremental `uv run pytest tests/integration/application -q`: 27, 41, 72, 102, then 134 passed as test groups were added.
- Intermediate `uv run ruff check .`: one DTZ001 finding in an intentionally naive datetime test. Added a narrowly documented local suppression; the final check passed.
- Formatting commands executed:
  - `uv run ruff format src/probability_calibration_tool/application src/probability_calibration_tool/persistence/repositories/rounds.py`
  - `uv run ruff format tests/integration/application`
  - `uv run ruff format tests/integration/application/test_recalculate.py`
  - `uv run ruff format tests/integration/application/test_correction.py`
  - `uv run ruff format src/probability_calibration_tool/application tests/integration/application`
- Optional native PowerShell bytecode cleanup was rejected by environment policy before execution. No deletion occurred; verification found 69 .pyc files and 9 __pycache__ directories, ignored by the existing .gitignore.
