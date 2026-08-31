# Phase 3 Completion Report

## Files created

Exact paths (15 application modules, 10 test/support files, 2 reports):

```text
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\__init__.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\_checks.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\_view_builder.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\analysis_builder.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\commands.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\correction_service.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\enums.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\errors.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\maintenance_service.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\ports.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\recovery_service.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\regime_service.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\round_service.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\views.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\workflow.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\__init__.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\conftest.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\helpers.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\test_calculate.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\test_correction.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\test_lifecycle.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\test_recalculate.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\test_recovery.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\test_regime_maintenance.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\test_workflow.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\phase3_completion_report.md
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\phase3_validation_commands.md
```

## Files modified

```text
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\rounds.py
```

No existing source/test files were removed. Test-generated caches remain ignored: 69 .pyc files in 9 __pycache__ directories. An optional cleanup command was rejected by environment policy before execution; no deletion was performed.

## Persistence additions

- `RoundRepository.list_pending()`: a read-only, typed query returning every pending round. Needed for global pending guards and recovery cardinality checks; no implicit selection and no repository commit.
- No other persistence method was added or modified.

Schema v1 unchanged.

SHA-256 equality verified against the pre-change baseline for all existing Core, Domain, Phase 1/2 tests, schema, migrations, UoW, configuration and lock files. Only the existing rounds repository changed.
- SPEC: `AEE4EB200BEA8EC1A652A65A2076645613E6057C37D6280A9A0787CC5B040FC4`
- schema.py: `FB457C818780A94EF62AB53A3ED02FC0779FF1C4B0001734FBD67D56486F9315`

## Application architecture

| Module | Responsibility |
|---|---|
| __init__.py | Public use-case exports; no persistence record exports |
| errors.py | Semantic business/input/invariant errors; unexpected persistence failures propagate |
| enums.py | Workflow, historical display and recovery states |
| commands.py | Immutable CalculateCommand |
| views.py | Use-case-specific safe DTOs; separate nonnumeric/visible historical variants |
| ports.py | Clock, IdGenerator, SafetyBackupPort; minimal UTC/UUID adapters only |
| analysis_builder.py | Compose accepted Core functions and assemble full internal snapshot |
| _checks.py | Private reusable business/input/time guards |
| _view_builder.py | Private committed-record projection; no recalculation; exposure authorization |
| round_service.py | Calculate, Recalculate, Complete, pending Void |
| regime_service.py | Atomic explicit regime switch |
| recovery_service.py | Pending cardinality inspection and same-record continuation |
| maintenance_service.py | Nondirectional maintenance DTOs |
| correction_service.py | Verified-backup-gated post-run correction |
| workflow.py | In-memory state machine, edits, choices and failure transitions |

The two private helper modules isolate shared guards and output projection without introducing a framework. Application contains no SQL, database schema edits, GUI, filesystem backup engine or duplicated mathematical formulas.

## Workflow states

States: DRAFT, CALCULATING, PENDING_LOCKED, PENDING_EDIT, CONFIRM_SAVE, COMPLETING, RECOVERY, RECOVERY_ERROR, COMPLETED_NOTICE.

Implemented transitions:
- DRAFT -> CALCULATING -> PENDING_LOCKED; failure -> DRAFT.
- PENDING_LOCKED -> Modify -> PENDING_EDIT -> CALCULATING -> PENDING_LOCKED; failure -> PENDING_EDIT.
- Result/include choices remain memory-only. Both chosen -> CONFIRM_SAVE.
- CONFIRM_SAVE -> Back -> PENDING_LOCKED.
- CONFIRM_SAVE -> COMPLETING -> COMPLETED_NOTICE; failure -> CONFIRM_SAVE.
- COMPLETED_NOTICE -> dismiss -> empty DRAFT.
- Confirmed pending Void -> empty DRAFT.
- Inspection: 0 pending stays DRAFT; 1 -> RECOVERY -> Continue -> PENDING_LOCKED; >1 -> RECOVERY_ERROR.

