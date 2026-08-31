# Phase 7A validation commands and results

Working directory for commands unless explicitly isolated by the helper:

`C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability`

Windows 11 build 26200 x64; Python 3.13.14; pytest 9.1.1. Accepted source semantics, Schema v1, Golden values and SPEC are unchanged.

## Chronological release validation

| Literal command | Result |
|---|---|
| `uv run pytest` (BEFORE any Phase 7 edits) | 992 passed in 50.45s; failed/skipped/xfailed/xpassed all 0. Baseline verified before packaging work. |
| `uv lock` | Success; normal lock regeneration adds PyInstaller/build transitive dependencies. |
| `uv sync` | Success; build tools installed. Accepted SciPy 1.18.1 / PySide6 6.11.2 unchanged. |
| `uv run pytest tests/release/test_performance_100k.py -q` | 1 passed in 34.31s. |
| `uv run pytest tests/release/test_release_artifact.py tests/release/test_release_verify.py -q` | Initial 15 passed in 0.77s. |
| `uv run ruff check .` (development pass) | Initially 2 formatting/import I001 findings in new performance helper, resolved by formatting; no lint settings changed. |
| `uv run ruff format tools tests/release packaging/pyinstaller_entry.py` | 6 new files reformatted, 6 unchanged; accepted files untouched. |
| `uv run pytest tests/release/test_release_artifact.py tests/release/test_release_verify.py tests/release/test_manual_history_fixture.py -q` | Development run: 1 failed/18 passed due to new helper importing enum from wrong public module; fixed to accepted domain.enums import. Rerun: 19 passed in 0.96s. |
| `uv run pytest` (pre-first-build) | 1012 passed in 84.06s, all other outcome counts 0. Preserved in pytest_pre_packaging_fix.log. |
| `uv run ruff check .` / `uv run ruff format --check .` (pre-first-build) | Passed; format 188 files. |
| `uv run pyinstaller --clean --noconfirm packaging/ProbabilityCalibrationTool.spec` (first build) | Build succeeded (~58.6s) but EXE launch later FAILED on wrong Poppler ICU DLL. This build was rejected, not accepted as RC. |
| `uv run python -m tools.release_verify --artifact dist/ProbabilityCalibrationTool --evidence outputs/release/artifact_audit.json` (first build) | Static audit passed (346 files); actual launch correctly remained a separate blocking check. |
| `uv run python -m tools.packaged_smoke --artifact dist/ProbabilityCalibrationTool --evidence outputs/release/packaged_smoke.json` (first build) | FAILED exit 1; process error before DB initialization. No success JSON emitted. Detailed root cause and rejected artifact paths in phase7a_packaging_first_failure.md. |
| `uv run pytest tests/release/test_release_artifact.py -q` (spec PATH fix) | 17 passed in 0.19s, including poisoned build-PATH regression. |
| `uv run pytest` (FINAL, after ALL source/config fixes) | **1013 passed in 83.55s; 0 failed, 0 skipped, 0 xfailed, 0 xpassed.** |
| `uv run ruff check .` (FINAL pre-build) | **All checks passed!** Exit 0. |
| `uv run ruff format --check .` (FINAL pre-build) | **189 files already formatted.** Exit 0. |
| `uv run pyinstaller --clean --noconfirm packaging/ProbabilityCalibrationTool.spec` (FINAL clean build) | **Success**, ~39.4s; build/ and dist/ absent at start after exact-target archive of rejected outputs. |
| `uv run python -m tools.release_verify --artifact dist/ProbabilityCalibrationTool --evidence outputs/release/artifact_audit.json` (FINAL) | **PASS**, 298 files, 223,928,257 bytes, x64 GUI PE, no project/user leakage. |
| `uv run python -m tools.packaged_smoke --artifact dist/ProbabilityCalibrationTool --evidence outputs/release/packaged_smoke.json` (FINAL) | **PASS**, exit 0; covers launch, external-copy independence, unrelated cwd, isolated LOCALAPPDATA, native Qt/SciPy load, lock/modal observation. Normal GUI close/manual single-instance dismissal not claimed. |
| `uv run pytest --collect-only -q` (final collection evidence) | 1013 tests collected in 0.79s; collection alone is not the pass evidence — see actual full run. |

The actual PowerShell final build invocation additionally checked that old targets did not exist and captured the log:

```powershell
if ((Test-Path -LiteralPath build) -or (Test-Path -LiteralPath dist)) { throw 'Old artifacts remain.' }; uv run pyinstaller --clean --noconfirm packaging/ProbabilityCalibrationTool.spec 2>&1 | Tee-Object -FilePath outputs/release/pyinstaller_build.log; exit $LASTEXITCODE
```

