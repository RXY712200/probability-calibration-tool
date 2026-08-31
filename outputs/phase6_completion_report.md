# Phase 6 Completion Report

## Files created

```text
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\__main__.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\bootstrap.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\desktop_host.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\backup_catalog_service.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\correction_query_service.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\desktop_session.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\integrated_round_actions.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\correction_page.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\desktop_boundary.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\desktop_window.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\restore_page.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\safety_window.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\desktop\__init__.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\desktop\conftest.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\desktop\helpers.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\desktop\test_backup_catalog.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\desktop\test_bootstrap.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\desktop\test_correction_integration.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\desktop\test_end_to_end.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\desktop\test_error_boundary.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\desktop\test_recent_integration.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\desktop\test_regime_integration.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\desktop\test_restore_session_rebuild.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\desktop\test_startup_routing.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\phase6_completion_report.md
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\phase6_validation_commands.md
```

## Files modified

```text
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\rounds.py
```

No existing source/test file was removed.

## Schema

Schema v1 unchanged

SPEC SHA-256: `AEE4EB200BEA8EC1A652A65A2076645613E6057C37D6280A9A0787CC5B040FC4`.

Schema SHA-256: `FB457C818780A94EF62AB53A3ED02FC0779FF1C4B0001734FBD67D56486F9315`.

## Accepted-layer modifications

Only RoundRepository gained `correction_identifiers()`: an eager read-only query returning round ID, character display name and completed timestamp. This is necessary for the non-directional correction browser. No transaction, mutation, schema or existing query behavior changed.

All 59 accepted test/helper Python files are byte-for-byte unchanged. Core, Domain, accepted Workflow/services, Phase 4 reliability and original Phase 5 UI files are unchanged.

## Bootstrap

QApplication is created before StartupService. RuntimeContext surrounds host construction, initial routing and the Qt event loop. A finally block disposes host/session/window before the runtime context releases logging and the OS lock. No early aboutToQuit runtime shutdown.

Unpackaged launch from the project root:

```powershell
uv run --directory src python -m probability_calibration_tool
```

The module import and isolated actual module-entry subprocess were verified; interactive release acceptance was not claimed.

## __main__

Only imports bootstrap.main and raises SystemExit(main()). No business logic.

## Startup routing

- READY_DRAFT: real DesktopSession/Workflow and Draft.
- READY_RECOVERY: real session, exact recovery inspection, Recovery page.
- RECOVERY_ERROR: safety presentation without normal Workflow.
- EMERGENCY_RECOVERY: verified backup catalog and Emergency Restore, without normal Workflow.
- UNSUPPORTED_NEWER_SCHEMA: safe Close/error presentation; no business writes or restore override.
- ALREADY_RUNNING: notification then exit; no normal host/window/event loop.
- DATA_SAFETY_ERROR: safety presentation; Emergency Restore exposed only when the runtime unsafe flag permits it.

## READY_RECOVERY consistency

Workflow inspection must return RECOVERABLE. NONE/multiple inconsistencies are logged with Error ID and fail closed to safety. Continue is explicit; no automatic Workflow continuation. Read-only preview uses the accepted RecoveryService.

## DesktopSession

Coordinates real services, post-commit backup warnings, safe queries, confirmation tickets and Restore. Lifecycle state is active/disposed plus operation busy, not a duplicate business state machine. GuardedWorkflow delegates accepted semantics and revokes even previously captured callbacks after disposal.

## UoW lifecycle

Business and query operations use RuntimeContext-managed short-lived UoWs. Maintenance and correction DTOs are detached before return. No open UoW, cursor, repository or lazy DB generator escapes to UI. DTO use during runtime quiescence was tested.

## Recent backup integration

Exactly four successful post-commit triggers: Complete, Pending Void, Regime Switch and Historical Correction. Calculate/Recalculate, Modify, selections, Recovery inspection/Continue and administrative-page viewing do not trigger Recent.

## Recent failure semantics

Successful business commits remain authoritative. Backup failure produces a safe nonfatal warning. The authoritative new state and refreshed views render before the warning banner. No automatic business retry occurs after backup or rendering failure.

## Maintenance integration

Real MaintenanceService supplies the accepted five safe columns through detached DTOs. Viewing is permitted while pending; directional history is not exposed.

## Regime integration

Healthy active Draft and not busy are required for presentation/admin mutation. A one-shot confirmation ticket is consumed before service execution: one commit, one Recent attempt, then Maintenance refresh. Duplicate confirmation cannot create regime 3 from a single regime-1 confirmation sequence.

## Historical Correction

Candidates contain only round ID, character display name and completed time. UI accepts explicitly new result/include choices and a nonempty reason; it does not expose old results, probabilities, odds or snapshots.

The accepted CorrectionService uses the real SQLiteSafetyBackupAdapter: verified pre_history_correction Safety, atomic correction commit, Recent, candidate refresh, Maintenance refresh, then warning. Confirmation is one-shot. Safety failure prevents the correction write transaction and Recent; invalid inputs are rejected before Safety.

## Correction pre-run-fact limitation

No accepted void-only completed-record service exists. It was not invented or wired. The optional ability to void a completed record with incorrect pre-run facts remains unexposed; no replacement prediction is fabricated.

## Backup catalog

Only Phase 4 VALID inventory entries become candidate DTOs. UI receives opaque UUID handles, never file paths. Refresh invalidates the previous generation, including when refresh fails. Disposal revokes catalog access. RestoreService revalidates the selected file.

## Normal Restore

Explicit selection and in-page confirmation are required. Busy state immediately disables selection, confirmation and conflicting actions and ignores user close; production code never pumps events.

