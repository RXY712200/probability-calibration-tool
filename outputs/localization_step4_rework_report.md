# Localization Step 4 — External Review Narrow Rework Report

Date: 2026-09-01

Status: **STEP 4 NARROW REWORK COMPLETE — READY FOR EXTERNAL RE-REVIEW**

This report supersedes the implementation's rejected Step 4 review status. It does not declare Step 4 accepted or frozen. Step 5 was not started.

## Scope and files

A SHA-256 inventory of 233 project paths was captured before the rework. Before creating these two reports, exactly eight existing files changed, zero were added, and zero were removed. The other 225 paths remained byte-identical.

### Production files modified

- [src/probability_calibration_tool/ui/localization.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/localization.py) — explicit public expected-error whitelist; no UNKNOWN/stale-record fallback.
- [src/probability_calibration_tool/ui/language_dialog.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/language_dialog.py) — frozen canonical sources, visible availability, provenance and healthy saved no-op behavior.
- [src/probability_calibration_tool/ui/desktop_boundary.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/desktop_boundary.py) — routes only whitelisted expected errors inline/to the expected banner; all others use report_unexpected.
- [src/probability_calibration_tool/ui/main_window.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/main_window.py) — applies the same routing to the direct MainWindow path.
- [src/probability_calibration_tool/ui/safety_window.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/src/probability_calibration_tool/ui/safety_window.py) — prevents its direct input-error presentation hook from rendering internal/unmapped codes.

### Tests modified

- [tests/localization/test_presentation.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/localization/test_presentation.py) — freezes the exact public-code set; UNKNOWN, three stale codes, string and unhashable unknowns are not presentable; stale sources are absent from extraction.
- [tests/localization/test_language_ui.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/localization/test_language_ui.py) — exact canonical copy, provenance, visible-only availability/demotion, no-op Confirm and success/failure notice contracts.
- [tests/localization/test_presentation_integration.py](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/localization/test_presentation_integration.py) — English/translated unexpected routing for all five required cases, direct Main/Safety paths, logs, secrecy, Error IDs and no-retry after commit.

### Reports created

- [outputs/localization_step4_rework_report.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/localization_step4_rework_report.md)
- [outputs/localization_step4_rework_validation.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/localization_step4_rework_validation.md)

No other rework file changed.

## External-review findings and fixes

### 1. Unknown/unmapped semantic-error routing

`ERROR_SOURCES` now contains only public expected codes. `ErrorCode.UNKNOWN`, `ROUND_NOT_FOUND`, `ROUND_NOT_PENDING` and `ROUND_NOT_COMPLETED` are deliberately absent. `is_public_expected_error()` is an explicit, type-safe membership gate; even an unhashable foreign code returns false.

`expected_error()` has no generic fallback. It can render only a whitelisted source. DesktopBoundary checks the whitelist before inline/banner presentation. Any unknown/internal code passes the original exception to `session.report_unexpected()`, producing the fixed generic public message, Error ID and full diagnostic traceback without retry.

Direct MainWindow and SafetyWindow paths use the same gate. No path displays `str(exc)`, branches on English error messages or converts internal pending/completed tokens to UI text.

### 2. Tests approving wrong unknown behavior

The old unrecognized-code generic-without-ID expectation was removed. Tests now prove:

- unrecognized InputValidationError;
- ErrorCode.UNKNOWN BusinessRuleError;
- RoundNotFoundError;
- RoundNotPendingError;
- RoundNotCompletedError;

all use the unexpected path in English and marker-translated modes. They assert one operation call, Error ID in UI, no private/lifecycle diagnostic in UI, private detail plus traceback in log, and no database row for a pre-commit failure.

A separate commit-then-internal-error test asserts the committed Calculate row exists exactly once and the operation was called once. Direct MainWindow and SafetyWindow routing are exercised independently. Existing public expected-error placement/message tests remain intact.

### 3. Frozen Step 4.6 canonical English sources

All nine requested public sources are exact, including punctuation and `简体中文`:

- four startup fallback messages;
- Qt framework degradation;
- zh_CN confirm-time preflight failure;
- the one generic settings save/access/format/verification failure;
- new-language success;
- explicit-English success.

APP_INSTALL_FAILED reuses the frozen pack-load failure source. INITIALIZATION_ERROR reuses the frozen read-failure source so no extra alternative UI copy remains. Diagnostics still remain in logs. No QSettings implementation/location details are exposed.