No source/config edits followed the final regression/build. Only QA evidence reports were written. Source-integrity comparison after build confirmed all 175 tested source/config hashes unchanged. Final report-stage reruns: `uv run ruff check .` returned All checks passed; `uv run ruff format --check .` returned 193 files already formatted. Final artifact inventory recheck matched both 298-file copies; matrix verification confirmed exactly 18 rows (13 PASS, 5 PENDING) and no fabricated manual screenshots.

## Focused performance commands (both exit 0)

```text
uv run python -m tools.release_performance --rounds 50000 --root work/phase7a-perf-50k --evidence outputs/release/performance_50k.json
uv run python -m tools.release_performance --rounds 100000 --root work/phase7a-perf-100k --evidence outputs/release/performance_100k.json
```

Both are sequential separate-process diagnostics; root directories must be new. Correctness and unrounded measurements are in their JSON reports. No arbitrary timing or memory threshold was invented.

## Independent final read-only integrity commands (exit 0)

```text
uv run python -m tools.release_verify --database "C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\work\phase7a-perf-100k\data\probability.db" --recent "C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\work\phase7a-perf-100k\backups\recent\recent_20260831T051721.818104Z_dfdebfd4-30ad-47e0-8f50-8a4f1c3a0997.db" --evidence outputs/release/automated_integrity_100k.json
uv run python -m tools.release_verify --database "C:\Users\rxy71\AppData\Local\Temp\Probability Calibration Tool RC dgajh1ad\isolated LOCALAPPDATA\ProbabilityCalibrationTool\data\probability.db" --evidence outputs/release/automated_integrity_packaged.json
uv run python -m tools.release_verify --database "C:\Users\rxy71\AppData\Local\Temp\Probability Calibration Tool RC dgajh1ad\isolated LOCALAPPDATA\ProbabilityCalibrationTool\backups\daily\daily_2026-08-31_20260831T053058.126832Z_6804479a-5801-4fa2-baec-2aaa7805fe2e.db" --evidence outputs/release/automated_integrity_packaged_daily.json
```

All report integrity=ok, no FK violations, schema v1, equal round/snapshot totals. 100k source and Recent have 100001 completed/pending 0; fresh packaged source and Daily have zero records. The final packaged Daily is explicitly a Daily backup, not a Recent from a completed packaged round. No --final-manual acceptance invocation was performed against a manual-workflow DB.

## Phase 1–6 accepted groups rerun in the unfiltered full suite

| Group | Passed |
|---|---:|
| Phase 1 Core | 213 |
| Phase 2 persistence (excluding later Phase 4 migration tests) | 293 |
| Phase 3 application (excluding later reliability/presentation tests) | 153 |
| Phase 4 application reliability + infrastructure + migration | 107 |
| Phase 5 UI + 4 presentation-capability tests | 106 |
| Phase 6 desktop integration | 120 |
| Phase 7A focused release regressions | 21 |
| Total | 1013 |

No tests were filtered out of the final full run, skipped, xfailed, weakened or removed. SHA-256 preserves all accepted test files and expected Golden values.

## Explicit invariant evidence references

These source-level tests were actually rerun by the final full command; none is substituted for a manual packaged gate:

- Fresh/recovery/Recent/frozen prediction: `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/integration/desktop/test_end_to_end.py`.
- Exposure commit before presentation: same file's test_full_integration_valid_history_is_committed_before_render_and_snapshot_stays_frozen; `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/integration/application/test_calculate.py` test_golden_c_exposure_and_snapshot_durable_before_view_construction.
- No reference=false/no_history/insufficient numerical leakage, cleared stale views: `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/ui/test_analysis_safety.py`, `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/integration/application/test_calculate.py`, `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/integration/application/test_recovery.py`.
- Draft/subjective lock and non-directional Maintenance/Correction: `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/ui/test_pre_run.py`, `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/ui/test_maintenance.py`, `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/integration/application/test_regime_maintenance.py`, `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/integration/application/test_correction.py`.
- Safety-before-correction, immutable/no-branch chain and Recent: `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/integration/application/test_correction.py`, `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/integration/desktop/test_correction_integration.py`, `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/integration/desktop/test_recent_integration.py`.
- Normal/emergency Restore, pre-replacement preservation, post-replacement emergency, stale Session revocation: `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/integration/application/reliability/test_restore.py`, `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/integration/application/reliability/test_restore_runtime_state.py`, `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/integration/desktop/test_restore_session_rebuild.py`.
- Schema migration: `C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/tests/integration/persistence/test_migrations_phase4.py`.

## Scope of remaining work

Manual Windows 125%/150%, full packaged round, normal close/reopen Recovery, actual history-visible SciPy UI, final post-manual DB integrity and single-instance modal dismissal remain PENDING. No Phase 7B manual acceptance was performed.
