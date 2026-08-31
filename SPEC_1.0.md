# Probability Calibration Tool — SPEC 1.0

**Specification Version:** 1.0  
**Status:** Frozen implementation baseline  
**Target Platform:** Windows 11 x64  
**Development Baseline:** CPython 3.13.14 x64

---

# 1. Purpose

Probability Calibration Tool 1.0 is a local, single-user Windows desktop application for recording and analyzing repeated binary events.

It maintains two strictly independent probability lines:

1. **Subjective model** — the user's independently entered probability.
2. **Historical model** — a statistical estimate derived only from eligible historical observations for the same character and current History Regime.

Version 1.0 prioritizes:

- reproducibility;
- auditability;
- prevention of anchoring and future-data leakage;
- preservation of raw records;
- crash recovery;
- database integrity;
- explicit model versioning;
- deterministic rules.

The application MUST NOT:

- fuse subjective and historical probabilities;
- use another character's data in the current character model;
- silently modify subjective probability based on history;
- silently learn or alter frozen model constants;
- automatically change History Regime;
- physically delete audit history during normal operation;
- retroactively rewrite past prediction snapshots;
- convert the analysis into automatic stake-size or participation instructions.

---

# 2. Technology Stack

## 2.1 Platform

- Windows 11 x64 only for version 1.0.

Persistent data root:

