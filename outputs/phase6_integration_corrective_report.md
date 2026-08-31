# Phase 6 Integration Corrective Report

## Files modified

```text
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\desktop_session.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\desktop_boundary.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\desktop_window.py
```

## Files created

```text
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\desktop\test_compound_failure_priority.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\desktop\test_confirmation_lifetime.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\phase6_integration_corrective_report.md
```

No files removed. All 71 previously accepted test/helper Python files remain hash-identical.

## Regime ticket lifecycle

Begin issues a local UI ticket and a matching Session authority bound to the selected character. Confirm removes the UI ticket and the business call consumes the Session ticket exactly once. A finally cleanup revokes any remaining authority if the confirmation aborts before consumption, including a pre-action rendering failure.

Back, navigation away and Maintenance re-entry/reload revoke the matching Session ticket and clear the UI ticket before new page data is populated. Existing Session disposal still clears all tickets; its semantics were not changed.

## Navigation cancellation

All production Round/Maintenance/Correction/Restore navigation cancels active administrative confirmations before changing page. Re-entering any administrative page also cancels the previous interaction before querying/populating. Maintenance returns with enabled table, no selection and a visible Start control. Fresh selection and Begin are required.

## Confirmation identity

Cancellation matches the exact currently active ticket object. None, repeated cancellation, unrelated objects and late cancellation of an older ticket cannot revoke a newer ticket. Canceled Isaac authority is rejected; fresh Magdalene confirmation changes only Magdalene and creates one Recent attempt. Actual queued duplicate confirmations still execute at most one mutation.

## Correction / Restore ticket symmetry

Dedicated cancel_regime/cancel_correction/cancel_restore delegate to a narrow matching-identity revocation primitive. Every cancellation requires an active Session and performs no UoW, business mutation or backup.

Correction/Restore Back, navigation, re-entry and backup reload revoke both layers. Emergency Restore uses the same cancellation behavior. GuardedWorkflow, Session disposal and Restore rebuild/runtime-result identity semantics are unchanged.

## Error priority

The boundary drains operational warnings and selects one final banner outcome. Unexpected errors retain their safe message and their own Error ID, with warning text appended below at error severity. Expected errors also outrank warnings. Warning-only actions remain warning severity; error-only actions remain error severity. Input feedback stays inline.

A combined error/warning rendering failure is logged without another rendering attempt or business retry.

## Compound failure

Regime commit + Recent failure + Maintenance refresh failure:

- Exactly one regime was committed and one Recent attempt occurred.
- No automatic retry or rollback.
- Final banner retained the unexpected Error ID and Recent warning.

Correction commit + Recent failure + candidate or Maintenance refresh failure:

- Original A remained voided; exactly one completed replacement B superseded A.
- Corrected stats and verified Safety remained.
- Exactly one Safety and one Recent attempt occurred.
- Final banner retained the unexpected Error ID and Recent warning.

Post-commit rendering failure and failure of the combined error presentation were also tested.

## Tests added

40 focused new cases across two files.

Confirmation lifetime (31 cases):

- test_regime_round_trip_revokes_authority_and_restores_usable_maintenance
- test_fresh_magdalene_confirmation_cannot_use_stale_isaac_identity
- test_navigation_and_reentry_revoke_both_ticket_layers
- test_back_revokes_ui_and_session_without_business_or_backup
- test_cancellation_is_matching_identity_only_and_idempotent
- test_cancellation_requires_active_session
- test_failed_page_reload_revokes_before_query_or_population
- test_confirm_revokes_even_if_pre_action_render_aborts
- test_emergency_restore_cancellation_revokes_authority

Error priority (9 cases):

- test_regime_commit_recent_failure_refresh_failure_retains_unexpected_id
- test_correction_commit_recent_failure_refresh_failure_retains_unexpected_id
- test_single_failure_presentation_remains_warning_or_error
- test_combined_presentation_failure_logs_once_without_recursive_render_or_retry
- test_post_commit_render_failure_also_keeps_recent_warning_below_error
- test_expected_error_also_outranks_operational_warning

```text
uv run pytest tests/integration/desktop/test_confirmation_lifetime.py tests/integration/desktop/test_compound_failure_priority.py -q
```

40 passed in 6.35s.

## Phase 6 integration tests

```text
uv run pytest tests/integration/desktop --collect-only -q
uv run pytest tests/integration/desktop -q
```

120 collected; 120 passed in 18.94s. Existing 80 integration tests preserved; 40 new corrective cases.

## Full tests

```text
uv run pytest
```

992 passed in 55.89s.

- failed: 0
- skipped: 0
- xfailed: 0
- xpassed: 0

Original accepted baseline 952 plus 40 corrective cases; no accepted test was modified, removed, skipped or marked xfail.

## Phase 1-5 regressions

```text
uv run pytest tests/unit/core -q
```

Phase 1: 213 passed in 0.70s.

```text
uv run pytest tests/integration/persistence --ignore=tests/integration/persistence/test_migrations_phase4.py -q
```

Phase 2 original baseline: 293 passed in 15.37s.

```text
uv run pytest tests/integration/application --ignore=tests/integration/application/reliability --ignore=tests/integration/application/test_presentation_capabilities.py -q
```

Phase 3 original baseline: 153 passed in 22.08s.

```text
uv run pytest tests/integration/application/reliability tests/integration/infrastructure tests/integration/persistence/test_migrations_phase4.py -q
```

Phase 4: 107 passed in 18.07s.

```text
uv run pytest tests/ui tests/integration/application/test_presentation_capabilities.py -q
```

Phase 5: 106 passed in 18.14s.

The --ignore flags only isolate historical phase groups; the corresponding later-phase tests were run separately and included in the unfiltered full suite.

## Ruff

`uv run ruff check .`: All checks passed!

`uv run ruff format --check .`: 174 files already formatted (exit code 0).

## Schema

Schema v1 unchanged

SPEC, Schema, Core mathematics, accepted Phase 1-5 source files and persistence behavior are unchanged.

## SPEC deviations

none

## SPEC concerns

The accepted Application layer still has no void-only completed-record service for incorrect pre-run facts. This optional capability remains unexposed. No new mutation path or replacement prediction was invented.

## Incomplete work

none for Phase 6 code implementation.

## Manual DPI

- Windows 125% manual DPI: pending.
- Windows 150% manual DPI: pending.

Only automated structural/offscreen UI tests were run.

## Phase 7 work

none

Phase 6 integration corrective pass complete. No Phase 7 implementation was started.
