# Localization Step 5 External Review Narrow Rework Report

## Scope and outcome

This narrow rework corrected the two external-review findings in the official Simplified Chinese TS, expanded permanent exact-copy protection for the frozen current sources, regenerated the human-review inventory, and rebuilt/reverified the runtime candidate. No production file under `src\` and no SPEC, schema, dependency, packaging, version, installer, tag, or business behavior changed. Step 6–9 were not started.

## Rework files

Modified:

- `translations\probability_calibration_tool_zh_CN.ts` — corrected the two externally reviewed Simplified Chinese translations without changing either English source or the 225-key catalog.
- `tests\localization\test_step5_catalog.py` — added exact permanent assertions for the two corrections and expanded frozen-Chinese protection to every applicable reviewed current source group.
- `outputs\localization_step5_translation_inventory.md` — automatically regenerated from the corrected final TS so its hash and all 225 entries match the final catalog.

Added:

- `outputs\localization_step5_rework_report.md` — records narrow-rework scope, exact wording, coverage, and final results.
- `outputs\localization_step5_rework_validation.md` — records literal validation commands and exact outcomes.

Deleted:

- none

Generated ignored candidate:

- `build\localization\probability_calibration_tool_zh_CN.qm` — freshly rebuilt verification candidate; not a committed production artifact.

The original rejected `outputs\localization_step5_completion_report.md` and `outputs\localization_step5_validation_commands.md` were not overwritten or rewritten.

## Required translation corrections

- `Restore / pre_restore` → `备份恢复前备份`
- `Errors / Backup accepted; rotation stopped safely with possible over-retention.` → `备份已接受；轮换已安全停止，保留的备份数量可能超过设定上限。`

Both values are asserted literally in `tests\localization\test_step5_catalog.py` and were also verified through the real compiled QTranslator.

## Exact frozen-Chinese protection

The focused exact-copy gate now contains 194 literal assertions:

- 135 current `(context, source)` keys in `FROZEN_EXACT`:
  - Round: 29
  - Analysis: 25
  - DomainLabels: 19
  - Localization: 19
  - Correction: 11
  - Restore: 11
  - Maintenance: 10
  - AppShell: 5
  - Recovery: 4
  - StartupSafety: 2
- 23 frozen expected/reviewed Errors translations, including the corrected over-retention wording.
- 34 exact character translations plus Normal/Tainted headers: 36.

This protects the frozen high-risk corpus while leaving the complete 225-unit TS as the sole full translation authority.

## Catalog and inventory

- TS SHA-256: `82ce883454ed19a5c34d3f8b0660262e982073aa82349f4897075e769c436257`
- Active units: 225
- Contexts: exactly 12
- Unfinished/empty/whitespace-only/vanished/obsolete/duplicates/numerus: all 0
- Placeholder mismatches: 0
- Fresh extraction missing/extra keys: 0/0
- Inventory: `outputs\localization_step5_translation_inventory.md`
- Inventory header represents the final TS hash above and 225 active entries across 12 contexts.

## Qt/QM and runtime verification

- Strict lrelease: exit 0; 225 finished, 0 unfinished.
- QM: `build\localization\probability_calibration_tool_zh_CN.qm`
- QM size: 19,429 bytes
- QM SHA-256: `712747514fccce8f3f5e610dbdddf07187f9167b22d33365f97ca06a4d9b5547`
- Real QTranslator: load true, nonempty, language `zh_CN`, exact equivalence 225/225.
- Corrected `pre_restore` compiled value: exact true.
- Corrected over-retention compiled value: exact true.
- Step 3 preflight: `valid`.
- Preferred=`zh_CN`; Effective=`zh_CN`; Available=`en,zh_CN`; fallback=`none`; app translator owned=true.
- Qt framework translation status on this machine: `loaded`.
- Installed-translator context smoke: 12/12.
- Real widget, English fallback, and missing-pack fallback gates remained passing in the Step 5 runtime suite.

## Tests and static gates

- Focused Step 5 catalog: 5 passed in 0.98s.
- Step 5 runtime: 5 passed in 0.99s.
- All localization: 298 passed in 16.08s.
- Full suite: 1311 passed in 108.44s.
- Final outcome categories: failed 0, errors 0, skipped 0, xfailed 0, xpassed 0.
- `uv run ruff check .`: pass.
- `uv run ruff format --check .`: 221 files already formatted.
- `git diff --check`: pass.

## Schema and protected scope

- `PRAGMA user_version=1`.
- Exact tables: character_stats, characters, history_regimes, meta, round_analysis_snapshots, rounds.
- Protected hash comparison: 181 baseline files, 181 final files, missing 0, added 0, changed 0.
- Protected groups unchanged: `src\`, `SPEC_1.0.md`, `pyproject.toml`, `uv.lock`, `packaging\`.
- Initial and final HEAD: `00bd24b9fdc509809962ace4412b1e233b7c6598`.
- No reset, checkout, commit, or tag was performed.

## Stage boundary

- Step 6 not started.
- Step 7 not started.
- Step 8 not started.
- Step 9 not started.
- No release packaging or version bump was performed.

`STEP 5 NARROW REWORK COMPLETE — READY FOR EXTERNAL RE-REVIEW`