The transition matrix tests every disallowed origin for all 11 workflow operations, plus successful, transient and failed paths. Persistent RoundStatus remains pending/completed/voided only.

## Calculate

Core validates/parses the input and creates the subjective estimate. A single consistent UoW then checks global pending state, obtains the active regime, reads eligible source rounds, calculates historical/odds/relation models, builds the full snapshot, generates the round ID and determines exposure.

Pending round, snapshot and exposure are inserted in that same transaction. The official safe view is constructed only after commit and UoW exit. Transaction failures return no official view and leave no partial round/snapshot.

The transaction includes the history read to keep it consistent with the prediction write. Stats cache is not used as prediction source. Chronology uses the existing calculated_at ordering; UUID is not treated as prediction time.

## Safe historical output

| Display state | Public historical payload |
|---|---|
| HIDDEN | State only, regardless of stored historical readiness |
| NO_HISTORY | Nonnumeric state only |
| INSUFFICIENT | Nonnumeric state only; internal Jeffreys estimate/interval remains persisted |
| VISIBLE | Independent historical counts, probability/interval, EV, posterior threshold and model relations, authorized by durable exposure |

Nonnumeric DTOs have exactly one field: state. Historical model relations are also withheld outside VISIBLE. Subjective results remain independent; there is no subjective/history fusion. Public services never return the complete persistence snapshot.

## Exposure

Reference=true and VALID causes exposure to be persisted in the prediction transaction before numerical view construction. Fresh-connection spies verify durable round/snapshot/exposure at the instant projection starts. No-history/insufficient messages do not count as exposure.

Once set, history_exposed remains true and the first history_exposed_at timestamp survives odds changes, reference off/on and historical status changes.

## Recalculate

Only pending may be recalculated. Same round ID and snapshot identity; created_at unchanged; revision_count increments; calculated_at and last_updated_at advance using the injected clock. A changed character uses that character's current active regime.

Round, snapshot and audit updates commit together. Failure preserves every old persisted field and the old snapshot. Editing before Recalculate is memory-only, and crash recovery restores the previous committed inputs/snapshot.

## Independence compromise

The test is based on the persisted OLD history_exposed flag:
`old_compromised OR (old_exposed AND (character actually changed OR p_h_raw actually changed))`.

It is irreversible. Odds-only and reference-only changes do not introduce compromise. If the same Recalculate changes p_h_raw and creates the FIRST exposure, old_exposed=false, so compromise remains false.

## Complete / Void

Complete validates explicit booleans and requires pending. Result, inclusion, completed_at, last_updated_at and completed status update in one UoW; included rounds rebuild affected stats inside it. Excluded rounds retain result/snapshot/audit but do not rebuild stats or enter future eligible history.

Pending Void sets voided status/time/reason while post-run facts remain NULL; snapshot remains untouched. Terminal rounds cannot be recalculated, completed again or returned to pending. No physical deletion.

## Regime

Any pending anywhere blocks switching. One transaction closes the old regime, preserves its original reason, creates the next numbered UUID regime with the new reason, and inserts zero stats. Failures restore the old active regime and leave no partial regime/cache row. Old history remains stored; the new regime starts at no history.

Maintenance exposes only character identity/name, active regime number/start/reason and included count, verified structurally and through serialization.

## Recovery

0 pending -> no recovery; 1 -> recoverable; >1 -> semantic MultiplePendingRoundsError and RECOVERY_ERROR. Multiple-pending tests use a fake query result, without weakening schema constraints.

Continue uses the same persisted round/snapshot and returns the same safe locked analysis without Core calls, new IDs, writes or new timestamps. Reference=true + valid + exposed=false fails closed with ApplicationInvariantError. Missing snapshots also fail closed.

## Historical correction

