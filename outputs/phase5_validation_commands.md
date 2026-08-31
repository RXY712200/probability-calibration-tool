# Phase 5 validation commands

Working directory: `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability`

Environment: Windows, Python 3.13.14, pytest 9.1.1, PySide6 6.11.2.

Dependency operation: `uv sync` (successful; 4 Qt packages installed at 6.11.2).

Below are the literal final validation commands and captured outputs, not a transcript of every exploratory/debug command. Initial new-test fixture and Qt initial-selection issues were corrected without editing accepted tests. Offscreen font discovery returned no families; the test fixture now explicitly loads Segoe UI for meaningful layout checks.

## 1. `uv run pytest`

Exit code: 0

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability
configfile: pyproject.toml
testpaths: tests
collected 860 items

tests\integration\application\reliability\test_application_invariants.py . [  0%]
......                                                                   [  0%]
tests\integration\application\reliability\test_restore.py .............. [  2%]
............                                                             [  3%]
tests\integration\application\reliability\test_restore_runtime_state.py . [  3%]
..................                                                       [  6%]
tests\integration\application\reliability\test_startup.py .............. [  7%]
.....                                                                    [  8%]
tests\integration\application\reliability\test_stats_validation.py ..... [  8%]
..                                                                       [  9%]
tests\integration\application\test_calculate.py ........................ [ 11%]
...                                                                      [ 12%]
tests\integration\application\test_correction.py ....................... [ 14%]
.........                                                                [ 15%]
tests\integration\application\test_lifecycle.py ...................      [ 18%]
tests\integration\application\test_presentation_capabilities.py ....     [ 18%]
tests\integration\application\test_recalculate.py ..............         [ 20%]
tests\integration\application\test_recovery.py ...........               [ 21%]
tests\integration\application\test_regime_maintenance.py ............    [ 22%]
tests\integration\application\test_revision_lock.py ...................  [ 25%]
tests\integration\application\test_workflow.py ...................       [ 27%]
tests\integration\infrastructure\test_backup.py .............            [ 28%]
tests\integration\infrastructure\test_logging.py ..                      [ 29%]
tests\integration\infrastructure\test_paths.py .                         [ 29%]
tests\integration\infrastructure\test_runtime_lock.py ..                 [ 29%]
tests\integration\infrastructure\test_sqlite_health.py ....              [ 29%]
tests\integration\persistence\test_character_constraints.py ........     [ 30%]
tests\integration\persistence\test_initialization.py .......             [ 31%]
tests\integration\persistence\test_migrations_phase4.py .......          [ 32%]
tests\integration\persistence\test_mutation_primitives.py .............. [ 34%]
.................................                                        [ 37%]
tests\integration\persistence\test_persistence.py .......                [ 38%]
tests\integration\persistence\test_regime_constraints.py ........        [ 39%]
tests\integration\persistence\test_repositories.py ..................... [ 42%]
.........                                                                [ 43%]
tests\integration\persistence\test_round_constraints.py ................ [ 45%]
...............................                                          [ 48%]
tests\integration\persistence\test_snapshot_constraints.py ............. [ 50%]
........................................................................ [ 58%]
................................                                         [ 62%]
tests\integration\persistence\test_stats_constraints.py ...........      [ 63%]
tests\integration\persistence\test_stats_rebuild.py ....                 [ 63%]
tests\integration\persistence\test_unit_of_work.py .......               [ 64%]
tests\ui\test_analysis_safety.py ..........                              [ 65%]
tests\ui\test_architecture_formatting.py ......                          [ 66%]
tests\ui\test_close_guard.py .......................                     [ 69%]
tests\ui\test_dpi_structure.py ..                                        [ 69%]
tests\ui\test_maintenance.py ..                                          [ 69%]
tests\ui\test_pre_run.py ........................                        [ 72%]
tests\ui\test_recovery_ui.py ......                                      [ 73%]
tests\ui\test_startup_pages.py .........                                 [ 74%]
tests\ui\test_workflow_contract.py ........                              [ 75%]
tests\unit\core\test_ev.py .............................                 [ 78%]
tests\unit\core\test_historical.py ...................                   [ 80%]
tests\unit\core\test_subjective.py ..................................... [ 85%]
........................................................................ [ 93%]
................                                                         [ 95%]
tests\unit\core\test_validation.py ..................................... [ 99%]
...                                                                      [100%]

