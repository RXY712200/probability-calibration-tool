# Localization Step 3 Completion Report

## Result

PASS — Localization Infrastructure only. All gates G1–G20 pass.

The pre-localization baseline was **1013 passed**. After the third-party review correction, the latest full suite is **1178 passed**, including **165 localization tests**, with **0 failed, 0 errors, 0 skipped, 0 xfailed, and 0 xpassed**. The original implementation had 1168 passing tests; this correction adds ten AST-only contract checks. The original pre-localization tests remain unchanged. This pass changes no production code and adds no feature.

Repository: `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability`

The authorized request was read from `C:\Users\rxy71\Desktop\新建 文本文档 (2).txt`.

## Third-party review correction — test contract only

The review correctly identified that permanently banning UI translation imports and `translate`/`tr` calls would block the frozen Step 4 presentation design. That over-constraint was removed; this is a test-contract correction, not a new feature or Step 4 implementation.

Exactly these files changed during the corrective pass:

```text
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\localization\test_architecture.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\localization_step3_completion_report.md
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\localization_step3_validation_commands.md
```

No files were created or removed during this correction. Production code did not change. All 86 production-file SHA-256 hashes match the start-of-correction snapshot, including `localization.py`, `bootstrap.py`, DesktopHost, UI, and all business layers. SPEC, schema, dependencies, packaging, version, and model/business logic were unchanged. Existing uncommitted Step 3 production changes were preserved, not rewritten.

The business-layer AST check is unchanged: Core/Domain/Application/Persistence remain localization-agnostic. Their localization/Qt imports and translation-call prohibitions were not weakened; translated/display text does not become a business-decision input.

The revised UI/DesktopHost check permits translation APIs, presentation-localization imports/helpers, and read-only dependency references to an injected context. It rejects QTranslator construction, installTranslator/removeTranslator, and new LocalizationContext construction or initialization from presentation code, including ordinary qualified and imported-alias calls. Translator/process-context lifecycle remains outside UI/DesktopHost; merely referencing localization state is not forbidden.

Ten AST-only contract regression cases were added: one positive example containing translation APIs/helpers and an injected read-only context, and nine negative construction/activation/context-replacement examples. They only parse source strings; no production presentation helper, translated UI, or Language dialog was created.

G20 is evidenced by the Step 3 diff/hash audit: UI and business production files are unchanged, no formal production TS/QM or Language dialog exists, and no UI translation implementation was added. G20 is not enforced by a permanent prohibition on legitimate future UI translation.

**Step 4 and Step 5 were NOT started during this correction.** Exact rerun commands/results are in the validation record's third-party review section.

Correction validation: architecture **28 passed in 2.27s**; localization **165 passed in 11.36s**; full suite **1178 passed in 124.33s (0:02:04)**. Ruff check, Ruff format --check (204 files), and git diff --check all exited 0. All correction test runs had zero failed/errors/skipped/xfailed/xpassed. Final hash comparison across 225 snapshotted files identifies only the architecture test and these two reports as changed; every production-file hash is unchanged.

## Files modified in the original Step 3 implementation

```text
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\bootstrap.py
```

Only localization initialization, its narrow fail-open boundary, and process-level context lifetime were added. The tracked diff is 15 insertions and 2 deletions. Existing runtime scope, host disposal, startup routing, and ALREADY_RUNNING notification-only behavior remain intact.

## Files created in the original Step 3 implementation

```text
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\localization.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\localization\__init__.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\localization\conftest.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\localization\helpers.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\localization\test_architecture.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\localization\test_bootstrap.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\localization\test_catalog.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\localization\test_preferences.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\localization\test_runtime.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\localization_step3_completion_report.md
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\localization_step3_validation_commands.md
```

## Files removed

None from the project. Test-controlled deletion of a temporary QM exercises Confirm-time disappearance; it does not delete any source or production language pack.

## Intentionally unchanged

