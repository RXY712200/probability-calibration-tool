# Phase 2 Final Corrective Report

## Files modified

- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\database.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\schema.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\unit_of_work.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\meta.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\regimes.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\rounds.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\snapshots.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\stats.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_repositories.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_round_constraints.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_unit_of_work.py`

## Files created

- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_mutation_primitives.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\phase2_final_corrective_report.md`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\phase2_final_corrective_commands.md`

## UnitOfWork fix

Selected contract B:
- Entering a UnitOfWork explicitly starts a transaction.
- commit() commits the current transaction and explicitly begins a new, uncommitted transaction.
- Further writes after commit() are allowed but require another explicit commit to persist.
- Exiting the scope always rolls back the currently uncommitted transaction, including after an earlier commit. Previously committed work remains committed.
- Exceptions before commit roll back current changes; exceptions after a previous commit roll back only the later transaction.
- Every mutating repository method checks for an active transaction and explicitly begins one if absent. Standalone repository callers must explicitly commit or roll back their connection; closing without committing discards changes.
- Repositories never call commit() or rollback(). Connection-factory PRAGMAs remain unchanged.

Independent observer tests cover all nine mutation paths both through UnitOfWork after commit and through directly constructed repositories.

## Voided-state fix

For status='voided':
- voided_at must be non-NULL;
- result, include_character_history and completed_at must be either all NULL or all non-NULL.

All six mixed NULL/non-NULL combinations are rejected. Both legitimate forms remain accepted, including result=0/include=0 in completed-derived voids and either nullable or explicit void_reason. No new void_reason policy was added.

The v1 CREATE TABLE definition was updated. SCHEMA_VERSION and PRAGMA user_version remain 1. SPEC_1.0.md was not edited.

## Repository primitives

- RoundRepository.update(record: RoundRecord) -> None
- HistoryRegimeRepository.update(record: HistoryRegimeRecord) -> None
- CharacterStatsRepository.insert(record: CharacterStatsRecord) -> None

Update operations use the existing identity in their WHERE clause and do not modify that identity. SQLite enforces structural validity; these primitives make no state-transition or workflow decisions and do not commit independently.

## Regression tests added

- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_mutation_primitives.py`: 47 new cases. New primitive round trips, identity/unrelated-row preservation, SQLite rejection, and commit/rollback visibility for nine write paths used directly or after a UoW commit.
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_round_constraints.py`: 10 new cases. Six hybrid voided combinations rejected, four combinations of legitimate void forms and nullable/non-NULL reason accepted.
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_unit_of_work.py`: 3 new cases. Post-commit write invisibility/rollback, second explicit commit, and exception after prior commit.
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_repositories.py`: existing assertions unchanged; added explicit commit for preparation of the snapshot-update visibility test because repository inserts no longer autocommit.

Existing round-plus-snapshot joint commit and failure/exception/no-commit rollback tests all still pass. No test was removed, weakened, skipped, or xfailed.

## Persistence test inventory

| File | Collected test items |
|---|---:|
| tests/integration/persistence/test_character_constraints.py | 8 |
| tests/integration/persistence/test_initialization.py | 7 |
| tests/integration/persistence/test_mutation_primitives.py | 47 |
| tests/integration/persistence/test_persistence.py | 7 |
| tests/integration/persistence/test_regime_constraints.py | 8 |
| tests/integration/persistence/test_repositories.py | 30 |
| tests/integration/persistence/test_round_constraints.py | 47 |
| tests/integration/persistence/test_snapshot_constraints.py | 117 |
| tests/integration/persistence/test_stats_constraints.py | 11 |
| tests/integration/persistence/test_stats_rebuild.py | 4 |
| tests/integration/persistence/test_unit_of_work.py | 7 |
| **Total** | **293** |

Command: `uv run pytest tests/integration/persistence --collect-only -q`

Literal final summary: `293 tests collected in 0.03s`

60 regression items were added to the previous total of 233.

## Tests

- Exact full command: `uv run pytest`
- Passed: **506**
- Failed: **0**
- Skipped: **0**
- xfailed/xpassed: **0/0**

All tests use temporary file databases. No production application LocalAppData was used.

## Ruff

- `uv run ruff check .`: `All checks passed!`
- `uv run ruff format --check .`: `47 files already formatted`

## Phase 1 regression

All 213 Phase 1 tests pass. Hash comparison verifies Phase 1 math files, Golden tests, SPEC, pyproject.toml, uv.lock and .gitignore are unchanged.

SPEC SHA-256: `AEE4EB200BEA8EC1A652A65A2076645613E6057C37D6280A9A0787CC5B040FC4`.

## Source hygiene

Deleted 44 generated .pyc files and 7 empty __pycache__ directories, only under src/ and tests/. Nonrecursive literal-path removal followed target/contents validation. Final scan reports zero matching artifacts. No source file was removed. Bytecode is regenerable.

.gitignore retains .venv/, __pycache__/ and *.py[cod].

## SPEC deviations

none

## SPEC concerns

none

## Incomplete work

none

## Known risks

Existing prerelease v1 database files do not automatically receive the new CHECK constraint because this pass updates the v1 initialization definition without a version bump or migration, as requested. Such development databases must be recreated to receive the new schema; no existing database was migrated, rebuilt, or deleted.

## Phase 3 work

none

## Execution evidence

All literal commands and final results are saved in:
`C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\phase2_final_corrective_commands.md`

Phase 2 final corrective pass complete. No Phase 3 implementation was started.