Rebuild uses identity of runtime.result, not the returned operation disposition. Pre-replacement failure preserves the same result object, session and usable Workflow. Replacement disposes the old session and builds a fresh presentation from the authoritative runtime.

## Emergency Restore

Corrupt startup creates no normal Workflow/UoW. Verified candidates initially have no selection. Failed pre-replacement recovery stays in the original safety session; successful replacement reroutes first and constructs a normal session only if the runtime permits it.

## Session rebuild

Old session is revoked before obsolete presentation is detached. Its Workflow methods, captured callbacks, queries, confirmations and catalog access reject use. New session/window receives fresh Workflow, views and candidate mappings. Restored pending data enters newly inspected Recovery without automatic Continue.

Post-replacement validation failure removes the normal session, preserves Safety, presents Emergency Restore and does not roll back automatically.

## Programmatic teardown

close_for_session_replacement disables, hides and schedules deletion of obsolete presentation without invoking user Close Guard, completing or voiding. Ordinary user close retains accepted Phase 5 behavior.

## Error boundary

Input errors are inline; expected business errors use a nonmodal banner; operational failures use warnings. Unexpected errors show a safe message/Error ID and log the same ID with traceback. Rendering failure is reported without recursive rendering or automatic mutation retry.

## Runtime lock lifecycle

Real OS lock remains held through the Qt event loop and host disposal. A second startup cannot acquire it. A new runtime acquires it after the previous context closes and observes durable pending Recovery.

## End-to-End

Executed real fresh startup → Calculate → close RuntimeContext A → StartupService/RuntimeContext B → Recovery inspection → explicit Continue → same committed round/snapshot → Save → Recent → Completed Notice → New Draft.

Also accumulated 19 wins/1 loss, verified history exposure was committed before rendering, and confirmed the next completed round did not change its prior snapshot. Integrity checks returned ok.

## Recent backup E2E

Independently reopened an actual VALID Recent file, verified the committed completed round and PRAGMA integrity_check = ok. Four trigger paths and their negative/failure cases passed.

## Restore E2E

Real Normal and Emergency replacement passed. Pre-replacement faults preserve original session and allow Calculate. Pending restore builds Recovery. Post-check failure revokes normal access. Actual queued Qt callbacks against the disposed old session are rejected.

## Correction E2E

Verified pre-correction Safety contains original completed A; A becomes voided, B completed and supersedes A; B snapshot exactly copies A except round ID; stats rebuild; Recent contains corrected data. Safety/Recent faults and duplicate confirmation passed.

## Tests

`uv run pytest`: **952 passed, 0 failed, 0 skipped, 0 xfailed, 0 xpassed**.

Accepted baseline: 872; new Phase 6 tests: 80.

`uv run pytest tests/integration/desktop --collect-only -q`: 80 collected.

`uv run pytest tests/integration/desktop -q`: 80 passed.

Focused Restore/Recent/Correction/startup/E2E command: 43 passed. Exact literal command strings and all regression commands are recorded in phase6_validation_commands.md.

## Adversarial integration tests

| # | Required family | Result |
|---|---|---|
| 1 | Runtime alive through real event loop | passed |
| 2 | Exact READY_RECOVERY inspection; no auto-continue | passed |
| 3 | Startup warning after initial render | passed |
| 4 | Complete success + Recent failure | passed |
| 5 | Void success + Recent failure | passed |
| 6 | Regime success + Recent failure | passed |
| 7 | Correction Safety failure blocks writes | passed |
| 8 | Correction success + Recent failure | passed |
| 9 | No Recent on Calculate/Recalculate | passed |
| 10 | One-shot Regime double confirmation | passed |
| 11 | One-shot Correction double confirmation | passed |
| 12 | Restore pre-failure preserves session | passed |
| 13 | Restore success disposes old session | passed |
| 14 | Queued stale callback rejected before dependencies | passed |
| 15 | Restored pending creates new inspected Workflow | passed |
| 16 | Post-check failure removes normal session | passed |
| 17 | Emergency startup without normal Workflow | passed |
| 18 | Emergency success constructs normal session afterward | passed |
| 19 | VALID-only opaque backup catalog | passed |
| 20 | Correction UI non-directional metadata only | passed |
| 21 | Required nonempty correction reason | passed |
| 22 | Detached DTOs usable during quiescence | passed |
| 23 | Internal teardown bypasses user Close Guard | passed |
| 24 | Presentation failure does not retry mutation | passed |
| 25 | Final E2E integrity_check = ok | passed |

## Phase 1 regression

213 passed; original accepted Core tests unchanged.

## Phase 2 regression

293 passed; original accepted Persistence baseline unchanged. Phase 4 migration tests counted separately.

## Phase 3 regression

153 passed; original accepted Application baseline unchanged. Reliability and presentation-capability tests counted separately.

## Phase 4 regression

107 passed, including Restore runtime-state corrections and migration tests.

## Phase 5 regression

106 passed: 102 UI tests plus 4 presentation-capability tests.

## Ruff

`uv run ruff check .` → All checks passed!

`uv run ruff format --check .` → 171 files already formatted.

## Manual DPI

- Windows 125% manual DPI: pending.
- Windows 150% manual DPI: pending.

Only automated structural/offscreen GUI tests were performed.

## SPEC deviations

none

## SPEC concerns

Optional void-only handling of completed records with incorrect pre-run facts has no accepted service and remains unexposed, as required by this phase's scope. No new business path or frozen-contract change was introduced.

## Incomplete work

none for Phase 6 code implementation.

Phase 7 release validation remains separate.

## Known risks

Unpackaged integration is verified, not final release acceptance. Packaging, packaged-app survival, 100k performance smoke and both manual DPI gates remain unperformed.

## Phase 7 work

none

Phase 6 complete. No Phase 7 implementation was started.
