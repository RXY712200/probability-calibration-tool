# Localization Step 4 — Presentation Integration Completion Report

Date: 2026-09-01. Platform: Windows, Python 3.13.14, PySide6/Qt 6.11.2.

Status: **IMPLEMENTATION COMPLETE — READY FOR EXTERNAL STEP 4 REVIEW**

This is an implementation handoff, not acceptance/freeze. Step 5 was not started. No commit, tag, release or version change was made.

## A. Scope summary

Implemented the seven frozen Step 4 areas: presentation ownership/composition, static translation wiring, numbered dynamic templates and domain labels, character/correction identity, semantic errors, language chooser/startup notices, and automated integration/regression coverage.

English remains built-in source/default/fallback. Tests use a synthetic marker translator only. The normal desktop has a far-right Language entry after the existing navigation stretch. Preference changes use the accepted Step 3 save API and apply on a future launch, not by live switching.

## B. Files changed

All links below resolve to exact absolute paths under `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability`. The list is relative to the **incoming accepted local Step 3 baseline**, not merely Git HEAD.

### Modified — 45 files

| Exact file link | Purpose |
|---|---|
| [src/probability_calibration_tool/application/_checks.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/application/_checks.py) | Attach explicit input validation reason codes without changing checks. |
| [src/probability_calibration_tool/application/analysis_builder.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/application/analysis_builder.py) | Map Core validation identities to field + Application code; keep snapshot calculations unchanged. |
| [src/probability_calibration_tool/application/backup_catalog_service.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/application/backup_catalog_service.py) | Classify expired backup selection by code. |
| [src/probability_calibration_tool/application/correction_query_service.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/application/correction_query_service.py) | Read-only CorrectionCandidate now carries character_id. |
| [src/probability_calibration_tool/application/correction_service.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/application/correction_service.py) | Classify the existing verification race as confirmation expired. |
| [src/probability_calibration_tool/application/desktop_session.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/application/desktop_session.py) | Classify session errors and forward structured backup warnings; no language dependency. |
| [src/probability_calibration_tool/application/errors.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/application/errors.py) | Language-independent expected error codes and existing hierarchy metadata. |
| [src/probability_calibration_tool/application/recovery_service.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/application/recovery_service.py) | Distinguish the no-pending recovery reason. |
| [src/probability_calibration_tool/application/reliability_views.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/application/reliability_views.py) | Warnings carry semantic identities/ErrorPresentation, not runtime English. |
| [src/probability_calibration_tool/application/restore_service.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/application/restore_service.py) | Attach the two existing Restore failure meanings; no restore policy changes. |
| [src/probability_calibration_tool/application/startup_service.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/application/startup_service.py) | Emit semantic startup warnings; log technical recovery issues rather than displaying them. |
| [src/probability_calibration_tool/application/workflow.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/application/workflow.py) | Distinguish missing inputs/revision closed from generic current-state rejection. |
| [src/probability_calibration_tool/bootstrap.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/bootstrap.py) | Translate Already Running and pass the already-owned Step 3 context to the real host. |
| [src/probability_calibration_tool/core/errors.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/core/errors.py) | Add a small Qt-free Core validation identity enum. |
| [src/probability_calibration_tool/core/subjective.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/core/subjective.py) | Attach only RAW_PROBABILITY metadata to the existing invalid-input raise. |
| [src/probability_calibration_tool/core/validation.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/core/validation.py) | Attach codes to the four existing odds guards; accepted input sets unchanged. |
| [src/probability_calibration_tool/desktop_host.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/desktop_host.py) | Carry the same context reference; show one low-priority startup notice; retain error severity. |
| [src/probability_calibration_tool/infrastructure/backup.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/infrastructure/backup.py) | Emit semantic warning/error metadata; copy, verification, rotation and triggers unchanged. |
| [src/probability_calibration_tool/infrastructure/error_reporting.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/infrastructure/error_reporting.py) | Add safe error/warning identities while retaining diagnostics, Error ID and traceback logging. |
| [src/probability_calibration_tool/infrastructure/restore_engine.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/infrastructure/restore_engine.py) | Return semantic quarantine-warning identity; replacement/isolation behavior unchanged. |
| [src/probability_calibration_tool/persistence/repositories/rounds.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/persistence/repositories/rounds.py) | Select correction round_id/character_id/completed_at with unchanged filter/order; no display-name join. |
| [src/probability_calibration_tool/ui/analysis_panel.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/analysis_panel.py) | Translate static captions, fixed dynamic templates, semantic domain labels and N/A. |
| [src/probability_calibration_tool/ui/banners.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/banners.py) | Translate visible severity and Error ID presentation; preserve machine severity property. |
| [src/probability_calibration_tool/ui/character_matrix.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/character_matrix.py) | Render by ID; translate before mnemonic escaping; accessible name stays unescaped. |
| [src/probability_calibration_tool/ui/close_guard.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/close_guard.py) | Translate existing close-confirmation text without changing decisions. |
| [src/probability_calibration_tool/ui/correction_page.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/correction_page.py) | Translate controls and render localized character identity; execute by round_id. |
| [src/probability_calibration_tool/ui/desktop_boundary.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/desktop_boundary.py) | Semantic errors/warnings, numbered Error ID template, nonrecursive localization-failure fallback. |
| [src/probability_calibration_tool/ui/desktop_window.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/desktop_window.py) | Far-right Language entry and context-only settings path; no business-session rebuild on save. |
| [src/probability_calibration_tool/ui/formatting.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/formatting.py) | Remove unused enum-guessing format_label; numeric/date formatters unchanged. |
| [src/probability_calibration_tool/ui/main_window.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/main_window.py) | Translate shell and expected errors; remove Recovery display-name relay. |
| [src/probability_calibration_tool/ui/maintenance_page.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/maintenance_page.py) | Render character IDs and fixed confirmation template; same five nondirectional columns. |
| [src/probability_calibration_tool/ui/post_run_panel.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/post_run_panel.py) | Translate existing post-run/void/confirmation controls. |
| [src/probability_calibration_tool/ui/pre_run_panel.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/pre_run_panel.py) | Translate existing inputs and controls; retain input parsing behavior. |
| [src/probability_calibration_tool/ui/presentation.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/presentation.py) | Narrow CharacterOption to character_id only. |
| [src/probability_calibration_tool/ui/recovery_page.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/recovery_page.py) | Translate fixed Recovery facts template and character by command ID. |
| [src/probability_calibration_tool/ui/restore_page.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/restore_page.py) | Translate existing Normal/Emergency Restore controls. |
| [src/probability_calibration_tool/ui/round_page.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/round_page.py) | Translate existing state-selected labels without changing workflow states. |
| [src/probability_calibration_tool/ui/safety_window.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/safety_window.py) | Translate safety title/errors; do not add a language chooser. |
| [src/probability_calibration_tool/ui/startup_pages.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/startup_pages.py) | Delayed safety sources and explicit backup-category/reason display sources. |
| [tests/integration/desktop/test_compound_failure_priority.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/integration/desktop/test_compound_failure_priority.py) | Migrate injected expected errors to semantic codes; retain warning priority and no-retry assertions. |
| [tests/integration/desktop/test_correction_integration.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/integration/desktop/test_correction_integration.py) | Freeze exact new candidate fields; retain immutable/minimal/anti-browsing checks. |
| [tests/integration/infrastructure/test_logging.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/integration/infrastructure/test_logging.py) | Assert new code field while retaining rotation, unique IDs, traceback and secrecy checks. |
| [tests/ui/conftest.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/ui/conftest.py) | Construct the intentionally narrowed CharacterOption. |
| [tests/ui/test_startup_pages.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/ui/test_startup_pages.py) | Use semantic backup category/warning fixtures; preserve explicit selection and nonfatal warning checks. |
| [tests/ui/test_workflow_contract.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/ui/test_workflow_contract.py) | Assert safe generic current-state source, not injected private diagnostic; audit-lock checks retained. |