============================ 860 passed in 36.82s =============================
```

## 2. `uv run pytest tests/ui --collect-only -q`

Exit code: 0

```text
tests/ui/test_analysis_safety.py::test_stale_history_is_cleared_not_just_hidden[hidden]
tests/ui/test_analysis_safety.py::test_stale_history_is_cleared_not_just_hidden[no_history]
tests/ui/test_analysis_safety.py::test_stale_history_is_cleared_not_just_hidden[insufficient]
tests/ui/test_analysis_safety.py::test_real_safe_view_leaks_no_history_numbers[hidden_valid]
tests/ui/test_analysis_safety.py::test_real_safe_view_leaks_no_history_numbers[no_history]
tests/ui/test_analysis_safety.py::test_real_safe_view_leaks_no_history_numbers[insufficient]
tests/ui/test_analysis_safety.py::test_new_draft_clears_all_analysis_including_hidden_widgets[complete]
tests/ui/test_analysis_safety.py::test_new_draft_clears_all_analysis_including_hidden_widgets[void]
tests/ui/test_analysis_safety.py::test_visible_subjective_and_history_are_separate_safe_cards
tests/ui/test_analysis_safety.py::test_presenting_safety_page_clears_off_page_analysis
tests/ui/test_architecture_formatting.py::test_ui_has_no_persistence_math_private_workflow_or_event_pumping
tests/ui/test_architecture_formatting.py::test_local_timestamp_and_readable_formatting_do_not_mutate_values
tests/ui/test_architecture_formatting.py::test_command_conversion_defers_validity_to_application[]
tests/ui/test_architecture_formatting.py::test_command_conversion_defers_validity_to_application[garbage]
tests/ui/test_architecture_formatting.py::test_command_conversion_defers_validity_to_application[1.1]
tests/ui/test_architecture_formatting.py::test_command_conversion_defers_validity_to_application[1000]
tests/ui/test_close_guard.py::test_close_policy[draft-choices0-CloseDecision.ACCEPT]
tests/ui/test_close_guard.py::test_close_policy[pending_locked-choices1-CloseDecision.ACCEPT]
tests/ui/test_close_guard.py::test_close_policy[pending_edit-choices2-CloseDecision.CONFIRM_EDITS]
tests/ui/test_close_guard.py::test_close_policy[pending_locked-choices3-CloseDecision.CONFIRM_CHOICES]
tests/ui/test_close_guard.py::test_close_policy[pending_locked-choices4-CloseDecision.CONFIRM_CHOICES]
tests/ui/test_close_guard.py::test_close_policy[confirm_save-choices5-CloseDecision.CONFIRM_CHOICES]
tests/ui/test_close_guard.py::test_close_policy[calculating-choices6-CloseDecision.IGNORE]
tests/ui/test_close_guard.py::test_close_policy[completing-choices7-CloseDecision.IGNORE]
tests/ui/test_close_guard.py::test_close_policy[recovery-choices8-CloseDecision.ACCEPT]
tests/ui/test_close_guard.py::test_close_policy[recovery_error-choices9-CloseDecision.ACCEPT]
tests/ui/test_close_guard.py::test_close_policy[completed_notice-choices10-CloseDecision.ACCEPT]
tests/ui/test_close_guard.py::test_real_close_event_never_mutates_database[False-draft]
tests/ui/test_close_guard.py::test_real_close_event_never_mutates_database[False-locked]
tests/ui/test_close_guard.py::test_real_close_event_never_mutates_database[False-edit]
tests/ui/test_close_guard.py::test_real_close_event_never_mutates_database[False-choices]
tests/ui/test_close_guard.py::test_real_close_event_never_mutates_database[False-confirm]
tests/ui/test_close_guard.py::test_real_close_event_never_mutates_database[True-draft]
tests/ui/test_close_guard.py::test_real_close_event_never_mutates_database[True-locked]
tests/ui/test_close_guard.py::test_real_close_event_never_mutates_database[True-edit]
tests/ui/test_close_guard.py::test_real_close_event_never_mutates_database[True-choices]
tests/ui/test_close_guard.py::test_real_close_event_never_mutates_database[True-confirm]
tests/ui/test_close_guard.py::test_busy_close_is_ignored_without_mutation[calculating]
tests/ui/test_close_guard.py::test_busy_close_is_ignored_without_mutation[completing]
tests/ui/test_dpi_structure.py::test_resizable_layout_character_stability_and_confirmation_access[size0]
tests/ui/test_dpi_structure.py::test_resizable_layout_character_stability_and_confirmation_access[size1]
tests/ui/test_maintenance.py::test_maintenance_safe_columns_and_in_page_regime_confirmation
tests/ui/test_maintenance.py::test_pending_disables_regime_ui_and_service_still_guards
tests/ui/test_pre_run.py::test_first_run_defaults
tests/ui/test_pre_run.py::test_exact_matrix_mapping_and_exclusive_choices
tests/ui/test_pre_run.py::test_enter_never_calculates[False-16777220-probability]
tests/ui/test_pre_run.py::test_enter_never_calculates[False-16777220-win_odds]
tests/ui/test_pre_run.py::test_enter_never_calculates[False-16777220-lose_odds]
tests/ui/test_pre_run.py::test_enter_never_calculates[False-16777221-probability]
tests/ui/test_pre_run.py::test_enter_never_calculates[False-16777221-win_odds]
tests/ui/test_pre_run.py::test_enter_never_calculates[False-16777221-lose_odds]
tests/ui/test_pre_run.py::test_enter_never_calculates[True-16777220-probability]
tests/ui/test_pre_run.py::test_enter_never_calculates[True-16777220-win_odds]
tests/ui/test_pre_run.py::test_enter_never_calculates[True-16777220-lose_odds]
tests/ui/test_pre_run.py::test_enter_never_calculates[True-16777221-probability]
tests/ui/test_pre_run.py::test_enter_never_calculates[True-16777221-win_odds]
tests/ui/test_pre_run.py::test_enter_never_calculates[True-16777221-lose_odds]
tests/ui/test_pre_run.py::test_inline_errors_preserve_raw_text[probability-105-subjective_probability]
tests/ui/test_pre_run.py::test_inline_errors_preserve_raw_text[probability-garbage-subjective_probability]
tests/ui/test_pre_run.py::test_inline_errors_preserve_raw_text[probability-1.5-subjective_probability]
tests/ui/test_pre_run.py::test_inline_errors_preserve_raw_text[win_odds-2,00-win_odds]
tests/ui/test_pre_run.py::test_inline_errors_preserve_raw_text[win_odds-1e2-win_odds]
tests/ui/test_pre_run.py::test_inline_errors_preserve_raw_text[lose_odds-NaN-lose_odds]
tests/ui/test_pre_run.py::test_inline_errors_preserve_raw_text[lose_odds-0.9-lose_odds]
tests/ui/test_pre_run.py::test_endpoint_note_preserves_raw_input[0-1]
tests/ui/test_pre_run.py::test_endpoint_note_preserves_raw_input[100-99]
tests/ui/test_pre_run.py::test_valid_calculate_locks_fields_and_preserves_odds
tests/ui/test_recovery_ui.py::test_real_recovery_safe_render_and_continue_without_recalculate[hidden]
tests/ui/test_recovery_ui.py::test_real_recovery_safe_render_and_continue_without_recalculate[no_history]
tests/ui/test_recovery_ui.py::test_real_recovery_safe_render_and_continue_without_recalculate[insufficient]
tests/ui/test_recovery_ui.py::test_real_recovery_safe_render_and_continue_without_recalculate[visible]
tests/ui/test_recovery_ui.py::test_recovery_does_not_create_persisted_session_preferences
tests/ui/test_recovery_ui.py::test_no_pending_inspection_stays_draft_without_error
tests/ui/test_startup_pages.py::test_all_startup_dispositions_have_safe_presentation[ready_draft]
tests/ui/test_startup_pages.py::test_all_startup_dispositions_have_safe_presentation[ready_recovery]
tests/ui/test_startup_pages.py::test_all_startup_dispositions_have_safe_presentation[recovery_error]
tests/ui/test_startup_pages.py::test_all_startup_dispositions_have_safe_presentation[emergency_recovery]
tests/ui/test_startup_pages.py::test_all_startup_dispositions_have_safe_presentation[unsupported_newer_schema]
tests/ui/test_startup_pages.py::test_all_startup_dispositions_have_safe_presentation[already_running]
tests/ui/test_startup_pages.py::test_all_startup_dispositions_have_safe_presentation[data_safety_error]
tests/ui/test_startup_pages.py::test_emergency_requires_explicit_valid_selection_and_injected_action
tests/ui/test_startup_pages.py::test_operational_warning_does_not_claim_transaction_failed
tests/ui/test_workflow_contract.py::test_real_workflow_calculate_modify_recalculate
tests/ui/test_workflow_contract.py::test_failed_recalculate_preserves_candidate_and_committed_analysis
tests/ui/test_workflow_contract.py::test_audit_lock_post_choices_back_and_rejected_widget_signal
tests/ui/test_workflow_contract.py::test_completed_reset_and_session_only_retention
tests/ui/test_workflow_contract.py::test_void_in_page_confirmation_does_not_delete
tests/ui/test_workflow_contract.py::test_official_analysis_not_shown_until_calculate_returns
tests/ui/test_workflow_contract.py::test_unexpected_error_uses_safe_phase4_dto
tests/ui/test_workflow_contract.py::test_completing_disables_conflicting_controls_and_rejects_close

