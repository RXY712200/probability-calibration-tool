# Phase 7A final packaging audit

PASS for automated packaging/launch scope. Manual Phase 7B remains PENDING. The first rejected build is documented separately; only the final paths below are the RC.

## Final artifact

- Directory: `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\dist\ProbabilityCalibrationTool`
- EXE: `C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\dist\ProbabilityCalibrationTool\ProbabilityCalibrationTool.exe`
- 298 files; 223,928,257 bytes (213.55 MiB).
- EXE SHA-256: `d45ebba5acd758b05401c1bd6b146af815517605fe8dacb7426120d9b2baeaf1`.
- PE inspection: AMD64, PE32+, Windows GUI subsystem 2. Whole-folder onedir distribution; console=False.
- Every file's relative name, byte size and SHA-256 is retained in artifact_audit.json. The external copied inventory matches exactly before and after launch.

## Build configuration and provenance

Thin absolute-import adapter calls only the accepted bootstrap.main. Analysis explicitly resolves project/src from SPECPATH. COLLECT produces onedir with _internal runtime. No custom hidden imports/data/binaries, custom runtime hooks, collect_all, installer, signing or updater. This follows the [PyInstaller spec-file structure](https://pyinstaller.org/en/stable/spec-files.html).

PyInstaller 6.22.2 / hooks-contrib 2026.7, Python 3.13.14 AMD64, SciPy 1.18.1 and PySide6 6.11.2. Runtime dependency versions unchanged. Native DLL discovery PATH is constrained inside the spec to Windows/System32 and Windows; standard hooks still collect wheel binaries. This resolves the evidence-backed first-build Poppler ICU shadowing defect without modifying production sources.

Final build starts with build/ and dist/ absent and --clean. The 1013-test full regression and both Ruff checks passed BEFORE this build. 175 final source/config hashes were captured; post-build comparison shows no source changes. The 159 accepted source/test/SPEC baseline files are unchanged; only pyproject.toml, uv.lock and .gitignore changed among baseline files.

## Leakage and native runtime audit

No project/user DB, log, backup, lock, screenshot/report, project source/test tree, pytest/Ruff cache or .venv directory is in the artifact. Legitimate vendor runtime names are allowed. The final analysis contains 2028 records, 84 product modules and 83 SciPy binary/extension records. No source from project tests/tools/outputs/work or unrelated codex-primary-runtime tool directories was collected. In particular, no Poppler ICU or libheif API-set payload remains. Vendor pytest/numpy testing support reached by normal SciPy hooks is not the project's test tree, cache or user data; no broad manual collection was used.

Required bundled components verified: python313.dll, Qt6Widgets.dll, qwindows.dll, sqlite3.dll, SciPy special/stats extensions. Required Qt and numerical native files actually loaded in the EXE process; existence alone was not treated as proof. Final loaded ICU is C:\\WINDOWS\\SYSTEM32\\icuuc.dll (and system icu.dll), which provides Qt's 20 required ICU imports.

## Build warnings reviewed

Full final warning output is retained in pyinstaller_warnings.txt and pyinstaller_build.log; it is not blanket-ignored.

| Warning family | Disposition and evidence |
|---|---|
| Hidden import scipy.special._cdflib not found | Standard _ufuncs hook requests this for every SciPy >=1.13. Installed accepted SciPy 1.18.1 has no such module: find_spec is None; no Python/pyx/pxd import found in its special directory. beta PPF uses _ufuncs._beta_ppf; CDF uses special.betainc. Both exist; source numeric check succeeds. Final EXE loads _ufuncs, _ufuncs_cxx, _special_ufuncs, _stats and cython_special. No synthetic _cdflib or dependency downgrade. Final actual history-visible GUI computation remains Phase 7B PENDING. |
| scipy.special.betainc/beta and other NumPy/SciPy function/type names | Static analysis confuses re-exported attributes with modules. 220 listed numerical re-export attributes resolve in the accepted wheel. Relevant numerical extensions are in analysis and loaded in the final EXE. |
| scipy.linalg._fblas_64 / _flapack_64 | Optional ILP64 variants guarded by HAS_ILP64; accepted LP64 _fblas/_flapack libraries are collected and loaded. Product Beta analysis does not request the ILP64 alternative. |
| collections.abc (including importers PySide6/sqlite3/product) | Python 3.13 collections explicitly aliases sys.modules['collections.abc'] to _collections_abc; that module is collected. Packaged PySide6/schema/startup imports succeed. |
| probability_calibration_tool.*, PySide6/Qt, sqlite3 required module names | No missing product module, required Qt module/plugin or sqlite3 runtime warning. The names in collections.abc's importer list are not missing project modules. Loaded-plugin and DB initialization smoke confirms these required paths. |
| pwd/grp/fcntl/posix/termios/_posixsubprocess/_posixshmem/resource/_scproxy, Java/VMS, curses/readline | Non-Windows or interactive-terminal conditional branches; accepted Windows lock uses msvcrt, which the smoke verified. Not product runtime dependencies on Windows 11. |
| _frozen_importlib*, pyimod02_importers; multiprocessing/asyncio exported names | Python/PyInstaller bootstrap builtins or re-exported attributes; final bootloader/frozen importer startup works. No product multiprocessing workflow added. |
| typing_extensions/_typeshed/annotationlib/exceptiongroup | Type-checking or alternate-Python-version branches. Python target remains 3.13. Actual imports and full source suite pass; no import-error fallback was added to product code. |
| torch/jax/cupy/dask/ndonnx/sparse/uarray/array_api_compat/cupyx and vendor array_namespace | Optional alternative numerical backends / vendor exports. This product uses NumPy-backed SciPy Beta, not those backends. |
| matplotlib/PIL/sphinx/yaml/Cython/psutil/threadpoolctl/win32pdh/chardet/ctags/twisted/zope/argcomplete/pexpect/pkg_resources and related vendor extras | Optional plotting, documentation, development, pytest or diagnostic branches, not requested product paths. Their absence does not justify copying developer environments. |
| _distributor_init_local, usercustomize/sitecustomize, win32evtlog/win32evtlogutil | Optional distributor/site overrides or Windows event-log handlers. App uses its accepted file logger, not event logging. |

The warnings do not replace manual numerical acceptance. No new hidden import was needed for the final launch; the actual blocking defect was a wrongly collected native DLL, fixed at build search-path level.

## External packaged process observations

- Full external copy: `C:\Users\rxy71\AppData\Local\Temp\Probability Calibration Tool RC dgajh1ad\Probability Calibration Tool`
- Absolute launched EXE: `C:\Users\rxy71\AppData\Local\Temp\Probability Calibration Tool RC dgajh1ad\Probability Calibration Tool\ProbabilityCalibrationTool.exe`
- Unrelated cwd: `C:\Users\rxy71\AppData\Local\Temp\Probability Calibration Tool RC dgajh1ad\unrelated working directory`
- Isolated LOCALAPPDATA: `C:\Users\rxy71\AppData\Local\Temp\Probability Calibration Tool RC dgajh1ad\isolated LOCALAPPDATA`
- PATH: `C:\Windows\System32;C:\Windows`; PYTHONPATH/VIRTUAL_ENV and inherited Qt/Python overrides removed; QT_QPA_PLATFORM=windows, not offscreen.
- A PID 35208: normal title Probability Calibration Tool 1.0, real qwindows/QtWidgets/Python/SQLite/SciPy libraries loaded; no loaded module under repository or .venv. No source, tests or virtual environment copied. System security software modules were observed in the process; they are not bundled application dependencies.
- B PID 31536: title Probability Calibration Tool only (ALREADY_RUNNING notification), no second normal business title. A remains alive; exclusive runtime byte lock confirmed. Human dismissal/exit confirmation is PENDING, not claimed automated PASS.
- Only saved A/B child processes were terminated after observation. Their PIDs are no longer running. NOT normal GUI close/reopen/Recovery acceptance.
- Cwd remains empty; artifact manifests unchanged; no DB/log/lock/backup written in artifact or cwd.

## Persistent data and read-only checks

The only persistent files created by the final smoke under its isolated LOCALAPPDATA were:

- `C:\Users\rxy71\AppData\Local\Temp\Probability Calibration Tool RC dgajh1ad\isolated LOCALAPPDATA\ProbabilityCalibrationTool\backups\daily\daily_2026-08-31_20260831T053058.126832Z_6804479a-5801-4fa2-baec-2aaa7805fe2e.db`
- `C:\Users\rxy71\AppData\Local\Temp\Probability Calibration Tool RC dgajh1ad\isolated LOCALAPPDATA\ProbabilityCalibrationTool\data\probability.db`
- `C:\Users\rxy71\AppData\Local\Temp\Probability Calibration Tool RC dgajh1ad\isolated LOCALAPPDATA\ProbabilityCalibrationTool\logs\app.log`
- `C:\Users\rxy71\AppData\Local\Temp\Probability Calibration Tool RC dgajh1ad\isolated LOCALAPPDATA\ProbabilityCalibrationTool\runtime\application.lock`

Fresh database and Daily backup each have integrity=ok, no FK violations, schema v1, zero rounds/snapshots/pending. This is a successful FRESH START smoke, not a full packaged round. Rechecked independently after child termination with mode=ro/query_only=ON. Neither the verifier nor the audit heals a database. Detailed paths/results: packaged_smoke.json, automated_integrity_packaged.json and automated_integrity_packaged_daily.json.

Windows 125%/150%, full packaged round, normal close/reopen Recovery, numerical history-valid GUI and final post-manual DB integrity remain PENDING. The automated native-module observations satisfy only Phase 7A's minimum packaged SciPy evidence, not Phase 7B.