### 4. Available-language presentation

Each available entry has a row container. Refresh sets both enabled and visible state from `context.available_languages`. An unavailable zh_CN row is hidden, not displayed as a disabled Available choice. Preferred=zh_CN can still appear in the informational Preferred summary.

Confirm-time pack demotion immediately unchecks, disables and hides zh_CN. Recreating the pack and refreshing the dialog does not re-promote it because the Step 3 process context remains demoted.

### 5. Language provenance

Visible entry rows show:

- English + translated `Built-in`;
- 简体中文 + translated `External language pack`.

Both provenance sources use the Localization context. The self-name radio text remains exactly `English` / `简体中文`, including under the marker translator.

### 6. Healthy saved no-op

For `PreferenceState.SAVED_VALID`, selecting the already saved Preferred language disables Confirm. The confirm handler has a second defensive guard and neither closes the dialog nor calls `save_preference()`.

DEFAULT English can still be explicitly persisted. Invalid/read-error explicit English repair remains enabled and uses the frozen English success notice.

## Test changes and results

| Final command/scope | Passed | Failed | Errors | Skipped | Xfailed | Xpassed |
|---|---:|---:|---:|---:|---:|---:|
| `uv run pytest` | 1301 | 0 | 0 | 0 | 0 | 0 |
| `uv run pytest tests/localization -q` | 288 | 0 | 0 | 0 | 0 | 0 |
| Architecture/static suite | 45 | 0 | 0 | 0 | 0 | 0 |
| Presentation/language/error integration suite | 112 | 0 | 0 | 0 | 0 | 0 |
| Dedicated real extraction test | 1 | 0 | 0 | 0 | 0 | 0 |

Full suite: **1301 passed in 128.31s (0:02:08)**.

The rework adds 15 tests over the rejected implementation's 1286 total. No existing test was deleted, skipped, xfailed, weakened or given changed mathematical expected values.

## Extraction audit

Actual installed `pyside6-lupdate -extensions py` against production `src` generated a temporary, untracked TS outside the repository:

`C:/Users/rxy71/AppData/Local/Temp/pct-step4-rework-audit-42c8b6d2-d5cf-4cf8-ba61-d3118309ef3f/step4-rework-extraction.ts`

Result: **225 source texts**, exactly the same 12 frozen contexts:

| Context | Sources |
|---|---:|
| Analysis | 25 |
| AppShell | 9 |
| Characters | 36 |
| Correction | 11 |
| DomainLabels | 19 |
| Errors | 34 |
| Localization | 19 |
| Maintenance | 13 |
| Recovery | 7 |
| Restore | 17 |
| Round | 29 |
| StartupSafety | 6 |

The count changed legitimately from 230. Errors lost three stale-round public sources. Localization canonical sources are shared/deduplicated across semantically equivalent failures while adding the two provenance sources. No official TS/QM exists in src or packaging.

## Schema and frozen-boundary audit

Actual production `initialize_v1` in a fresh in-memory database:

- `PRAGMA user_version = 1`
- exact tables: `character_stats`, `characters`, `history_regimes`, `meta`, `round_analysis_snapshots`, `rounds`

HEAD remains `00bd24b9fdc509809962ace4412b1e233b7c6598`. Version remains 1.0.0.

No rework changes were made to Core, Domain, Application, persistence, infrastructure, bootstrap/DesktopHost, top-level Step 3 localization infrastructure, SPEC_1.0.md, dependencies, schema, migrations, math, Workflow, Correction, Recovery, Restore, backup policy, packaging, release metadata or prior reports.

No commit, reset, checkout, tag or version bump was performed.

## Git diff and scope

The repository remains intentionally dirty from accepted Step 3 plus the rejected Step 4 implementation. Therefore Git's HEAD-relative stat is cumulative, not a rework-only stat:

```text
45 files changed, 711 insertions(+), 258 deletions(-)
```

Untracked Step 3/4 files and reports are not included in that Git stat. The rework-only SHA-256 comparison is authoritative for scope: **8 modified + 2 required reports created; 0 removed; all 225 other baseline paths unchanged**.

Final lint/format/whitespace results are recorded in the validation file.

SPEC deviations: none. Step 5 work: none.

**STEP 4 NARROW REWORK COMPLETE — READY FOR EXTERNAL RE-REVIEW**
