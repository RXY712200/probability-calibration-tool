# Phase 7B manual acceptance — NOT EXECUTED

Every checkbox below is PENDING. Phase 7A process observations, offscreen tests and generated fixtures do not satisfy these manual gates. Do not mark final 1.0 acceptance until a human completes and records the checks against the final RC hash manifest. Distribute the entire onedir folder, never the EXE alone.

## Test setup and evidence

Use Windows 11 x64 and a dedicated PowerShell window. Record operator, date, Windows version, display resolution, scaling, RC SHA-256, process IDs and screenshots under this release evidence directory. No screenshots have been fabricated. Use only disposable isolated data roots; never point these steps at personal production data. Keep the same PowerShell window and environment for launches A/B/C.

Run from the project root (QA tooling uses uv; the packaged application does not):

```powershell
Set-Location -LiteralPath 'C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability'
$pctSmoke = Get-Content -Raw -LiteralPath outputs/release/packaged_smoke.json | ConvertFrom-Json
$pctExe = $pctSmoke.exe
if (-not (Test-Path -LiteralPath $pctExe)) { throw 'Restore the whole verified external RC folder first.' }
$pctOriginalLocal = $env:LOCALAPPDATA
$pctWorkflowLocal = Join-Path $env:TEMP ('PCT Phase7B Workflow ' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $pctWorkflowLocal -ErrorAction Stop
$env:LOCALAPPDATA = $pctWorkflowLocal
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
Remove-Item Env:VIRTUAL_ENV -ErrorAction SilentlyContinue
```

Launch manually using `& $pctExe` (visible app is intentional in this manual procedure). Record its exact PID in Task Manager. For every normal close use the window close control, answer the accepted close confirmation when shown, and verify that exact PID exits; do NOT terminate the process to pass a close gate. If exit fails, record FAIL and stop that workflow. Keep the controlled DB for diagnosis.

## Packaged full round and close/reopen Recovery (gates 16–17)

1. [ ] Launch A, observe fresh DRAFT. Select character 1, explicitly choose **Do not use history**, enter subjective `70`, Win odds `2.00`, Lose odds `3.00`, click **Calculate**.
2. [ ] Observe committed pending analysis and locked subjective inputs. Record displayed inputs, timestamp and subjective analysis. No historical numerical line may appear for reference=false. Close normally; verify PID A exits.
3. [ ] Launch B with the SAME `$pctWorkflowLocal`. Observe Recovery, not a new DRAFT. Inspect the shown facts without inventing a recalculation. Click explicit **Continue**. Verify the same prediction, timestamp, inputs and analysis.
4. [ ] Select **Win** and **Include** explicitly; inspect CONFIRM_SAVE, click **Confirm Save**, and observe COMPLETED_NOTICE. Verify a Recent backup now exists in `$pctWorkflowLocal\ProbabilityCalibrationTool\backups\recent`.
5. [ ] Click **New Round**, observe DRAFT, close normally and verify PID B exits.
6. [ ] Launch C on the same root: DRAFT, not Recovery. Close normally and verify PID C exits. No pending round must remain.

## Controlled history-valid packaged/SciPy path

Prepare a NEW separate test root. This helper uses 20 real production Calculate/complete operations, verifies 19 wins/1 loss in character 1/current regime, creates and checks Recent, and refuses an existing root. Preparation is not GUI acceptance.

```powershell
$pctHistoryLocal = Join-Path $env:TEMP ('PCT Phase7B History ' + [guid]::NewGuid())
uv run python -m tools.prepare_manual_history --localappdata "$pctHistoryLocal"
$env:LOCALAPPDATA = $pctHistoryLocal
& $pctExe
```

1. [ ] Confirm DRAFT and no quantitative history before locking. Select character 1, **Use history**, subjective `70`, Win `2.00`, Lose `3.00`, then **Calculate**.
2. [ ] Subjective inputs lock first. Historical numerical analysis must appear only after committed exposure; verify sample size 20 and the helper's Jeffreys center/bounds with the accepted display rounding. No SciPy DLL/import error or crash. Record a screenshot and log observations. Source regression already checks commit-before-render; do not claim a screenshot alone proves transaction order.
3. [ ] Close normally after resolving pending via the accepted complete or void workflow. Do not reuse this modified root as a fresh 19/1 fixture; create another new root when needed.

## Windows DPI (gates 12–13)