- Core, Domain, Application, Persistence, UI, `desktop_host.py`, and existing infrastructure.
- Every original pre-localization test, including existing bootstrap/startup tests and Golden expectations. The corrective pass changes only the localization architecture test described above.
- `SPEC_1.0.md`, database schema, application version, and existing release artifacts.
- `pyproject.toml` and `uv.lock`: unchanged. No dependency installation or upgrade.
- All packaging files, including `packaging/ProbabilityCalibrationTool.spec`: unchanged. No new package or release candidate.
- No Git commit, tag, or release was created.

Before the original Step 3 implementation, Git status was clean. That implementation's before/after SHA-256 comparison covered 175 baseline files; 174 were identical and only the authorized `bootstrap.py` changed. The correction starts from that already-dirty worktree and separately verifies no additional production change. The SPEC, dependency files, and packaging spec hashes are recorded in the validation report.

## Implementation behavior

### Preference, availability, and effective language

Only `Language.EN` (`en`) and `Language.ZH_CN` (`zh_CN`) exist. English is built in and requires neither settings nor any QM. Startup only reads `settings.ini`; it does not create directories or persist defaults, repairs, or fallback preferences.

`Preferred` is the saved/requested future language; `Effective` and active translators are immutable for this process. In particular, saved Chinese plus a missing/invalid pack keeps Preferred=zh_CN and Effective=en. `Available` is discovered at startup, always includes English, and cannot be promoted mid-session. Explicit Confirm may demote Chinese after a known pack disappears or fails preflight. Reappearance after demotion still requires restart.

The Golden test exercises all 15 combinations of five preference cases (default, en, zh_CN, invalid, read error) and three app-pack cases (missing, invalid, valid).

### Exact-path QSettings protocol

Every settings operation uses a fresh explicit-path INI object with fallbacks disabled and atomic synchronization required. Startup does not call setValue/remove/clear/sync. Read status is checked after reading, including lazy parse failures. Unreadable settings resolve to READ_ERROR/en without repair.

Explicit save captures old key presence/raw value, writes the selected enum value, synchronizes, requires NoError, then verifies the exact value using a fresh reader. Only verified success updates Preferred and SAVED_VALID; Effective and installed translators never change. Explicit DEFAULT/en is persisted; an already saved identical valid preference can be a no-op. Successful save clears the current fallback reason while retaining immutable startup notice history. `restart_required` is exactly Preferred != Effective.

Failures preserve context state. The failed writer restores the old raw value, or removes a newly introduced key, before teardown on a best-effort basis. Tests inspect teardown state for all three old states (absent/en/invalid) across AccessError, FormatError, set/sync exceptions, and fresh-reader mismatch/missing/error cases. Unrelated INI keys survive. Unsupported internal language arguments raise TypeError; unexpected save programming failures are not silently converted into normal settings errors.

This follows Qt's status/sync semantics; it does not claim a cross-object ACID transaction. See [Qt QSettings documentation](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QSettings.html).

### Catalog preflight and activation

The only app-pack path is `languages/probability_calibration_tool_zh_CN.qm`. Preflight checks existence, exact loading, nonempty catalog, locale metadata, limited locale normalization (trim and hyphen-to-underscore only), and the `Localization` / `Language` sentinel. Its seven results are tested. No expected Chinese translation string is hardcoded in production validation.

Explicit empty filename-load directory/delimiters/suffix disable Qt's default filename fallback; loaded `filePath()` is also verified. Real tests prove a `.qm.qm` neighbor cannot rescue a corrupt canonical file or shadow a valid one. No glob, arbitrary locale discovery, binary parser, manifest, signature scheme, or hash allowlist was introduced. The filename behavior is described in [Qt QTranslator documentation](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QTranslator.html) and was verified against the installed Qt runtime.

Only a valid app catalog permits Chinese activation. Qt framework lookup uses `QLibraryInfo.path(TranslationsPath)/qtbase_zh_CN.qm`. Qt installs first, app second; app translation takes precedence. Missing, unloadable, empty, or failed Qt installation degrades only framework translation. A failed app installation removes attempted translators; unexpected initialization failure is logged and bootstrap continues in English, without changing healthy business startup disposition.