### Added — 8 files

| Exact file link | Purpose |
|---|---|
| [src/probability_calibration_tool/ui/localization.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/localization.py) | Presentation-only sources, exhaustive mappings and placeholder-safe formatting. |
| [src/probability_calibration_tool/ui/language_dialog.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/language_dialog.py) | Preference chooser and semantic startup-notice presentation using Step 3 APIs. |
| [tests/localization/test_presentation.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/localization/test_presentation.py) | 35 mapping/character/history/template/extraction/error presentation tests. |
| [tests/localization/test_language_ui.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/localization/test_language_ui.py) | 29 chooser/composition/startup-priority tests. |
| [tests/localization/test_presentation_integration.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/localization/test_presentation_integration.py) | 33 translated safety/no-retry/Core classification/deterministic database parity tests. |
| [tests/localization/test_presentation_architecture.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/localization/test_presentation_architecture.py) | 11 permanent ownership/static isolation checks. |
| [outputs/localization_step4_completion_report.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/localization_step4_completion_report.md) | This external-review handoff report. |
| [outputs/localization_step4_validation_commands.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/localization_step4_validation_commands.md) | Exact validation commands, outcomes and audit evidence. |

### Deleted

None. Only the unused `format_label()` function was removed; no source/test file was deleted.

## C. Frozen design compliance