`%LOCALAPPDATA%\ProbabilityCalibrationTool\`

Program files and persistent user data MUST remain separate.

---

## 2.2 Python

- CPython 3.13.x x64.
- Development baseline: CPython 3.13.14.

---

## 2.3 GUI

Use:

- PySide6;
- Qt Widgets;
- programmatic Python UI construction;
- limited QSS where useful.

Do NOT use:

- `.ui` files;
- Qt Designer as runtime source;
- QML / Qt Quick;
- third-party UI/theme frameworks.

---

## 2.4 Statistical Computation

Use:

- standard library `math`;
- SciPy;
- `scipy.stats.beta` for Beta CDF/PPF.

Do NOT implement a custom Beta inverse CDF.

---

## 2.5 Database

Use:

- SQLite;
- standard library `sqlite3`;
- explicit SQL;
- Repository pattern;
- Unit of Work.

Do NOT use an ORM.

---

## 2.6 Migration

Use explicit application-controlled migrations based on:

`PRAGMA user_version`

Do not use Alembic.

---

## 2.7 Dependency Management

Use:

- `uv`;
- `pyproject.toml`;
- `uv.lock`;
- project-local `.venv`.

`pyproject.toml` is the canonical direct-dependency declaration.

`uv.lock` is the canonical dependency lock.

---

## 2.8 Models

Use:

- `dataclasses`;
- `Enum`;
- type hints.

Calculation result DTOs SHOULD normally use:

`@dataclass(frozen=True)`

Do not introduce Pydantic in version 1.0.

---

## 2.9 Testing and Quality

Use:

- pytest;
- Ruff.

Release checks:

- `ruff check`
- `ruff format --check`

Strict mypy is not a version 1.0 release blocker.

---

## 2.10 Logging

Use standard library:

- `logging`;
- `RotatingFileHandler`.

Configuration:

- maximum current log size: 2 MiB;
- `backupCount = 5`.

Thus the current log plus up to five rotated logs are retained.

---

## 2.11 Packaging

Use:

- PyInstaller;
- `onedir`.

Version 1.0 does not require a `onefile` build.

---

# 3. Architecture

Use `src` layout:

ProbabilityCalibrationTool/
├── pyproject.toml
├── uv.lock
├── README.md
├── SPEC_1.0.md
├── src/
│   └── probability_calibration_tool/
│       ├── __main__.py
│       ├── bootstrap.py
│       ├── domain/
│       ├── core/
│       ├── application/
│       ├── persistence/
│       ├── infrastructure/
│       └── ui/
├── tests/
└── tools/

Primary dependency direction:

`UI -> Application -> Core / Domain`

Application may also call Persistence and Infrastructure.

Core/Domain MUST NOT depend on:

- Qt;
- SQLite;
- filesystem;
- backup implementation.

---

# 4. Module Responsibilities

## `domain/`

Defines pure data semantics:

- Enums;
- dataclasses;
- DTOs.

No database or GUI access.

## `core/`

Pure deterministic mathematical/model logic.

Recommended modules:

- `subjective.py`
- `historical.py`
- `ev.py`
- `validation.py`
- `model_specs.py`

Core MUST NOT execute SQL or access Qt.

## `application/`

Owns:

- business workflow;
- state machine;
- transaction intent;
- history-exposure decisions;
- regime operations;
- recovery;
- correction workflow.

## `persistence/`

Owns:

- SQLite schema;
- explicit SQL;
- repositories;
- migrations;
- Unit of Work.

Repositories MUST NOT call `commit()` independently.

## `infrastructure/`

Owns:

- persistent paths;
- backup implementation;
- logging setup;
- runtime lock.

## `ui/`

Thin PySide6 presentation layer.

UI MUST NOT:

- execute SQL;
- reproduce model formulas;
- call SciPy to calculate probabilities.

## `bootstrap.py`

Single dependency-composition point.

Business rules MUST NOT live here.

## `__main__.py`

Minimal application entry point.

---

# 5. Frozen Model Constants

All frozen mathematical constants MUST be centralized and versioned.

At minimum:

- `SUBJECTIVE_MODEL_VERSION = 1`
- `HISTORY_MODEL_VERSION = 1`
- `HISTORY_GATE_VERSION = 1`
- `ODDS_ANALYSIS_VERSION = 1`
- `STATS_VERSION = 1`
- `FLOAT_EPSILON = 1e-12`

Do not scatter model constants as magic numbers throughout the project.

---

# 6. Characters

Version 1.0 contains exactly 34 stable character identities arranged as 17 paired rows.

| ID | row | normal internal code | normal display | tainted internal code | tainted display |
|---:|---:|---|---|---|---|
| 1 / 18 | 1 | `isaac` | Isaac | `tainted_isaac` | Tainted Isaac |
| 2 / 19 | 2 | `magdalene` | Magdalene | `tainted_magdalene` | Tainted Magdalene |
| 3 / 20 | 3 | `cain` | Cain | `tainted_cain` | Tainted Cain |
| 4 / 21 | 4 | `judas` | Judas | `tainted_judas` | Tainted Judas |
| 5 / 22 | 5 | `blue_baby` | ??? | `tainted_blue_baby` | Tainted ??? |
| 6 / 23 | 6 | `eve` | Eve | `tainted_eve` | Tainted Eve |
| 7 / 24 | 7 | `samson` | Samson | `tainted_samson` | Tainted Samson |
| 8 / 25 | 8 | `azazel` | Azazel | `tainted_azazel` | Tainted Azazel |
| 9 / 26 | 9 | `lazarus` | Lazarus | `tainted_lazarus` | Tainted Lazarus |
| 10 / 27 | 10 | `eden` | Eden | `tainted_eden` | Tainted Eden |
| 11 / 28 | 11 | `the_lost` | The Lost | `tainted_lost` | Tainted Lost |
| 12 / 29 | 12 | `lilith` | Lilith | `tainted_lilith` | Tainted Lilith |
| 13 / 30 | 13 | `keeper` | Keeper | `tainted_keeper` | Tainted Keeper |
| 14 / 31 | 14 | `apollyon` | Apollyon | `tainted_apollyon` | Tainted Apollyon |
| 15 / 32 | 15 | `the_forgotten` | The Forgotten | `tainted_forgotten` | Tainted Forgotten |
| 16 / 33 | 16 | `bethany` | Bethany | `tainted_bethany` | Tainted Bethany |
| 17 / 34 | 17 | `jacob_and_esau` | Jacob & Esau | `tainted_jacob` | Tainted Jacob |

IDs are stable and MUST NOT be reordered later merely for UI convenience.

The Tainted side of row 17 is Tainted Jacob; Tainted Esau is not a separate playable character entry.

---

# 7. Anti-Anchoring Rule

This is a critical invariant.

Before the current round's subjective probability has been successfully locked by Calculate, the application MUST NOT reveal quantitative directional history information to the user.

Prohibited before subjective lock includes:

- historical win rate;
- historical wins/losses;
- Jeffreys point probability;
- historical interval;
- historical EV;
- historical posterior threshold probability;
- early-vs-recent quantitative comparisons.

Therefore version 1.0 maintenance screens MUST NOT expose quantitative historical direction information.

Maintenance may show non-directional information such as:

- character;
- current regime number;
- regime start time;
- regime reason;
- included sample count.

Version 1.0 does NOT provide the previously considered quantitative History Health Check.

---

# 8. Subjective Probability Input

User input:

`x ∈ {0,1,...,100}`

Store:

`p_h_raw = x`

Mathematical probability:

p =
- 0.01 when x=0
- x/100 when 1<=x<=99
- 0.99 when x=100

Raw 0 and 100 MUST remain stored unchanged.

UI should indicate that raw 0/100 use 1%/99% for mathematical calculation.

---

# 9. Subjective Uncertainty Model

d(p):

- ln(1.5), for 0.01 <= p <= 0.45
- ln(1.5) + ((p-0.45)/0.10) * (ln2-ln1.5), for 0.45 < p < 0.55
- ln2, for 0.55 <= p <= 0.85
- ln2 - ((p-0.85)/0.10) * (ln2-ln1.4), for 0.85 < p < 0.95
- ln1.4 - ((p-0.95)/0.04) * (ln1.4-ln1.2), for 0.95 <= p <= 0.99

Define:

`z = ln(p/(1-p))`

`p_min = sigmoid(z-d(p))`

`p_max = sigmoid(z+d(p))`

`sigmoid(t) = 1/(1+exp(-t))`

The interval is a:

**user-specific subjective uncertainty interval**

It is NOT a statistical confidence interval.

Version 1.0 MUST NOT automatically learn or modify this function.

---

# 10. Historical Model Eligibility

Historical model for a character reads only rows satisfying all:

- same `character_id`;
- same current active `history_regime_id`;
- `status='completed'`;
- `include_character_history=1`.

It MUST NOT use another character's data.

---

# 11. Jeffreys Historical Model

Let:

- `w` = eligible wins;
- `l` = eligible losses;
- `n=w+l`.

If `n=0`:

- `history_model_status='no_history'`;
- point probability NULL;
- interval NULL;
- ready false.

Do NOT fabricate 50%.

For `n>=1`:

`theta | D ~ Beta(w+0.5,l+0.5)`

Point estimate:

`p_hist=(w+0.5)/(n+1)`

95% equal-tailed Jeffreys interval:

`L=BetaPPF(0.025,w+0.5,l+0.5)`

`U=BetaPPF(0.975,w+0.5,l+0.5)`

This is the:

**historical probability uncertainty interval**

not a next-result interval.

---

# 12. Statistical Readiness Gate

Historical line is valid only when:

`n>=20`

AND:

`U-L<=0.25`

If both true:

- status `valid`;
- ready true.

If n>=1 but Gate fails:

- status `insufficient`;
- internal model remains calculable and storable;
- ready false.

Gate is recalculated whenever eligible history changes.

A model may move:

- insufficient -> valid;
- valid -> insufficient.

Gate MUST NOT inspect subjective probability.

Gate does not prove predictive accuracy.

---

# 13. History Regimes

Every character starts with exactly one active regime:

`regime_number=1`

Normal application invariant:

- every active character has exactly one active regime.

Database partial uniqueness enforces at most one.

Application invariant checks enforce at least one.

Starting a new regime:

1. is allowed only when no pending round exists;
2. closes old active regime;
3. creates next numbered regime;
4. creates zero `character_stats`;
5. preserves all old regime data;
6. restarts current Gate from no history.

No automatic regime switching exists in 1.0.

---

# 14. Reference History

`reference_history` controls **display only**.

After every successful Calculate, regardless of whether `reference_history` is true or false, the application MUST:

1. calculate the then-current historical snapshot;
2. persist that snapshot.

Display rules:

- false / any status -> subjective only
- true / no_history -> subjective + nonnumeric no-history message
- true / insufficient -> subjective + nonnumeric insufficient-history message
- true / valid -> subjective + independent historical line

Concrete historical values MUST NOT leak for false/no_history/insufficient cases.

---

# 15. History Exposure

Store:

- `history_exposed`
- `history_exposed_at`

Quantitative history counts as exposed only when actual directional numerical historical information is released, e.g.:

- historical probability;
- historical interval;
- historical EV;
- threshold posterior probability.

Messages such as:

- “no history”;
- “history insufficient”

do NOT count as exposure.

If:

- `reference_history=true`;
- status=`valid`;

the application MUST commit:

- `history_exposed=1`;
- first exposure timestamp;

before the UI receives the historical numerical values.

Exposure is irreversible as an audit fact.

Once true, it remains true even if a later pending revision changes `reference_history` to false.

`history_exposed_at` records the FIRST exposure time and MUST NOT be overwritten later.

---

# 16. Future-Data Leakage

Prediction for round t MUST use only data available before round t.

`p_t = f(D_1,...,D_(t-1))`

Current round result MUST NOT enter its current historical prediction.

Every historical snapshot stores:

- wins;
- losses;
- sample size;
- model version;
- gate version;
- regime ID;
- data-through timestamp;
- last included historical round ID.

UUID values MUST NOT be treated as chronological ordering keys.

Once a round becomes completed or voided, its saved analysis snapshot is permanently frozen.

Later correction of historical facts MUST NOT rewrite an older prediction snapshot.

---

# 17. Pending Snapshot Revision Boundary

A pending prediction is editable only through the explicit:

`Modify -> Recalculate`

workflow.

Before successful Recalculate:

- edits exist only in memory;
- committed pending record and snapshot remain untouched.

Successful Recalculate:

- uses the SAME round ID;
- updates the same snapshot row;
- increments `revision_count`;
- updates `calculated_at`;
- updates `last_updated_at`.

`created_at` never changes.

If history had already been exposed, its first exposure timestamp remains unchanged.

After the round becomes completed or voided:

**analysis snapshot is permanently immutable**

No later correction or migration may recalculate it in place.

---

# 18. Subjective Independence Audit

If quantitative history has already been exposed and a later successful revision changes:

- `character_id`; or
- `p_h_raw`;

then:

`subjective_independence_compromised = 1`

This flag is irreversible.

Changing only odds does not automatically set this flag.

---

# 19. Excluded / Special Rounds

`include_character_history=0` means:

- the round is fully stored;
- result remains stored;
- snapshot remains stored;
- it does not change normal `character_stats`;
- it does not enter normal historical `w/l/n`;
- it must not indirectly alter normal live probability via automatic learning.

Principle:

**saved != included in the normal historical model**

---

# 20. Odds Validation

Odds are gross return multipliers including principal.

For each parsed multiplier R:

`R>=1`

AND:

`isfinite(R)=true`

Reject:

- R<1;
- NaN;
- +infinity;
- -infinity.

UI accepts ordinary decimal notation only.

Scientific notation is rejected.

Application uses binary64 float.

---

# 21. Break-Even Thresholds

`q_W=1/R_W`

`q_L=1/R_L`

Lose-side favorable threshold expressed as streamer-win probability:

`p < 1 - 1/R_L`

No-action baseline:

`EV_0=0`

---

# 22. Subjective EV

Win:

`EV_W,c = p*R_W - 1`

`EV_W,min = p_min*R_W - 1`

`EV_W,max = p_max*R_W - 1`

Lose:

`EV_L,c = (1-p)*R_L - 1`

`EV_L,min = (1-p_max)*R_L - 1`

`EV_L,max = (1-p_min)*R_L - 1`

---

# 23. Subjective Robust-Margin Index

`S_W = [logit(p)-logit(1/R_W)] / d(p)`

`S_L = [logit(1-p)-logit(1/R_L)] / d(p)`

Lose-side denominator MUST remain `d(p)`.

Official name:

**subjective robust-margin index**

It is not:

- z-score;
- confidence;
- success probability;
- stake fraction.

If R=1:

- S=NULL;
- EV remains calculable.

---

# 24. Floating Boundaries

Use:

`epsilon=1e-12`

Never use direct floating-point equality for analytical thresholds.

---

# 25. Odds Combination Status

Let:

`Q=q_W+q_L`

If:

`abs(Q-1)<=epsilon`

-> `critical`

If:

`Q>1+epsilon`

-> `normal_overlap`

If:

`Q<1-epsilon`

-> `double_positive_window`

For `double_positive_window`, warn that the input/multiplier timing should be checked.

Do not automatically choose a side.

---

# 26. EV-State Classification

For each side:

If:

`EV_min>epsilon`

-> `robust_positive`

If:

`EV_max<-epsilon`

-> `robust_negative`

Otherwise:

-> `crosses_threshold`

---

# 27. Historical EV

When history is valid:

`EV_hist_W,c = p_hist*R_W - 1`

`EV_hist_L,c = (1-p_hist)*R_L - 1`

Win interval:

`[L*R_W-1, U*R_W-1]`

Lose interval:

`[(1-U)*R_L-1, (1-L)*R_L-1]`

---

# 28. Historical Posterior Threshold Probability

Win:

`C_W = 1 - F_Beta(1/R_W; w+0.5,l+0.5)`

Lose:

`C_L = F_Beta(1-1/R_L; w+0.5,l+0.5)`

Official meaning:

**historical posterior probability of exceeding the break-even threshold**

Do NOT merge this value with subjective S.

---

# 29. Subjective / Historical Relation

For each side independently:

- both robust positive -> `agreement_positive`
- both robust negative -> `agreement_negative`
- one robust positive and one robust negative -> `conflict`
- either crosses threshold -> `uncertain`
- historical unavailable -> `history_unavailable`

The two probabilities are never fused.

---

# 30. Long-Term Evaluation

Model performance is separate from Gate readiness.

Evaluation may later use:

`BS=(1/N)*sum((p_i-y_i)^2)`

and calibration analysis.

Version 1.0 evaluation does not automatically change live models.

---

# 31. Persistent Round States

Allowed database states:

- `pending`
- `completed`
- `voided`

Normal flow:

`pending -> completed`

or:

`pending -> voided`

No transition back to pending is allowed.

Special historical correction may perform:

`completed -> voided`

but still never returns that record to pending.

---

# 32. Workflow States

Application/UI may use:

- `DRAFT`
- `CALCULATING`
- `PENDING_LOCKED`
- `PENDING_EDIT`
- `CONFIRM_SAVE`
- `COMPLETING`
- `RECOVERY`
- `RECOVERY_ERROR`
- `COMPLETED_NOTICE`

These are not persisted as round statuses.

---

# 33. DRAFT

DRAFT has:

- no round ID;
- no database round.

User may select:

- character;
- reference-history choice;
- subjective probability;
- odds.

Draft may be lost on crash.

---

# 34. Calculate

Calculate performs:

1. validation;
2. subjective calculation;
3. prior-history acquisition;
4. historical snapshot calculation;
5. EV/threshold analysis;
6. UUID generation;
7. transactional insert of pending round + snapshot;
8. commit;
9. display official analysis.

Official analysis MUST NOT be displayed before COMMIT succeeds.

---

# 35. Pending Edit

Modify uses the same round ID.

Edited values remain memory-only until Recalculate commits successfully.

Crash before Recalculate restores the previous locked state.

---

# 36. Post-Run Selection

While pending, user chooses:

- result;
- include/not include history.

Before Confirm Save these remain in memory only.

---

# 37. Final Save

Final save transaction updates together:

- result;
- include decision;
- completed timestamp;
- status;
- required character stats.

All commit together or all roll back.

---

# 38. Backup Failure After Save

Main-database successful COMMIT means the round is completed.

Subsequent backup failure MUST NOT revert it.

---

# 39. Void

Pending may be voided after confirmation.

Required fields:

- `voided_at`;
- optional `void_reason`.

No physical deletion.

---

# 40. Historical Correction Workflow

Historical correction exists only for correcting POST-RUN FACTS.

Allowed corrected facts:

- `result`;
- `include_character_history`.

It MUST NOT be used to retroactively change:

- character;
- subjective probability;
- odds;
- reference-history selection;
- analysis snapshot.

Historical correction is prohibited while a pending round exists.

Workflow:

1. select an existing completed round A;
2. create and verify `pre_history_correction` Safety Backup;
3. obtain corrected result/include decision;
4. start one transaction;
5. change A from completed to voided;
6. set A `voided_at`;
7. set nonempty A `void_reason`;
8. create new UUID round B with `status='completed'`;
9. set `B.supersedes_round_id=A.round_id`;
10. copy A's pre-run facts;
11. copy A's analysis snapshot exactly except for new `round_id`;
12. preserve A's original `calculated_at`;
13. use correction time for B `created_at`, `last_updated_at`, and `completed_at`;
14. store corrected result/include fields in B;
15. rebuild affected `character_stats` from `rounds`;
16. commit;
17. generate Recent backup.

A's original snapshot remains unchanged.

If a completed record has an incorrect character, subjective probability, or odds, the application MUST NOT fabricate a replacement prediction after the fact.

Such a record may be voided with an explanatory reason, but a fake corrected prediction MUST NOT be created.

Correction chains are permitted:

`A -> B -> C`

Branching is prohibited.

---

# 41. Recovery

Startup:

- 0 pending -> DRAFT
- 1 pending -> RECOVERY
- >1 pending -> RECOVERY_ERROR

Continue restores the SAME round ID and committed snapshot.

Do not generate a replacement pending.

---

# 42. Multiple-Pending Invariant Violation

The database should normally make multiple pending rows impossible.

If external corruption or unsupported manual changes cause >1 pending:

- treat it as a special recoverable invariant violation;
- route to `RECOVERY_ERROR`;
- do not silently select one;
- record a warning/error in logs.

This special path takes precedence over generic invariant-failure handling.

---

# 43. Main Window

Single main window.

Left:

- fixed 17x2 character matrix.

Right:

1. pre-run;
2. analysis;
3. post-run.

Left matrix must not move when analysis contents change.

---

# 44. First-Run UI Defaults

Fresh database:

- no character preselected;
- no history-reference option preselected.

After the user explicitly chooses these once, subsequent new rounds may retain:

- previous selected character;
- previous reference-history preference.

---

# 45. Subjective Input UI

Accept:

- integers 0–100 only.

Show fixed `%` label.

Enter MUST NOT trigger Calculate.

---

# 46. Odds UI

Two large decimal fields.

Reject:

- scientific notation;
- malformed decimal;
- non-finite value;
- value <1.

Store raw text and parsed float.

---

# 47. Historical UI

Before subjective lock:

- no quantitative history anywhere in application.

After successful Calculate:

- false reference -> no numerical history;
- no_history -> nonnumeric message;
- insufficient -> nonnumeric message;
- valid + reference -> numerical independent historical line.

---

# 48. Maintenance / Regime Page

Version 1.0 maintenance page may show:

- character;
- active regime number;
- regime start time;
- regime reason;
- included sample count.

It MUST NOT show:

- wins;
- losses;
- historical win rate;
- Jeffreys probability;
- historical interval;
- early-vs-recent performance;
- any other directional quantitative historical metric.

This restriction prevents pre-input anchoring.

---

# 49. Start New Regime

Allowed only with no pending round.

Use in-page confirmation.

Optional reason.

Transaction:

- close old regime;
- create new regime;
- create zero stats.

After commit:

- create Recent backup.

---

# 50. Save Confirmation UI

Result and inclusion decision are both required.

Use in-page:

- Back;
- Confirm Save.

No unnecessary modal summary.

---

# 51. Close Behavior

DRAFT:

- close directly.

PENDING_LOCKED:

- may close;
- recover later.

PENDING_EDIT:

- warn uncommitted edits will be lost;
- committed pending remains safe.

Unsaved post-run selection:

- warn result is not yet persisted;
- pending remains recoverable.

---

# 52. Single Instance

Use `QLockFile` or equivalent.

Second instance:

- informs user application is already running;
- exits.

Stale lock must be recoverable when owning process is no longer alive.

---

# 53. Error Levels

Input error:

- inline field feedback.

Business-state error:

- nonmodal banner.

Nonfatal operational warning:

- warning banner.

Startup/data-safety error:

- dedicated recovery/startup page.

Raw traceback is never shown in normal UI.

---

# 54. Error IDs

Unexpected errors receive an identifier.

UI:

- readable message;
- error ID.

Log:

- same ID;
- full traceback.

---

# 55. Persistent Paths

`%LOCALAPPDATA%\ProbabilityCalibrationTool\`

Subdirectories:

- `data/probability.db`
- `backups/recent/`
- `backups/daily/`
- `backups/safety/`
- `logs/app.log`
- `runtime/application.lock`

---

# 56. Backup Categories

Recent:

- retain exactly latest 5 valid Recent snapshots;
- trigger after successful round completion, round void, regime switch, historical correction;
- do not create on every pending Calculate.

Daily:

- one valid snapshot per local calendar day;
- retain latest 7 different dates.

Safety:

- retain latest 10 valid Safety snapshots;
- used for pre-migration, pre-restore, pre-history-correction;
- independent rotation.

---

# 57. Backup Creation

Use SQLite Online Backup API.

Order:

1. create candidate backup;
2. `PRAGMA integrity_check`;
3. accept only if result=`ok`;
4. then rotate old backups.

Never delete an old valid backup before its replacement is verified.

---

# 58. Backup Failure

Recent/Daily failure:

- log;
- warning;
- do not undo successful main transaction.

Required Safety backup failure:

- abort dangerous operation.

---

# 59. Startup Sequence

1. establish persistent directories;
2. initialize logging;
3. acquire single-instance lock;
4. open or create DB;
5. configure SQLite connection;
6. full integrity check;
7. read `user_version`;
8. migrate if required;
9. run application invariant checks;
10. detect special multiple-pending condition;
11. validate/rebuild stats;
12. create Daily backup if required;
13. route to DRAFT / RECOVERY / RECOVERY_ERROR.

---

# 60. SQLite PRAGMAs

Every connection MUST ensure:

- `PRAGMA foreign_keys = ON;`
- `PRAGMA journal_mode = DELETE;`
- `PRAGMA synchronous = EXTRA;`

---

# 61. Migration

For supported older schema:

1. integrity check;
2. verified pre-migration Safety backup;
3. transaction;
4. explicit ordered migration;
5. update `user_version` only after migration succeeds;
6. commit;
7. integrity check again.

Failure:

- rollback;
- old DB remains usable.

If DB schema is newer than app supports:

- prohibit writing;
- require newer application.

---

# 62. Normal Restore

Normal restore requires no pending round.

Workflow:

1. validate candidate integrity;
2. inspect candidate schema;
3. copy candidate to temporary restore DB;
4. migrate temporary DB if necessary;
5. create verified current-main `pre_restore` Safety backup;
6. close live connection;
7. atomically replace live DB;
8. reopen;
9. integrity/invariant checks;
10. route to RECOVERY if restored DB contains pending.

Migrating the temporary restore copy does NOT require another pre-migration Safety backup because the original backup file remains unchanged.

---

# 63. Emergency Restore

If live DB:

- cannot open; or
- fails integrity check;

normal workflow must not start.

Emergency Recovery Page may restore a verified Recent/Daily/Safety backup.

Because the current DB is already damaged, Emergency Restore is an explicit exception to the normal requirement that the current database first produce a verified `pre_restore` snapshot.

Before replacement, the application SHOULD make a best-effort raw copy of the damaged DB into a quarantine/safety location for diagnosis.

That quarantine copy:

- is explicitly marked unverified/corrupt;
- is NOT treated as a valid backup;
- does not need to pass integrity check.

Only the replacement candidate must be verified.

---

# 64. Time Storage

All persisted timestamps use UTC ISO-8601 TEXT.

Example:

`2026-08-30T11:23:45.123456Z`

UI converts to local time for display.

---

# 65. Database Tables

Exactly six core tables:

1. `characters`
2. `history_regimes`
3. `rounds`
4. `round_analysis_snapshots`
5. `character_stats`
6. `meta`

---

# 66. `characters`

Columns:

- `character_id INTEGER PRIMARY KEY CHECK(character_id BETWEEN 1 AND 34)`
- `internal_code TEXT NOT NULL UNIQUE`
- `display_name TEXT NOT NULL`
- `tainted INTEGER NOT NULL CHECK(tainted IN (0,1))`
- `pair_row INTEGER NOT NULL CHECK(pair_row BETWEEN 1 AND 17)`
- `active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))`

Constraint:

`UNIQUE(pair_row, tainted)`

Seed exactly the 34 identities defined in Section 6.

---

# 67. `history_regimes`

Columns:

- `regime_id TEXT PRIMARY KEY`
- `character_id INTEGER NOT NULL`
- `regime_number INTEGER NOT NULL CHECK(regime_number >= 1)`
- `started_at TEXT NOT NULL`
- `ended_at TEXT NULL`
- `active INTEGER NOT NULL CHECK(active IN (0,1))`
- `reason TEXT NULL`

Constraints:

- FK `character_id -> characters`;
- `UNIQUE(character_id, regime_number)`;
- `UNIQUE(character_id, regime_id)`;
- active=1 implies ended_at NULL;
- active=0 implies ended_at non-NULL.

Partial unique index:

- maximum one active regime per character.

Application invariant:

- every active character must have one active regime.

---

# 68. `rounds`

Columns:

- `round_id TEXT PRIMARY KEY`
- `created_at TEXT NOT NULL`
- `calculated_at TEXT NOT NULL`
- `last_updated_at TEXT NOT NULL`
- `completed_at TEXT NULL`
- `voided_at TEXT NULL`
- `void_reason TEXT NULL`
- `character_id INTEGER NOT NULL`
- `history_regime_id TEXT NOT NULL`
- `reference_history INTEGER NOT NULL CHECK(reference_history IN (0,1))`
- `p_h_raw INTEGER NOT NULL CHECK(p_h_raw BETWEEN 0 AND 100)`
- `win_odds_raw TEXT NOT NULL`
- `lose_odds_raw TEXT NOT NULL`
- `win_odds REAL NOT NULL CHECK(win_odds >= 1.0 AND win_odds <= 1.7976931348623157e308)`
- `lose_odds REAL NOT NULL CHECK(lose_odds >= 1.0 AND lose_odds <= 1.7976931348623157e308)`
- `status TEXT NOT NULL CHECK(status IN ('pending','completed','voided'))`
- `revision_count INTEGER NOT NULL DEFAULT 0 CHECK(revision_count >= 0)`
- `result INTEGER NULL CHECK(result IS NULL OR result IN (0,1))`
- `include_character_history INTEGER NULL CHECK(include_character_history IS NULL OR include_character_history IN (0,1))`
- `history_exposed INTEGER NOT NULL DEFAULT 0 CHECK(history_exposed IN (0,1))`
- `history_exposed_at TEXT NULL`
- `subjective_independence_compromised INTEGER NOT NULL DEFAULT 0 CHECK(subjective_independence_compromised IN (0,1))`
- `supersedes_round_id TEXT NULL`

Foreign keys:

- `character_id -> characters(character_id)`
- composite `(character_id, history_regime_id) -> history_regimes(character_id, regime_id)`
- `supersedes_round_id -> rounds(round_id)`

Checks:

- self-supersede prohibited;
- exposure timestamp consistent with exposure flag;
- state fields consistent with round status.

---

# 69. Round-State Constraints

Pending:

- result NULL;
- include decision NULL;
- completed_at NULL;
- voided_at NULL;
- void_reason NULL.

Completed:

- result non-NULL;
- include decision non-NULL;
- completed_at non-NULL;
- voided_at NULL;
- void_reason NULL.

Voided:

- voided_at non-NULL.

A voided record may retain completed result/include/completed_at if it was previously completed and then voided by correction.

---

# 70. Pending Unique Index

Database MUST enforce at most one pending row.

Use a partial unique index equivalent to:

`CREATE UNIQUE INDEX ... ON rounds(status) WHERE status='pending';`

---

# 71. Supersede Unique Index

Database MUST enforce:

- one old round has at most one direct replacement.

Use unique partial index on:

`supersedes_round_id`

where non-NULL.

---

# 72. `round_analysis_snapshots`

Exactly one current locked snapshot per round.

Columns include:

Identity:

- `round_id TEXT PRIMARY KEY`

Subjective:

- `p_h_used INTEGER NOT NULL CHECK(p_h_used BETWEEN 1 AND 99)`
- `subjective_probability REAL NOT NULL CHECK(subjective_probability BETWEEN 0 AND 1)`
- `subjective_p_min REAL NOT NULL CHECK(subjective_p_min BETWEEN 0 AND 1)`
- `subjective_p_max REAL NOT NULL CHECK(subjective_p_max BETWEEN 0 AND 1)`
- `subjective_logit_half_width REAL NOT NULL CHECK(subjective_logit_half_width > 0)`
- `subjective_model_version INTEGER NOT NULL CHECK(subjective_model_version >= 1)`

Require:

`subjective_p_min < subjective_probability < subjective_p_max`

Odds / EV:

- `odds_analysis_version INTEGER NOT NULL CHECK(odds_analysis_version >= 1)`
- `break_even_win REAL NOT NULL CHECK(break_even_win BETWEEN 0 AND 1)`
- `break_even_lose_event REAL NOT NULL CHECK(break_even_lose_event BETWEEN 0 AND 1)`
- `break_even_lose_as_win_probability REAL NOT NULL CHECK(break_even_lose_as_win_probability BETWEEN 0 AND 1)`
- subjective win EV center/min/max
- subjective lose EV center/min/max
- nullable subjective win/lose margin index
- subjective win/lose EV state
- odds combination status

Historical:

- `history_model_status`
- `history_statistically_ready`
- history wins/losses/sample size
- history model/gate versions
- nullable history probability/lower/upper
- `history_data_through_at TEXT NOT NULL`
- nullable last included historical round ID
- nullable historical win/lose EV fields
- nullable threshold posterior probabilities
- win/lose model relation

Foreign keys:

- `round_id -> rounds(round_id)`
- last included historical round -> rounds(round_id)

Invariant:

`history_sample_size = history_wins + history_losses`

All enum fields MUST have explicit SQLite CHECK constraints using the exact values defined by this SPEC.

---

# 73. Historical Snapshot Null Rules

`no_history`:

- n=0;
- wins=0;
- losses=0;
- ready=0;
- probability/lower/upper NULL;
- last included round NULL;
- historical EV NULL;
- posterior threshold NULL;
- relations=`history_unavailable`.

`insufficient`:

- n>=1;
- probability/lower/upper non-NULL;
- ready=0;
- historical EV/posterior NULL;
- relations=`history_unavailable`.

`valid`:

- n>=1;
- probability/lower/upper non-NULL;
- ready=1;
- historical EV/posterior non-NULL;
- relations not `history_unavailable`.

Probability/interval/posterior values lie within [0,1].

---

# 74. `character_stats`

Columns:

- `character_id INTEGER NOT NULL`
- `regime_id TEXT NOT NULL`
- `included_games INTEGER NOT NULL DEFAULT 0 CHECK(included_games >= 0)`
- `wins INTEGER NOT NULL DEFAULT 0 CHECK(wins >= 0)`
- `losses INTEGER NOT NULL DEFAULT 0 CHECK(losses >= 0)`
- `last_included_round_id TEXT NULL`
- `updated_at TEXT NOT NULL`
- `stats_version INTEGER NOT NULL CHECK(stats_version >= 1)`

Primary key:

`(character_id, regime_id)`

Composite FK:

`(character_id, regime_id) -> history_regimes(character_id, regime_id)`

Optional FK:

`last_included_round_id -> rounds(round_id)`

Invariant:

`included_games = wins + losses`

If included_games=0:

- last included round NULL.

If included_games>0:

- last included round non-NULL.

---

# 75. Stats Cache Versioning

Current:

`STATS_VERSION=1`

Before trusting cache:

- stats version must equal application version.

Mismatch or count disagreement:

- rebuild from eligible source-of-truth rounds;
- write current version.

`rounds` remains source of truth.

---

# 76. `meta`

Columns:

- `key TEXT PRIMARY KEY`
- `value TEXT NOT NULL`
- `updated_at TEXT NOT NULL`

Schema version remains solely:

`PRAGMA user_version`

---

# 77. Database Initialization

Atomic initialization:

1. create schema;
2. indexes;
3. seed exact 34 characters;
4. create regime1 for each;
5. create zero stats;
6. metadata;
7. set `user_version=1`;
8. commit.

Failure rolls back all.

---

# 78. Required Indexes

At minimum:

- unique `(pair_row, tainted)`
- active-regime partial unique
- pending partial unique
- supersedes partial unique
- `rounds(calculated_at)`
- history rebuild index by character/regime/calculated time, preferably partial for completed+included rows.

---

# 79. Deletion Policy

Normal application workflows MUST NOT physically delete:

- rounds;
- history regimes;
- completed audit history.

Use statuses, supersede relations, inactive regimes.

Foreign keys should generally use RESTRICT.

---

# 80. Data Semantics

Source-of-truth:

- characters
- history_regimes
- rounds

Recorded prediction output:

- round_analysis_snapshots

Rebuildable cache:

- character_stats

Metadata:

- meta

---

# 81. Test Isolation

Every automated test must use temporary:

- DB;
- backups;
- logs;
- runtime directories.

Tests MUST NEVER touch real LocalAppData user data.

---

# 82. Subjective Golden Tests

At minimum:

| raw | used | lower approx | upper approx |
|---:|---:|---:|---:|
| 0 | 1 | 0.0066889632 | 0.0149253731 |
| 1 | 1 | 0.0066889632 | 0.0149253731 |
| 40 | 40 | 0.3076923077 | 0.5000000000 |
| 45 | 45 | 0.3529411765 | 0.5510204082 |
| 50 | 50 | 0.3660254038 | 0.6339745962 |
| 55 | 55 | 0.3793103448 | 0.7096774194 |
| 75 | 75 | 0.6000000000 | 0.8571428571 |
| 85 | 85 | 0.7391304348 | 0.9189189189 |
| 90 | 90 | 0.8432240348 | 0.9377330360 |
| 95 | 95 | 0.9313725490 | 0.9637681159 |
| 99 | 99 | 0.9880239521 | 0.9916527546 |
| 100 | 99 | 0.9880239521 | 0.9916527546 |

Test continuity at:

- 45
- 55
- 85
- 95

For all used 1–99%:

`0 < p_min < p < p_max < 1`

---

# 83. Historical Golden Tests

n=0:

- no_history
- probability NULL
- Gate false

1 win / 0 losses:

- point=0.75
- interval approx [0.1467463163,0.9996144190]
- Gate false

18 wins / 2 losses:

- point approx 0.8809523810
- interval width approx 0.2624807693
- Gate false

19 wins / 1 loss:

- point approx 0.9285714286
- width approx 0.2053696037
- Gate true

20 wins / 0 losses:

- point approx 0.9761904762
- width approx 0.1166147364
- Gate true

50 wins / 50 losses:

- point=0.5
- interval approx [0.4031739509,0.5968260491]
- Gate true

Reasonable numerical tolerance such as approximately `1e-10`.

---

# 84. Golden-Test Governance

Codex MUST NOT modify Golden expected values merely to make implementation pass.

They change only after explicit SPEC/model-version revision.

---

# 85. EV/Odds Tests

Cover:

- R<1 rejection
- NaN rejection
- infinity rejection
- R=1 safe
- critical
- normal_overlap
- double_positive_window
- epsilon boundary

R=1:

- EV works
- break-even=1
- S=NULL
- no crash

---

# 86. Schema Constraint Tests

Temporary real SQLite must reject:

- duplicate round ID
- multiple pending
- duplicate active regime
- mismatched character/regime
- illegal probability
- illegal result
- illegal enum values
- completed missing required facts
- pending with completed timestamp
- stats arithmetic mismatch
- self-supersede
- multiple direct replacements

Initialization verifies:

- 34 characters
- exact seed identities
- 34 regime1
- 34 zero stats
- user_version=1

---

# 87. Transaction Tests

Failure injection must prove all-or-nothing behavior.

Example:

- round completion update succeeds
- stats operation fails

Expected:

- entire transaction rollback.

---

# 88. Stats-Rebuild Test

Source truth:

- 20 games
- 16 wins
- 4 losses

Corrupt stats cache.

Startup validation rebuilds to:

- 20
- 16
- 4

and logs warning.

Also test stats_version mismatch.

---

# 89. State-Machine Tests

Cover:

- DRAFT -> PENDING -> COMPLETED
- PENDING -> VOIDED
- no completed/voided -> pending
- repeated completion rejected

---

# 90. Crash Tests

Calculate failure before commit:

- no pending.

Commit then process death:

- RECOVERY restores same round.

Final save failure before commit:

- pending remains.

Completed commit then backup failure:

- completed remains.

---

# 91. Exposure Tests

A:
- reference false
- internal history valid
- snapshot stored
- exposure false
- no numerical history visible

B:
- reference true
- valid
- exposure committed before release
- first timestamp retained

C:
- exposed
- odds-only change
- independence may remain false

D:
- exposed
- subjective probability or character change
- independence becomes permanently true

E:
- later reference false
- exposure stays true

F:
- no_history/insufficient message
- exposure stays false

---

# 92. Pending-Edit Crash Test

Modify without Recalculate, then crash.

Recovery restores previous committed inputs and snapshot.

---

# 93. Regime Tests

Current active regime only contributes history.

New regime:

- preserves old
- closes old
- creates new
- zero stats
- no_history
- Recent backup

Pending blocks switch.

Maintenance does not expose directional history.

---

# 94. Special-Rule Test

Completed excluded round:

- stored
- result retained
- snapshot retained
- stats unchanged
- future history excludes it

---

# 95. Leakage Test

Before round21:

- history 19/1
- snapshot n=20

After round21 win:

- live n=21
- round21 snapshot remains n=20 forever

Later correction does not rewrite it.

---

# 96. Historical Correction Test

A completed.

Correction:

- verified safety backup
- A voided
- B corrected completed
- B supersedes A
- B preserves prediction time and analysis
- only post-run facts corrected
- stats rebuilt

Verify:

- A remains
- A snapshot unchanged
- B snapshot copied except round ID
- no branch replacement
- A->B->C allowed

Attempted correction of character/p_h/odds must be rejected as correction workflow.

---

# 97. Backup Tests

Recent:

- latest 5 valid
- new verified before old deletion
- failed new backup preserves old five

Daily:

- one per local date
- latest 7 dates

Safety:

- latest 10 valid
- independent rotation

---

# 98. Migration Tests

Each migration:

- old DB
- integrity
- safety backup
- transaction
- migration
- version update
- data preserved

Failure:

- rollback
- old version remains
- backup remains

Newer unsupported schema:

- writing prohibited

---

# 99. Restore Tests

Normal:

- verify candidate
- temp copy
- temp migration
- pre_restore safety
- atomic replacement
- reopen/check

Corrupt candidate:

- current DB untouched

Restored DB with pending:

- RECOVERY

Emergency:

- damaged live DB does not require verified pre_restore
- optional quarantine copy is unverified
- only verified backup can replace live DB

---

# 100. UI Smoke Tests

Verify:

- window creation
- 34 character buttons
- correct 17x2 mapping
- mutually exclusive selections
- Enter does not Calculate
- inline invalid input
- Calculate locks inputs
- completed resets correct fields
- no history leak for reference=false
- no history leak for insufficient/no_history
- maintenance contains no directional quantitative history

---

# 101. DPI Manual Acceptance

Test Windows:

- 125%
- 150%

Release blocking if:

- overlap
- critical clipping
- inaccessible character buttons
- inaccessible confirmation controls
- unintended workflow scrolling
- left character layout movement

---

# 102. Single-Instance Test

Instance A runs.

Instance B:

- cannot acquire lock
- informs user
- exits

Dead-process stale lock must recover.

---

# 103. Logging Test

Unexpected exception:

UI:
- friendly message
- error ID
- no traceback

Log:
- same ID
- complete traceback

Rotation obeys 2 MiB and five backups.

---

# 104. End-to-End Test

Minimum:

1. fresh launch
2. initialize DB
3. select character
4. no-reference
5. enter subjective
6. enter odds
7. Calculate
8. pending
9. close
10. restart
11. RECOVERY
12. Continue
13. result
14. include choice
15. Confirm Save
16. completed
17. Recent backup
18. new DRAFT

Then accumulate history until valid and test reference=true:

- exposure committed
- history appears only after subjective lock

---

# 105. Performance Smoke

Generate at least 100,000 synthetic rounds.

Verify correctness and absence of obvious:

- O(N^2) behavior
- unbounded memory growth

No arbitrary millisecond release threshold.

---

# 106. Test Severity

Release-blocking:

- Golden math
- schema
- transactions
- state machine
- exposure
- anti-anchoring
- leakage
- regimes
- correction
- backup
- migration
- restore
- recovery
- duplicate prevention
- E2E
- critical DPI

Minor cosmetic issues may be review-only.

---

# 107. Codex Phase Completion Report

Every implementation phase MUST report:

- files created
- files modified
- exact commands
- passed
- failed
- skipped
- Ruff
- incomplete work
- SPEC deviations or `none`
- known risks

Codex MUST NOT start the next phase automatically.

Failed tests must not be hidden with deletion/skip/xfail unless explicitly authorized.

---

# 108. Final 1.0 Release Gate

All required:

1. release-blocking tests pass
2. Ruff check passes
3. Ruff format check passes
4. no unexplained skip/xfail
5. fresh DB E2E
6. pending recovery E2E
7. backup/restore E2E
8. migration
9. correction
10. anti-anchoring
11. 100k smoke
12. Windows 125% DPI
13. Windows 150% DPI
14. PyInstaller onedir
15. packaged app outside PyCharm/.venv
16. packaged app completes full test round
17. packaged app survives close/reopen correctly
18. final `PRAGMA integrity_check` returns `ok`

---

# 109. Frozen Invariants

Without an explicit future SPEC revision:

- history is character-specific
- active regime only
- excluded data does not enter normal history
- current result never enters current prediction
- completed/voided snapshots never recalculate
- pending changes only via explicit Recalculate
- subjective/history never fuse
- Gate never reads subjective probability
- no quantitative history before subjective lock
- no directional quantitative history in maintenance
- every Calculate stores historical snapshot
- quantitative exposure is irreversible
- exposed_at is first exposure
- insufficient/no-history messages are not exposure
- rounds are source of truth
- stats are rebuildable/versioned cache
- UUID is round identity
- field similarity is not primary duplicate detection
- pending is durable before official analysis display
- normal audit history is never physically deleted
- old regimes remain
- dangerous migration/restore/correction requires verified Safety backup
- Emergency Restore is the explicit damaged-DB exception
- UI contains no math formulas/SQL implementation
- repositories do not independently commit
- non-finite odds are rejected
- Golden expected values cannot be changed merely to accommodate incorrect implementation

---

# 110. Out of Scope for 1.0

Not required:

- AI integration
- automatic concept-drift detection
- automatic regime changes
- quantitative History Health Check
- cross-character hierarchical modeling
- subjective/history fusion
- automatic subjective uncertainty modification
- complex statistics dashboard
- automated participation behavior
- stake sizing
- cloud sync
- multi-user
- server DB
- macOS/Linux distribution
- automatic deletion of old history