Two explicit fallback reasons supplement the recommended names: APP_INSTALL_FAILED and INITIALIZATION_ERROR. They distinguish activation failure/internal initialization failure from malformed catalog/preferences. These are diagnostic states, not new business states or scope deviations.

### Ownership and bootstrap

Order is QApplication -> localization -> existing startup/runtime -> host/UI -> event loop -> UI disposal -> localization release -> runtime-resource release. Tests cover all seven existing startup dispositions, including notification-only ALREADY_RUNNING. Existing business startup, host construction, and event-loop exceptions still propagate normally.

LocalizationContext owns strong translator references outside DesktopHost/DesktopSession. Real QTranslator objects survive GC and actual DesktopHost session/window reconstruction. Saving English while Chinese is active retains the same objects and translations until restart; preflight translators are never installed.

## Required test families

All test files below are under the absolute repository path's `tests/localization/` directory.

| Family | Evidence | Result |
| --- | --- | --- |
| 1. Preferred/Available/Effective Golden matrix | `test_runtime.py`: 15-case cross-product | PASS |
| 2. Read states/no rewrite | `test_preferences.py`: real INI values, absent file/key, malformed INI; injected access/format/read failures | PASS |
| 3. Verified save/no-op/repair/immutability | `test_preferences.py`, `test_runtime.py` | PASS |
| 4. QSettings failure injection/teardown rollback | `test_preferences.py`: 24 old-state/failure combinations plus capture/programmer-error cases | PASS |
| 5. Unrelated INI keys preserved | `test_explicit_en_repairs_preference_preserves_keys_and_startup_notice` | PASS |
| 6. Seven preflight states | `test_all_seven_preflight_states` | PASS |
| 7. Real TS -> lrelease -> QM -> QTranslator | `test_real_locked_toolchain_ts_qm_qtranslator_smoke` | PASS |
| 8. Exact canonical filename/no locale fallback | `test_catalog.py`: aliases, renamed/non-QM/foreign-locale/double-suffix cases | PASS |
| 9. Locale metadata/sentinel | Real and injected structural catalog tests | PASS |
| 10. Startup-only discovery/demotion | `test_runtime.py`: no promotion, disappearance/corruption and no re-promotion | PASS |
| 11. Translator activation atomicity | Qt-first ordering, framework degradation, app-failure cleanup and bootstrap fallback | PASS |
| 12. Strong-reference lifetime | Real QTranslator/GC/actual business-window rebuild test | PASS |
| 13. Effective immutability | Actual translation remains active after preference save; public runtime state read-only | PASS |
| 14. Bootstrap order/ALREADY_RUNNING | `test_bootstrap.py`: seven startup dispositions and disposal ordering | PASS |
| 15. Zero persistence side effects | `test_architecture.py`: absent-root tests; 8 populated-DB language/failure states, all file SHA-256 and business rows unchanged | PASS |
| 16. Failures do not change business disposition | Real healthy StartupService stays READY_DRAFT for six failure cases and partial activation | PASS |
| 17. Architecture/schema v1 | AST dependency/call isolation; populated database PRAGMA user_version=1 | PASS |
| 18. Existing regression/Ruff | Full 1178-test suite and both Ruff commands | PASS |

Latest focused totals: architecture 28, bootstrap 17, catalog 32, preferences 52, runtime 36 = **165 passed**.

The persistence fixture creates a real completed round, snapshot, regime/stat rows, and existing Recent/Daily/Safety backups before taking the baseline. Localization then leaves every existing file hash and business row unchanged. No production/user database was used. All settings, database, backup, and TS/QM test artifacts are under pytest temporary roots; normal pytest temporary-directory retention applies.

## Validation results