- Exactly 12 extracted app-owned contexts; no generic Common/Buttons/Messages/Dialogs contexts.
- The same process LocalizationContext is carried through bootstrap → DesktopHost → DesktopWindow. Only settings/startup presentation uses it; the nine ordinary panels/widgets do not receive it.
- UI/DesktopHost do not construct/install/remove translators or replace process context. No new localization manager, repository, UoW, language framework, watcher or rescan UI.
- No official zh_CN TS/QM, lrelease distribution pipeline, installer or language-pack packaging. Temporary extraction is outside the repository.
- No live switching, LanguageChange handler, retranslateUi or QLocale.setDefault. Generic widget helpers remain untranslated.
- No database schema, model version, release version (still 1.0.0), seed identity, mathematics or business-decision changes. No localized business database values.
- No message-as-protocol in final UI error/warning presentation: semantic code selects a static source. Diagnostic messages and exception text remain for logs only.
- Input validation field placement remains independent from error meaning; unknown Core failures use the unexpected/invariant boundary.
- Invalid template placeholder multisets fall back only for that message; translation reordering and nonrecursive substitution work.
- Top-level Step 3 localization.py, its eight pre-existing test/helper files and two Step 3 reports match their incoming hashes. Bootstrap retains the accepted Step 3 implementation and adds only Step 4 composition/presentation integration.

## D. Intentional contract migrations

1. CharacterOption: only character_id. Character names come from the explicit 34-entry presentation map, never database display text. Updated tests/ui/conftest.py.
2. CorrectionCandidate/repository read model: exact fields round_id, character_id, completed_at. Removed the display-name-only join; completion filter, order, execution by round_id, detached/frozen DTO and anti-browsing assertions remain. Updated tests/integration/desktop/test_correction_integration.py.
3. Core/Application errors: add Qt-free validation/expected-error codes. Existing guards and exception hierarchy remain; the Application boundary maps Core codes instead of str(exc). Generic transition errors no longer expose internal workflow state; missing inputs and closed revision remain distinct. The correction verification race uses confirmation-expired public meaning.
4. ErrorPresentation: exact message, error_id, code metadata; message is diagnostic, code is UI authority. Updated tests/integration/infrastructure/test_logging.py without removing ID uniqueness, full traceback, secrecy or real log-rotation checks.
5. Operational warnings: ReliabilityResult/BackupResult now carry WarningCode or ErrorPresentation. Recent/Daily backup failures retain their exact English and Error IDs; cache rebuild, over-retention and quarantine warnings use explicit codes. This closes the remaining runtime-English presentation path without changing backup/restore transactions or policy.
6. Existing UI test fixtures: expected-error injections now specify codes, and private diagnostics must not appear. Backup category fixtures use the actual canonical category identity (recent); unavailable status is still selected exclusively through valid=False. Warning tests use semantic metadata and still assert that saved data was not reverted, severity is warning, and private diagnostics do not display.