90 tests collected in 0.03s
```

## 3. `uv run pytest tests/ui -q`

Exit code: 0

```text
........................................................................ [ 80%]
..................                                                       [100%]
90 passed in 8.32s
```

## 4. `uv run pytest tests/integration/application/test_presentation_capabilities.py -q`

Exit code: 0

```text
....                                                                     [100%]
4 passed in 0.13s
```

## 5. `uv run pytest tests/unit/core -q`

Exit code: 0

```text
........................................................................ [ 33%]
........................................................................ [ 67%]
.....................................................................    [100%]
213 passed in 0.79s
```

## 6. `uv run pytest tests/integration/persistence --ignore=tests/integration/persistence/test_migrations_phase4.py -q`

Exit code: 0

```text
........................................................................ [ 24%]
........................................................................ [ 49%]
........................................................................ [ 73%]
........................................................................ [ 98%]
.....                                                                    [100%]
293 passed in 9.57s
```

## 7. `uv run pytest tests/integration/application --ignore=tests/integration/application/reliability --ignore=tests/integration/application/test_presentation_capabilities.py -q`

Exit code: 0

```text
........................................................................ [ 47%]
........................................................................ [ 94%]
.........                                                                [100%]
153 passed in 17.56s
```

## 8. `uv run pytest tests/integration/infrastructure tests/integration/application/reliability tests/integration/persistence/test_migrations_phase4.py -q`

Exit code: 0

```text
........................................................................ [ 67%]
...................................                                      [100%]
107 passed in 14.80s
```

## 9. `uv run ruff check .`

Exit code: 0

```text
All checks passed!
```

## 10. `uv run ruff format --check .`

Exit code: 0

```text
141 files already formatted
```