All commands were run from the repository root. Exact commands, tool provenance, intermediate failures and final output summaries are in [the validation command record](<C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/localization_step3_validation_commands.md>).

| Command | Final observed result |
| --- | --- |
| `uv run pytest tests/localization/test_architecture.py -q` | 28 passed in 2.27s |
| `uv run pytest tests/localization -q` | 165 passed in 11.36s |
| `uv run pytest` | 1178 passed in 124.33s (0:02:04) |
| `uv run ruff check .` | All checks passed! |
| `uv run ruff format --check .` | 204 files already formatted (including the two reports) |
| `git diff --check` | Exit 0, no output |

Failed=0; errors=0; skipped=0; xfailed=0; xpassed=0 in every final validation run. The original 1013-test regression is retained; there are now 165 localization tests. The original implementation's standalone real-QM smoke and 33-test startup results remain in the historical command record; both are also covered by this correction's full rerun.

The real compiler is the existing repository `.venv\Scripts\pyside6-lrelease.EXE`, version 6.11.2. Tests verify the executable is inside this venv and PySide6 matches the existing `uv.lock` before compiling. Python is 3.13.14; pytest is 9.1.1. No new tooling dependency was required.

## Final Step 3 gates

| Gate | Result | Evidence |
| --- | --- | --- |
| G1 dependency boundary | PASS | localization imports only stdlib and QtCore; AST checks |
| G2 application/localization/startup order | PASS | bootstrap ordering/teardown tests |
| G3 English needs no QM | PASS | absent-root/default tests |
| G4 language matrix | PASS | all 15 Golden combinations |
| G5 seven preflight states | PASS | seven-status tests |
| G6 real Qt smoke | PASS | locked lrelease and real QTranslator |
| G7 app failure clean English fallback | PASS | invalid app, failed/partial installation cleanup |
| G8 Qt-only degradation | PASS | seven framework cases |
| G9 install order/lifetime | PASS | real translation precedence, GC and session rebuild |
| G10 settings protocol | PASS | real reads/saves and deterministic failure/read-back/teardown checks |
| G11 no live promotion | PASS | late pack, Confirm demotion, restart discovery |
| G12 effective immutable | PASS | no install/remove on preference change; actual translation retained |
| G13 no business mutation | PASS | absent-root and populated database/backup byte checks |
| G14 startup disposition unchanged | PASS | healthy real startup remains READY_DRAFT |
| G15 business-layer isolation | PASS | AST tests and protected-file diff/hash checks |
| G16 schema v1 | PASS | SCHEMA_VERSION and PRAGMA user_version both 1 |
| G17 existing English regression | PASS | all original tests unchanged; full suite green |
| G18 Ruff | PASS | check and format --check |
| G19 no hidden skip/xfail | PASS | zero skipped/xfailed/xpassed; no test deletion |
| G20 no Step 4/5 | PASS | Step 3 diff/hash audit: UI/business files unchanged, no formal TS/QM, Language dialog, or translated UI; no permanent UI translation prohibition |

## Incomplete work, deviations, and risks

Incomplete Step 3 work: **none**. Deviations from the prompt: **none**. SPEC deviations: **none**. SPEC concerns: **none**.

Known limits:

- QM files remain trusted translation assets, not a security sandbox; structural validation does not prove translation quality or malicious-file safety.
- Failed settings persistence receives best-effort in-memory restoration, not an ACID/durable rollback guarantee under disk failure, concurrent external edits, or process death.
- Availability is intentionally startup-only. Changing packs or Preferred requires restart for activation; this phase provides no language-selection UI.
- Effective=zh_CN describes translator activation, not completion of normal UI translation. Existing UI strings remain untouched pending separately authorized presentation work.
- Temporary TS/QM tests prove infrastructure, not a formal Chinese pack or a packaged Chinese release. No new release build was performed.

**Step 4 was NOT started. Step 5 was NOT started. No formal zh_CN language pack was created. Existing UI was NOT translated. Schema remains v1. Business/database/model behavior was not changed.**