For **each** scale separately: **close all packaged app processes normally → change Windows Settings / System / Display / Scale to 125% or 150% → launch packaged app fresh**. Record actual Windows scale and resolution. Changing scale on an already-running process alone is insufficient. Use separate disposable workflow/history roots per scale, following the preparation commands above.

| State to inspect | 125% | 150% | How to reach with accepted UI |
|---|---|---|---|
| DRAFT | PENDING | PENDING | Fresh root or New Round |
| PENDING_LOCKED, maximum analysis | PENDING | PENDING | Verified 19/1 history; Use history; 70%, Win 2.00 / Lose 3.00; both models/sides and odds-combination warning visible |
| PENDING_EDIT | PENDING | PENDING | Separate no-reference pending → Modify; never bypass the exposed-history lock |
| CONFIRM_SAVE | PENDING | PENDING | Pending → explicit result and Include/Exclude |
| COMPLETED_NOTICE | PENDING | PENDING | Confirm Save |
| Maintenance | PENDING | PENDING | New Round/DRAFT → Maintenance |
| Regime confirmation | PENDING | PENDING | Select character → Start New Regime; inspect then Back/Cancel to preserve fixture |
| Correction | PENDING | PENDING | Completed controlled record → Correction browser/form; inspect confirmation without inventing pre-run correction capability |
| Restore | PENDING | PENDING | DRAFT → Restore, select valid controlled backup, inspect confirmation; cancel for layout-only inspection |
| Recovery | PENDING | PENDING | Close normally with a pending round → fresh launch same isolated root |

Blockers (apply to EVERY state at BOTH scales):

- [ ] No overlap.
- [ ] No critical clipping.
- [ ] All 34 character buttons accessible.
- [ ] All confirmation controls accessible.
- [ ] No unintended workflow scrolling.
- [ ] Left 17×2 character layout does not shift when right-side analysis changes.

Do not elevate cosmetic preferences to blockers. Recovery/administrative pages use their accepted layouts; do not demand nonexistent business controls. For maximum analysis, capture all visible model/side lines and the warning. No hidden numerical history may leak into Maintenance or Correction browser rows.

Expected screenshot names (create only from genuine manual observation):

- `release_dpi_125_draft.png`, `release_dpi_125_max_analysis.png`, `release_dpi_125_admin.png`
- `release_dpi_150_draft.png`, `release_dpi_150_max_analysis.png`, `release_dpi_150_admin.png`

Add state-specific screenshots such as `release_dpi_125_recovery.png` and `release_dpi_150_confirm_save.png` as needed. Record per-state operator observations; three pictures alone do not substitute for the complete matrix.

## Packaged single-instance manual confirmation

1. [ ] Start A on an isolated root; then start B with exactly the same LOCALAPPDATA.
2. [ ] B shows ALREADY_RUNNING notification, not a second normal business window. A remains valid.
3. [ ] Human dismisses B's modal and verifies PID B exits. Close A normally and verify exit.

Automated Phase 7A observes the lock and modal-only second instance but deliberately does not click the modal; full dismissal/exit remains PENDING.

## Final post-manual read-only integrity (gate 18)

Run ONLY after A/B/C passed and all packaged processes using the workflow root have closed. The verifier opens DBs with SQLite `mode=ro` plus `query_only=ON`; it never invokes startup, migration, stats repair or rebuild. Keep gate 18 PENDING until the actual final post-manual DB is checked.

```powershell
$pctFinalRoot = Join-Path $pctWorkflowLocal 'ProbabilityCalibrationTool'
$pctFinalDb = Join-Path $pctFinalRoot 'data\probability.db'
$pctRecent = Get-ChildItem -LiteralPath (Join-Path $pctFinalRoot 'backups\recent') -File -Filter '*.db' | Sort-Object Name -Descending | Select-Object -First 1
if ($null -eq $pctRecent) { throw 'FAIL: no Recent backup exists.' }
uv run python -m tools.release_verify --database "$pctFinalDb" --recent "$($pctRecent.FullName)" --final-manual --evidence outputs/release/phase7b_final_integrity.json
$env:LOCALAPPDATA = $pctOriginalLocal
```

Required: integrity `["ok"]`, no FK violations, user_version 1, pending 0, at least one completed round, matching round/snapshot totals, valid Recent backup. Nonzero verifier exit is FAIL, not permission to repair. Preserve and investigate failures separately.

Finally record human sign-off, exact RC inventory hash, evidence filenames and results in `FINAL_RELEASE_GATE_1.0.md`. Do not prefill PASS, change frozen business behavior, or release while any required gate is FAIL/PENDING.
