import os
from pathlib import Path

# SPECPATH is supplied by PyInstaller, independent of the caller's cwd.
root = Path(SPECPATH).resolve().parent

# Restrict native dependency discovery to Windows, not unrelated tools on the
# developer shell PATH. An external Poppler ICU shadowed Windows ICU in the
# first build and caused QtWidgets to fail with a missing DLL procedure.
# Normal hooks still locate the locked Python/PySide6/SciPy wheel binaries.
windows = Path(os.environ["SystemRoot"])
os.environ["PATH"] = os.pathsep.join(map(str, (windows / "System32", windows)))
a = Analysis(
    [str(root / "packaging" / "pyinstaller_entry.py")],
    pathex=[str(root / "src")],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ProbabilityCalibrationTool",
    debug=False,
    strip=False,
    upx=False,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="ProbabilityCalibrationTool",
)
