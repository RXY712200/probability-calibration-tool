# Phase 2 Mandatory Test Completion Report

## Test files created

- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\__init__.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\conftest.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\helpers.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_character_constraints.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_initialization.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_regime_constraints.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_repositories.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_round_constraints.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_snapshot_constraints.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_stats_constraints.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_stats_rebuild.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_unit_of_work.py`

## Test files modified

none. The existing test_persistence.py and all Phase 1 tests are unchanged.

## Production files modified

- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\domain\records.py`
- `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\snapshots.py`

New tests exposed loss of snapshot Enum types during retrieval (13 initially failing regression cases). Restored EvState, HistoryModelStatus, OddsCombinationStatus and ModelRelation types in the snapshot record and repository read conversion. No SQL schema, frozen math, model constants, Golden expectations or SPEC changes.

## Commands executed

All literal commands, including repeated runs, read-only inspections and hash checks:
`outputs/phase2_mandatory_command_log.md`

Required final commands:
```text
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pytest tests/integration/persistence --collect-only -q
```

## Persistence test inventory

| File | Collected test items |
|---|---:|
| tests/integration/persistence/test_character_constraints.py | 8 |
| tests/integration/persistence/test_initialization.py | 7 |
| tests/integration/persistence/test_persistence.py | 7 |
| tests/integration/persistence/test_regime_constraints.py | 8 |
| tests/integration/persistence/test_repositories.py | 30 |
| tests/integration/persistence/test_round_constraints.py | 37 |
| tests/integration/persistence/test_snapshot_constraints.py | 117 |
| tests/integration/persistence/test_stats_constraints.py | 11 |
| tests/integration/persistence/test_stats_rebuild.py | 4 |
| tests/integration/persistence/test_unit_of_work.py | 4 |
| **Total** | **233** |

Literal collection summary: `233 tests collected in 0.10s`.
The three support files (__init__.py, conftest.py, helpers.py) collect no test items.
Persistence items increased from 7 to 233, an increase of 226.

## Constraint coverage

- Characters: complete. Both ID/range bounds, duplicate code/pair slot, invalid boolean flags; 34 independent frozen identities compared field by field.
- History regimes: complete. Invalid number, duplicates, active uniqueness, timestamps/booleans, parent FK and child composite FK protection; legal active/closed regimes.
- Rounds: complete. All requested invalid fields/states, exposure consistency, two odds sides, uniqueness and supersede branching; legal pending/completed/both voided shapes and supersede chain.
- Snapshots: complete. 117 tests covering legal no_history/insufficient/valid states, enum/version/probability/EV ordering, null/required fields, both posterior sides, count invariants and foreign keys.
- Character stats: complete. Negative/arithmetic counts, last-round/null consistency, version/composite FK/round FK, legal zero and positive rows.

## Repository coverage

- CharacterRepository: list_all(), get(); all returned records and bool fields are typed.
- HistoryRegimeRepository: get(), get_active(), insert(); active/closed records, nullable reason/end and UTC time.
- RoundRepository: insert(), get(), eligible_history(); typed values/Enums/nullable fields and all four legal shapes.
- SnapshotRepository: insert(), get(), update(); every field verified for all three statuses, all nine status combinations through the update primitive, unrelated row preservation and rejected-update preservation.
- CharacterStatsRepository: get(), rebuild_stats(); zero and positive typed cache records, complete source-truth rebuild.
- MetaRepository: get(), set(); insert/update, quoted Unicode strings and UTC timestamps.
- Six mutation paths are verified with an independent observer before and after explicit UoW commit: round insert, snapshot insert, snapshot update, regime insert, stats rebuild and meta set.

## UoW atomicity

All four release-blocking tests passed:
- Invalid snapshot insert after pending-round insert: both row counts zero on a fresh connection.
- Valid pending-round plus snapshot with explicit commit: both visible on a fresh connection.
- Exit without commit after both inserts: neither remains.
- Injected exception after both inserts: neither remains.

No application workflow was added.

## Eligible history

Complete. Twenty eligible records plus individually constructed other-character, other-regime, pending, voided and completed-excluded distractors. Exact returned records and order asserted; no Jeffreys calculation in persistence.

## Stats rebuild

Complete. Corrupted cache rebuilt from 20 eligible rounds to 16 wins/4 losses/current STATS_VERSION, ignoring all five distractors. Version mismatch is observable via the typed get() result and resolved by rebuild. Empty snapshot table proves snapshots are not required. Correct latest round asserted using prediction time despite reverse ID ordering; tie-break tested only for stable order.

## Initialization/versioning

Complete. Six tables, required indexes, three fresh connection PRAGMAs, user_version=1, independent exact 34 seeds, regimes/stats, two reopen passes preserving every row, failure during seed and after seed with full schema/seed/version rollback, successful retry, and schema 999 rejection preserving payload and the entire database file bytes.

All persistence tests use temporary file databases. Real application LocalAppData data was not accessed.

## Tests

- Command: `uv run pytest`
- Passed: **446**
- Failed: **0**
- Skipped: **0**
- xfailed/xpassed: **0/0**
- Persistence items: **233**

No existing tests were deleted, weakened, skipped or xfailed.

## Ruff

- `uv run ruff check .`: `All checks passed!`
- `uv run ruff format --check .`: `44 files already formatted`

## Phase 1 regression

All 213 Phase 1 tests pass. Phase 1 source and test hashes are unchanged.
SPEC SHA-256 remains `AEE4EB200BEA8EC1A652A65A2076645613E6057C37D6280A9A0787CC5B040FC4`.
pyproject.toml and uv.lock are unchanged.

## SPEC deviations

none

## SPEC concerns

none

## Incomplete work

none

## Phase 3 work

none

Phase 2 mandatory persistence coverage complete. No Phase 3 implementation was started.