- A read-only preflight UoW closes before invoking SafetyBackupPort with `pre_history_correction`.
- The port must return only after successful verification and raise on failure. Failure opens no correction write transaction and generates no replacement ID.
- After verification, generate correction time/ID; recheck pending state and source identity in the correction UoW.
- A becomes voided with reason/time while retaining its original result/include/completed_at and prediction/audit facts.
- B becomes completed, supersedes A, copies all pre-run/audit facts, and receives only corrected result/include facts.
- B.calculated_at = A.calculated_at; B.created_at/last_updated_at/completed_at = correction time.
- B snapshot is an exact copy of A snapshot except round_id. No Core calculation or snapshot time/count rewrite.
- Stats rebuild in the same transaction, so A is excluded and B is counted exactly once when included.
- A -> B -> C is supported; attempts to branch from an already voided A/B fail semantically before backup.
- The public correction signature cannot accept character, probability, odds, reference, regime or snapshot changes.

## Tests

`uv run pytest`: **640 passed in 16.71s**, exit 0.

- passed: 640
- failed: 0
- skipped: 0
- xfailed: 0
- xpassed: 0

`uv run pytest tests/integration/application --collect-only -q`: **134 tests collected**, exit 0. All 134 passed in the full suite. No separate application unit-test folder was created.

| Phase 3 test module | Items |
|---|---:|
| test_calculate.py | 27 |
| test_correction.py | 32 |
| test_lifecycle.py | 19 |
| test_recalculate.py | 14 |
| test_recovery.py | 11 |
| test_regime_maintenance.py | 12 |
| test_workflow.py | 19 |
| Total | 134 |

All 33 required test groups are covered by these modules. No prior test or Golden expected value was changed, removed, skipped or xfailed.

## Critical Golden Business Tests

| Case | Result | Verified behavior |
|---|---|---|
| A | PASS | Reference=false + valid: complete internal history, hidden public history, no exposure |
| B | PASS | Reference=true + insufficient: internal Jeffreys values, nonnumeric output, no exposure |
| C | PASS | Valid/reference numerical output is constructed only after exposure commit |
| D | PASS | Odds-only revision does not introduce compromise; already-true flag stays true |
| E | PASS | Exposed p_h_raw change irreversibly compromises independence |
| F | PASS | Exposed character change irreversibly compromises independence |
| G | PASS | Same revision changes probability and first exposes history: exposed=true, compromised=false |
| H | PASS | Reference off/on retains first timestamp T1 |

Round21 leakage: saved history remains 19 wins / 1 loss / n=20 after its included completion and later corrections; live history changes independently. Correcting Round21 itself copies its original n=20 snapshot.

## Fault injection

| Operation | Result | Injection points |
|---|---|---|
| Calculate rollback | PASS | After round insert/before snapshot; before commit; no official view |
| Recalculate rollback | PASS | After round+snapshot mutations; before commit; both old exposure states |
| Complete rollback | PASS | Before/after stats rebuild; before commit |
| Regime switch rollback | PASS | After old closure/before new regime; before zero stats; before commit |
| Correction rollback | PASS | After A; after B snapshot; after stats; before commit |

All rollback assertions inspect a fresh connection and compare complete logical database content. Pending Void commit failure and backup failure are also covered.

## Phase 1 regression

`uv run pytest tests/unit/core -q`: **213 passed**, exit 0. Also passed in the full suite; original Core and tests unchanged.

## Phase 2 regression

`uv run pytest tests/integration/persistence -q`: **293 passed**, exit 0. Also passed in the full suite; original persistence tests unchanged.

## Ruff

- `uv run ruff check .`: **All checks passed!**, exit 0.
- `uv run ruff format --check .`: **74 files already formatted**, exit 0.

An intermediate Ruff DTZ001 finding concerned the deliberately naive clock rejection test; it was resolved with a local documented suppression for that intentional invalid input. Production timestamp rules were not relaxed.

## SPEC deviations

none

## SPEC concerns

none

## Incomplete work

none

## Known risks

Production safety verification depends on a future correct SafetyBackupPort adapter. Phase 3 verifies this contract using fakes and does not provide or claim an actual backup/restore capability. Ignored Python caches remain because optional cleanup was blocked by the environment.

## Phase 4 work

none

Phase 3 complete. No Phase 4 implementation was started.