Existing tests intentionally updated: the six test files listed in section B (including conftest.py). No old test was deleted, skipped or xfailed. No mathematical expected/Golden values changed.

## E. Validation commands

Working directory: `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability`.

```text
uv run pytest
uv run pytest tests/localization -q
uv run pytest tests/localization/test_architecture.py tests/localization/test_presentation_architecture.py tests/ui/test_architecture_formatting.py -q
uv run pytest tests/localization/test_presentation.py tests/localization/test_presentation_integration.py tests/localization/test_language_ui.py -q
uv run pytest tests/localization/test_presentation.py::test_real_extraction_exact_contexts_sources_and_placeholder_signatures -q
uv run ruff check .
uv run ruff format --check .
git diff --check
git status --short
git diff --stat
git rev-parse HEAD
```

The literal temporary-extraction/schema commands and earlier correction cycles are recorded in [localization_step4_validation_commands.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/localization_step4_validation_commands.md).

## F. Test results

| Final validation command/scope | Passed | Failed | Errors | Skipped | Xfailed | Xpassed |
|---|---:|---:|---:|---:|---:|---:|
| uv run pytest | 1286 | 0 | 0 | 0 | 0 | 0 |
| uv run pytest tests/localization -q | 273 | 0 | 0 | 0 | 0 | 0 |
| Architecture/static command above | 45 | 0 | 0 | 0 | 0 | 0 |
| Presentation/integration/language command above | 97 | 0 | 0 | 0 | 0 | 0 |
| Dedicated real extraction test | 1 | 0 | 0 | 0 | 0 | 0 |

Final full suite: **1286 passed in 139.39s (0:02:19)**, including the existing 100k performance/release tests. The four new test files add 108 cases over the recorded 1178-case incoming Step 3 baseline. Counts above overlap and must not be added.

Ruff lint: exit 0, All checks passed. Ruff formatting after report creation: exit 0, 212 files already formatted. git diff --check: exit 0, no output.

## G. Extraction audit

Actual installed pyside6-lupdate ran with `-extensions py` against production src into:

`C:/Users/rxy71/AppData/Local/Temp/pct-step4-audit-831847d9-646c-4b0a-9e8b-854c82201ca0/step4-extraction.ts`

**230 source texts; exactly these 12 contexts:**

| Context | Sources |
|---|---:|
| AppShell | 9 |
| Round | 29 |
| Analysis | 25 |
| Maintenance | 13 |
| Correction | 11 |
| Restore | 17 |
| Recovery | 7 |
| StartupSafety | 6 |
| Errors | 37 |
| Characters | 36 |
| DomainLabels | 19 |
| Localization | 21 |

The dedicated extraction test verifies required dynamic sources/placeholder signatures, the 34 character sources, expected errors, domain labels and Language. Static declarations are literal Qt translation calls or QT_TRANSLATE_NOOP; lookups occur at runtime.

No TS/QM was added to src or packaging. The absence of a Step 5 catalog is a **this-stage scope audit**, not a permanent architecture rule blocking legitimate future Step 5 work.

## H. Database/schema audit

Actual production initialize_v1 schema inspected in a fresh in-memory database:

- PRAGMA user_version: **1**
- Exact table set: **character_stats, characters, history_regimes, meta, round_analysis_snapshots, rounds**

Additionally, paired real-file integration scenarios clone the same seeded database, use identical Application clock/IDs, freeze the independent stats/meta audit clock in the test only, and compare every logical row/column of all six tables. No SQLite file hash is used as the primary semantic parity oracle.

Both runs execute Calculate → Modify/Recalculate → close/start/Recovery → Complete → Correction → new Regime → preference save → Restore. Assertions compare states, original/replacement IDs, statuses, revision counts, result/include, snapshots, exposure/compromise flags, regime/cache facts, supersedes links and backup trigger calls. Recovery does not recalculate; Restore rebuilds the business session while retaining the same localization context/settings. Preference saves leave all six tables and backup trigger counts unchanged. Backups contain only database data, not settings.ini or language catalogs.

## I. English regression

