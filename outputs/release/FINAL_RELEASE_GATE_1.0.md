# Final Release Gate 1.0 — Phase 7A evidence

13 PASS, 0 FAIL, 5 PENDING. This is a Release Candidate for manual Phase 7B, NOT final 1.0 release acceptance.

Final EXE SHA-256: `d45ebba5acd758b05401c1bd6b146af815517605fe8dacb7426120d9b2baeaf1`.

| # | Frozen requirement | Status | Evidence / remaining work |
|---:|---|---|---|
| 1 | release-blocking tests pass | PASS | 1013 passed, all failure/skip/xfail/xpass counts 0. [pytest_final.log](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pytest_final.log) |
| 2 | Ruff check passes | PASS | uv run ruff check . — All checks passed, before final clean build. [phase7a_validation_commands.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_validation_commands.md) |
| 3 | Ruff format check passes | PASS | uv run ruff format --check . — 189 files already formatted, before final clean build. [phase7a_validation_commands.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_validation_commands.md) |
| 4 | no unexplained skip/xfail | PASS | 0 skipped, 0 xfailed, 0 xpassed; accepted tests preserved by SHA-256. [source_integrity.json](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/source_integrity.json) |
| 5 | fresh DB E2E | PASS | Accepted real StartupService/DesktopHost end-to-end test rerun in full suite (source/offscreen). [pytest_final.log](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pytest_final.log) |
| 6 | pending recovery E2E | PASS | Real source close/start/explicit Continue/same frozen snapshot/completion/New Round test rerun. [pytest_final.log](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pytest_final.log) |
| 7 | backup/restore E2E | PASS | Normal/emergency restore, pre/post replacement failures, stale Session revocation, Safety/Recent rerun. [phase7a_validation_commands.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_validation_commands.md) |
| 8 | migration | PASS | 7 frozen migration tests rerun, Schema v1 unchanged. [pytest_final.log](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/pytest_final.log) |
| 9 | correction | PASS | Safety-before-write, immutable correction chain/no branch and Recent checks rerun. [phase7a_validation_commands.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_validation_commands.md) |
| 10 | anti-anchoring | PASS | No pre-lock/reference=false/no_history/insufficient history leakage, non-directional admin and exposure-before-render tests rerun. [phase7a_validation_commands.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_validation_commands.md) |
| 11 | 100k smoke | PASS | 100,000 eligible under one current regime; real repair/Calculate/complete/backup; frozen n=100000 while live n=100001. [phase7a_performance_100k.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/phase7a_performance_100k.md) |
| 12 | Windows 125% DPI | PENDING | Phase 7B manual acceptance. No real Windows DPI acceptance performed. [PHASE_7B_MANUAL_ACCEPTANCE_CHECKLIST.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/PHASE_7B_MANUAL_ACCEPTANCE_CHECKLIST.md) |
| 13 | Windows 150% DPI | PENDING | Phase 7B manual acceptance. No real Windows DPI acceptance performed. [PHASE_7B_MANUAL_ACCEPTANCE_CHECKLIST.md](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/PHASE_7B_MANUAL_ACCEPTANCE_CHECKLIST.md) |
| 14 | PyInstaller onedir | PASS | Clean build; whole folder, AMD64 Windows GUI, 298 files. [artifact_audit.json](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/artifact_audit.json) |
| 15 | packaged app outside PyCharm/.venv | PASS | Full copy outside repo with spaces, absolute EXE, unrelated cwd and sanitized environment; actual qwindows/SQLite/SciPy native load. [packaged_smoke.json](C:/Users/rxy71/Documents/Codex/2026-08-30/files-pasted-by-the-user-probability/outputs/release/packaged_smoke.json) |
| 16 | packaged app completes full test round | PENDING | Phase 7B manual packaged full round and controlled history-valid/SciPy UI path. Launch is not full-round acceptance. |
| 17 | packaged app survives close/reopen correctly | PENDING | Phase 7B manual A/B/C normal-close/Recovery test. Automated child termination does not satisfy this gate. |
| 18 | final PRAGMA integrity_check returns ok | PENDING | Final post-Phase-7B packaged-workflow DB required. Automated 100k/backup/fresh DB checks passed but do not close this gate. |

Separate packaged single-instance manual dismissal/exit confirmation also remains PENDING. The automated smoke observed an exclusive lock and notification-only B while A remained valid; it did not dismiss the modal or perform normal GUI closure. No manual screenshots or acceptance results were fabricated.

