# Phase 7A 100k correctness and diagnostic performance

PASS for automated smoke; no GUI 100k browser or product bulk-import path was added. Manual packaged acceptance remains PENDING.

## Dataset and real paths

The primary isolated Schema v1 source contains exactly 100,000 completed eligible rounds and 100,000 matching full analysis snapshots: 70,000 wins / 30,000 losses, all character 1, current regime `regime-1-1`. Every block of ten has seven wins and three losses. Calculated timestamps start at 2026-01-01T00:00:00Z, advance two seconds, and completion follows one second later. Valid UUIDs deliberately decrease lexically as time advances, so last-included checks cannot accidentally pass by UUID ordering. The last chronological ID is `00ffffff-ffff-4fff-bfff-fffffffe7961`.

Release-only batched SQL creates the fixture in a controlled transaction; each historical snapshot is computed from prior counts through accepted Core functions. Real invariant checks pass. All 34 characters remain valid, with the other 33 zero/current caches. Test seed timestamps are moved before history; no schema or product source change.

Real StartupService repairs a deliberate stats_version=99 mismatch back to version 1, exact 100,000 / 70,000 / 30,000 and correct last ID; source rounds remain authoritative. Maintenance returns 34 safe summaries. Real Calculate with Use history freezes sample size 100,000 and commits exposure. Completing a win with Include=true changes live eligible history to 100,001 but preserves the complete prediction snapshot byte-for-field equality. Real Online Backup preserves all 100,001 completed rounds and snapshots.

## Timings (seconds)

Separate processes ran 50k and 100k sequentially. Measurements are one local diagnostic observation per size, not fixed release thresholds or a statistically powered benchmark.

| Operation | 50k | 100k | 100k / 50k |
|---|---:|---:|---:|
| fixture | 6.7827 | 13.6902 | 2.02× |
| invariant_inspection | 1.1032 | 2.3042 | 2.09× |
| stats_validation_and_rebuild | 0.5110 | 1.0043 | 1.97× |
| startup_including_repair_and_daily | 2.7835 | 5.5789 | 2.00× |
| maintenance | 0.0012 | 0.0014 | 1.11× |
| calculate | 0.4830 | 1.1345 | 2.35× |
| complete | 0.0178 | 0.0302 | 1.70× |
| large_online_backup | 0.7424 | 2.2351 | 3.01× |

Stats validation/rebuild is timed by a test-only subclass delegating unchanged to the accepted implementation through its existing dependency injection. It is INCLUDED in startup timing; do not add them together. Startup also includes integrity checks and Daily backup. The 100k repeated invariant inspections took 2.3065, 2.2495, 2.2407 seconds.

Fixture, invariants, repair and startup scale approximately with the twofold source increase. Calculate measured 2.35×; one Online Backup observation measured 3.01×, not hidden. The latter includes SQLite copying, candidate integrity verification and inventory/retention integrity reads; it is I/O-sensitive. Code inspection shows one Online Backup and bounded backup-inventory work, not an N-by-N history loop. A two-point, single-run ratio is insufficient to establish asymptotic behavior; no unexplained obvious quadratic path was found. There is no invented millisecond gate.

## Memory (MiB)

Windows GetProcessMemoryInfo captures native allocations as well as Python objects. Working set is resident memory; private bytes are a different committed-memory metric and must not be confused with resident RAM.

| Measurement | 50k | 100k |
|---|---:|---:|
| Pre-fixture working set | 94.64 | 94.57 |
| Process peak working set | 340.23 | 579.66 |
| Final working set | 108.93 | 109.44 |
| Pre-fixture private bytes | 1545.91 | 1545.83 |
| Final private bytes | 1561.92 | 1561.42 |

100k repeated invariant retained working sets after garbage collection: 107.52, 107.68, 108.23 MiB. The initial high private-commit baseline exists before fixture creation, after application/numerical imports; this measurement does not identify its exact native-library cause. It is not 1.5 GiB of additional resident data caused by 100k rows.

Accepted invariant inspection intentionally materializes all source rounds and snapshots and builds ID maps; transient peak memory therefore grows with history size. Baseline-adjusted peak at 100k is about twice that at 50k. Retained memory returns near baseline and the three repeated inspections show no obvious runaway accumulation. This is bounded diagnostic evidence, not a proof against all long-duration leaks or a claim of constant-space behavior. No arbitrary MB gate was added; a roughly 580 MiB transient resident peak remains a documented capacity consideration.

## Independent read-only integrity

Both sizes were checked before corruption/startup, after completion, and on Recent backup with SQLite mode=ro / query_only=ON. Every recorded integrity result is `ok`, FK violations empty, schema version 1 and round/snapshot counts equal. The 100k source and Recent end at 100,001 completed / pending 0. These generated DBs remain under work/, never in dist/. Each real startup additionally creates its normal Daily backup.

Exact paths and unrounded measurements are retained in `performance_50k.json` and `performance_100k.json`. Later verification does not run any migration, stats rebuild or repair. None of these automated DBs substitutes for the final post-manual packaged workflow DB required by gate 18.

## Commands

```text
uv run pytest tests/release/test_performance_100k.py -q
uv run python -m tools.release_performance --rounds 50000 --root work/phase7a-perf-50k --evidence outputs/release/performance_50k.json
uv run python -m tools.release_performance --rounds 100000 --root work/phase7a-perf-100k --evidence outputs/release/performance_100k.json
```

The focused test initially passed in 34.31s. The evidence commands both exited 0; diagnostic root directories must not exist before rerunning, so choose new isolated names for another run.