All existing static UI sentences remain canonical English; an AST literal inventory against HEAD found only dynamic f-string fragments replaced by fixed templates, not missing static sentences. Numeric/date/EV/S/interval/posterior formatting is unchanged.

Intentional public-text differences under the frozen semantic/safety contract:

- Internal `Operation is not allowed in <workflow token>.` becomes **Operation is not allowed in the current state.**
- Correction source-change diagnostic becomes **Confirmation expired. Confirm the operation again.**
- Unmapped diagnostic error text becomes **The operation could not be completed.** plus Error ID for unexpected failures.
- Startup diagnostics (**Application directories could not be prepared.**, **Database integrity could not be established.**, **Startup could not safely continue.**, **Committed migration requires emergency recovery.**, **Desktop startup could not safely continue.**) remain in logs; the UI shows the fixed safe generic error with its ID alongside the unchanged semantic safety page.
- Multiple-pending startup no longer forwards technical invariant issue strings as UI warnings; it shows the fixed public recovery-attention meaning, and the original issues are logged.
- New Step 4 Language chooser/preferred/current/availability/save/restart/fallback notices are new authorized UI. English/简体中文 self-names are stable.

Recent/Daily backup failure, rotation and quarantine warning English remains unchanged, including Error ID meaning. The Restore meanings remain distinct. `Double positive window` (label, no hyphen), its independently hyphenated warning sentence, N/A, 34 character names and untranslated product name are preserved. Backup metadata keeps its actual lower-case canonical English sources; only the legacy test fixture was aligned to those identities.

No additional opportunistic English-copy changes were made.

## J. Safety regression

Green in the final suite and focused translated-mode coverage:

- Anti-anchoring and history eligibility/visibility; HIDDEN/NO_HISTORY/INSUFFICIENT clear stale values/captions, not only visibility. Maintenance remains five nondirectional columns.
- Original no-retry assertions for committed Calculate, completed Save, Maintenance/Correction refresh and warning presentation failures execute in both presentations.
- A localization helper failing after Calculate cannot re-execute it. Failure inside error localization itself falls back nonrecursively to safe English with the same Error ID; full traceback/private detail remains in logs.
- Semantic field placement, unexpected/invariant safety, Error IDs, logging, Recovery identity, Correction anti-browsing/supersedes/snapshot immutability, Restore and backup invariants remain green.
- Chooser matrix, Cancel/Esc/X zero-save/zero-preflight, exactly-once Confirm, healthy no-op, explicit invalid/read-error repair, save failure, pack demotion/no re-promotion and no hot switch are tested.
- Missing-pack notice uses current English; Qt degradation preserves effective zh_CN; startup notices never supersede safety/recovery/error outcomes or add an Already Running popup. Error + operational-warning composition keeps error severity.

## K. Git diff/scope

HEAD before/after: `00bd24b9fdc509809962ace4412b1e233b7c6598` — **unchanged**. No reset, checkout, restore-to-HEAD, commit or tag operation was performed.

Incoming dirty state (preserved):

```text
 M src/probability_calibration_tool/bootstrap.py
?? outputs/localization_step3_completion_report.md
?? outputs/localization_step3_validation_commands.md
?? src/probability_calibration_tool/localization.py
?? tests/localization/
```

Final `git status --short`:

