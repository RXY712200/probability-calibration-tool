# Localization Step 7 Defect Log

Status: `MANUAL ACCEPTANCE NOT STARTED`

No manual visual execution has occurred. The empty table is intentional; absence of rows is not a claim that no defects exist.

| Defect ID | Severity | Checklist ID | Language | Scaling | Page/State | Description | Evidence | Owning Stage | Status | Resolution/Acceptance Rationale | Retest Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|

Allowed severity: `BLOCKER`, `HIGH`, `MEDIUM`, `LOW`.

Allowed status: `OPEN`, `ROUTED`, `FIXED_PENDING_RETEST`, `CLOSED`, `ACCEPTED_LOW`, `ACCEPTED_MEDIUM`.

## Routing rules

- Localization lifecycle or preference defects → Step 3.
- Presentation, layout, banner, focus, or geometry defects → Step 4.
- Translation or terminology defects → Step 5.
- Business or data behavior defects → the original Probability Calibration Tool 1.0 owning stage.
- A preparation-tool defect stays in Step 7 preparation and must not be presented as a frozen production defect.
- A frozen production defect blocks preparation completion: record it, identify the owning stage, and stop rather than opportunistically editing production.

## Evidence rules

Use project-relative screenshot paths. Retain raw Windows screenshots with enough page context and without AI modification or defect-concealing crops. Annotated copies are separate artifacts. Do not close a defect without a manual retest and retest evidence.
