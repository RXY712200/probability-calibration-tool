# Phase 7A first build rejection and packaging correction

The first build completed, and its static file audit passed (346 files / 270,946,145 bytes), but the external packaged launch FAILED. This build is NOT the Release Candidate.

## Observed failure

The packaged process displayed `Unhandled exception in script`. A read-only WM_GETTEXT inspection of that child process's error dialog reported:

```text
Failed to execute script 'pyinstaller_entry' due to unhandled exception:
DLL load failed while importing QtWidgets: The specified procedure could not be found.
pyinstaller_entry.py:3 -> probability_calibration_tool/bootstrap.py:5
ImportError: DLL load failed while importing QtWidgets
```

The original localized Windows error was rendered with encoding replacement characters by the diagnostic console; the import traceback and procedure-not-found meaning were inspected. No product data initialized. Smoke's 60-second liveness guard timed out, exited 1, and terminated only its own saved child process. Two additional isolated read-only diagnostic launches captured the dialog; their own PIDs were terminated afterward. These were not normal GUI close/manual acceptance.

## Root cause (confirmed, not a guessed SciPy issue)

The first `Analysis-00.toc` contained:

```text
icuuc.dll <- C:\Users\rxy71\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\icuuc.dll
icudt78.dll <- C:\Users\rxy71\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\icudt78.dll
```

It also pulled unrelated libheif API-set DLLs from the inherited build-shell PATH. Poppler's ICU 78 is not the Windows ICU API imported by this locked Qt wheel. PE inspection found the Qt6Core import descriptor requires 20 ICU functions absent from that Poppler binary. All 20 exist in `C:\Windows\System32\icuuc.dll`. Installed PySide6 tests passed because their normal loader uses Windows ICU; the frozen bundle wrongly shadowed it.

A preliminary pefile export scan also over-reported some Qt exports because its default export-count cap is 8192; these were not treated as actual missing Qt symbols. The ICU export set is below that cap and the real Windows ICU comparison used max_symbol_exports=100000.

## Minimal correction

Only `packaging/ProbabilityCalibrationTool.spec` changes native discovery PATH to SystemRoot/System32 and SystemRoot before Analysis. Normal PyInstaller hooks still locate locked wheel libraries. No hidden imports, broad collect_all, runtime hook, production bootstrap change, source fix, new dependency or version downgrade. A focused spec-execution regression passes a poisoned Poppler/developer PATH and asserts Analysis receives only the intended Windows search paths and explicit project/src pathex.

After this fix, full pytest and both Ruff commands must pass before another clean build. See final command evidence and artifact audit for the eventual result; this note does not preclaim it.

## Rejected artifact preservation

Old build/ and dist/ were moved with exact resolved-target/reparse checks to:

```text
C:\Users\rxy71\AppData\Local\Temp\PCT Phase7A rejected build 20260831\build
C:\Users\rxy71\AppData\Local\Temp\PCT Phase7A rejected build 20260831\dist
```

The first failed external copy is also preserved at:

```text
C:\Users\rxy71\AppData\Local\Temp\Probability Calibration Tool RC 5f75pvcr\Probability Calibration Tool
```

Do not distribute or use these rejected paths for Phase 7B. No source or user data was deleted. Initial build logs/warnings and pre-fix pytest output are retained under outputs/release with failed/pre_packaging_fix names.