```text
 M src/probability_calibration_tool/application/_checks.py
 M src/probability_calibration_tool/application/analysis_builder.py
 M src/probability_calibration_tool/application/backup_catalog_service.py
 M src/probability_calibration_tool/application/correction_query_service.py
 M src/probability_calibration_tool/application/correction_service.py
 M src/probability_calibration_tool/application/desktop_session.py
 M src/probability_calibration_tool/application/errors.py
 M src/probability_calibration_tool/application/recovery_service.py
 M src/probability_calibration_tool/application/reliability_views.py
 M src/probability_calibration_tool/application/restore_service.py
 M src/probability_calibration_tool/application/startup_service.py
 M src/probability_calibration_tool/application/workflow.py
 M src/probability_calibration_tool/bootstrap.py
 M src/probability_calibration_tool/core/errors.py
 M src/probability_calibration_tool/core/subjective.py
 M src/probability_calibration_tool/core/validation.py
 M src/probability_calibration_tool/desktop_host.py
 M src/probability_calibration_tool/infrastructure/backup.py
 M src/probability_calibration_tool/infrastructure/error_reporting.py
 M src/probability_calibration_tool/infrastructure/restore_engine.py
 M src/probability_calibration_tool/persistence/repositories/rounds.py
 M src/probability_calibration_tool/ui/analysis_panel.py
 M src/probability_calibration_tool/ui/banners.py
 M src/probability_calibration_tool/ui/character_matrix.py
 M src/probability_calibration_tool/ui/close_guard.py
 M src/probability_calibration_tool/ui/correction_page.py
 M src/probability_calibration_tool/ui/desktop_boundary.py
 M src/probability_calibration_tool/ui/desktop_window.py
 M src/probability_calibration_tool/ui/formatting.py
 M src/probability_calibration_tool/ui/main_window.py
 M src/probability_calibration_tool/ui/maintenance_page.py
 M src/probability_calibration_tool/ui/post_run_panel.py
 M src/probability_calibration_tool/ui/pre_run_panel.py
 M src/probability_calibration_tool/ui/presentation.py
 M src/probability_calibration_tool/ui/recovery_page.py
 M src/probability_calibration_tool/ui/restore_page.py
 M src/probability_calibration_tool/ui/round_page.py
 M src/probability_calibration_tool/ui/safety_window.py
 M src/probability_calibration_tool/ui/startup_pages.py
 M tests/integration/desktop/test_compound_failure_priority.py
 M tests/integration/desktop/test_correction_integration.py
 M tests/integration/infrastructure/test_logging.py
 M tests/ui/conftest.py
 M tests/ui/test_startup_pages.py
 M tests/ui/test_workflow_contract.py
?? outputs/localization_step3_completion_report.md
?? outputs/localization_step3_validation_commands.md
?? outputs/localization_step4_completion_report.md
?? outputs/localization_step4_validation_commands.md
?? src/probability_calibration_tool/localization.py
?? src/probability_calibration_tool/ui/language_dialog.py
?? src/probability_calibration_tool/ui/localization.py
?? tests/localization/
```

Final tracked `git diff --stat`: **45 files changed, 681 insertions(+), 246 deletions(-)**. This Git statistic includes the pre-existing bootstrap Step 3 diff and omits untracked files. The incoming SHA-256 comparison independently identifies **45 modified, 8 added, 0 removed** Step 4 files (section B), rather than incorrectly attributing old untracked Step 3 files to this stage.

Protected baseline hash checks: all 4 Domain files; all 4 unit/Core test files; schema.py; seed.py; core/model_specs.py; SPEC_1.0.md; pyproject.toml; uv.lock; both packaging files; all 5 tools files; top-level localization.py; 8 original localization tests/helpers; both Step 3 reports — unchanged.

High-risk changes are explicitly limited to error metadata in core/subjective.py and core/validation.py; semantic warnings/codes in backup.py, restore_engine.py, startup_service.py and restore_service.py; and correction identifier SELECT/read-model fields. No mathematical expression, persistence DDL, migration, snapshot mathematics, backup rotation/copy policy, Restore replacement policy, SPEC, release tool or packaging change.

Representative frozen hashes (SHA-256):

| File | Incoming = final |
|---|---|
| src/probability_calibration_tool/localization.py | A9E5716706FEFC25CF61093432F20DBF94A5F5A6EB90623B169673F428C00761 |
| SPEC_1.0.md | AEE4EB200BEA8EC1A652A65A2076645613E6057C37D6280A9A0787CC5B040FC4 |
| pyproject.toml | D4CEB0A37136942917DE80AA8940F9F60F4E6DFC16E276060A2C5F7C696654E6 |
| uv.lock | CBA8022E7E8A309A6436ED0667D4D78D4907EC82030676E7183211CF2C072A58 |

SPEC deviations: none. Step 5 implementation: none. External Step 4 acceptance remains outstanding.

**IMPLEMENTATION COMPLETE — READY FOR EXTERNAL STEP 4 REVIEW**
