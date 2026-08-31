import ast
import os
import runpy
import struct
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def artifact(tmp_path):
    root = tmp_path / "artifact"
    files = [
        "ProbabilityCalibrationTool.exe",
        "_internal/python313.dll",
        "_internal/PySide6/plugins/platforms/qwindows.dll",
        "_internal/PySide6/Qt6Widgets.dll",
        "_internal/scipy/special/_ufuncs.cp313-win_amd64.pyd",
        "_internal/scipy/stats/_stats.cp313-win_amd64.pyd",
        "_internal/sqlite3.dll",
    ]
    for name in files:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"test-only artifact audit fixture")
    header = bytearray(256)
    header[:2] = b"MZ"
    struct.pack_into("<I", header, 0x3C, 0x80)
    header[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<H", header, 0x84, 0x8664)
    struct.pack_into("<H", header, 0x80 + 24, 0x20B)
    struct.pack_into("<H", header, 0x80 + 24 + 68, 2)
    (root / "ProbabilityCalibrationTool.exe").write_bytes(header)
    return root


def test_artifact_audit_requires_runtime_and_allows_legitimate_vendor_names(artifact):
    from tools.release_verify import audit_artifact

    vendor = artifact / "_internal" / "numpy" / "tests" / "vendor_runtime.pyd"
    vendor.parent.mkdir(parents=True)
    vendor.write_bytes(b"legitimate vendor name is not project leakage")
    assert audit_artifact(artifact)["leaks"] == []


@pytest.mark.parametrize(
    "name",
    [
        "probability.db",
        "_internal/app.log",
        "application.lock",
        "backups/recent/test.db",
        ".venv/Scripts/python.exe",
        "src/probability_calibration_tool/a.py",
        "tests/test_example.py",
        ".pytest_cache/nodeids",
        "_internal/.pytest_cache/nodeids",
        "outputs/phase7a_report.md",
    ],
)
def test_artifact_audit_rejects_project_user_and_generated_data(artifact, name):
    from tools.release_verify import audit_artifact

    path = artifact / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"must not ship")
    with pytest.raises(AssertionError, match="leaked"):
        audit_artifact(artifact)


def test_missing_windows_plugin_is_rejected(artifact):
    from tools.release_verify import audit_artifact

    # A missing-plugin fixture is created by renaming this disposable test file.
    path = artifact / "_internal/PySide6/plugins/platforms/qwindows.dll"
    path.rename(path.with_suffix(".missing"))
    with pytest.raises(AssertionError, match="qt_windows_plugin"):
        audit_artifact(artifact)


@pytest.mark.parametrize("field,value", [(0x84, 0x14C), (0x80 + 24 + 68, 3)])
def test_wrong_architecture_or_console_executable_is_rejected(artifact, field, value):
    from tools.release_verify import audit_artifact

    path = artifact / "ProbabilityCalibrationTool.exe"
    header = bytearray(path.read_bytes())
    struct.pack_into("<H", header, field, value)
    path.write_bytes(header)
    with pytest.raises(AssertionError, match="x64 Windows GUI"):
        audit_artifact(artifact)


def test_packaging_adapter_and_spec_keep_production_bootstrap_and_onedir():
    root = Path(__file__).parents[2]
    adapter = ast.parse((root / "packaging/pyinstaller_entry.py").read_text())
    imports = [n for n in adapter.body if isinstance(n, ast.ImportFrom)]
    assert [n.module for n in imports] == ["probability_calibration_tool.bootstrap"]
    assert isinstance(adapter.body[-1], ast.Raise)
    text = (root / "packaging/ProbabilityCalibrationTool.spec").read_text()
    tree = ast.parse(text)
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    assert any(n.func.id == "COLLECT" for n in calls)
    exe = next(n for n in calls if n.func.id == "EXE")
    assert next(k.value.value for k in exe.keywords if k.arg == "console") is False
    assert "SPECPATH" in text and 'root / "src"' in text
    assert "collect_all" not in text


def test_packaged_environment_does_not_rely_on_venv_or_pythonpath(tmp_path, monkeypatch):
    from tools.packaged_smoke import sanitized_environment

    monkeypatch.setenv("PYTHONPATH", "project/src")
    monkeypatch.setenv("VIRTUAL_ENV", "project/.venv")
    monkeypatch.setenv("QT_PLUGIN_PATH", "project/.venv/qt")
    monkeypatch.setenv("PATH", "project/.venv/Scripts")
    environment = sanitized_environment(tmp_path)
    assert "PYTHONPATH" not in environment and "VIRTUAL_ENV" not in environment
    assert "QT_PLUGIN_PATH" not in environment
    assert ".venv" not in environment["PATH"]
    assert environment["LOCALAPPDATA"] == str(tmp_path)
    assert environment["QT_QPA_PLATFORM"] == "windows"


def test_spec_native_discovery_excludes_unrelated_developer_tool_dlls(monkeypatch):
    root = Path(__file__).parents[2]
    monkeypatch.setenv("PATH", r"C:\unrelated\poppler\bin;C:\project\.venv\Scripts")
    windows = Path(os.environ["SystemRoot"])
    observed = []

    def analysis(*args, **kwargs):
        observed.append(os.environ["PATH"])
        assert kwargs["pathex"] == [str(root / "src")]
        assert kwargs["hiddenimports"] == kwargs["binaries"] == kwargs["datas"] == []
        return SimpleNamespace(pure=[], scripts=[], binaries=[], datas=[])

    runpy.run_path(
        str(root / "packaging/ProbabilityCalibrationTool.spec"),
        init_globals={
            "SPECPATH": str(root / "packaging"),
            "Analysis": analysis,
            "PYZ": lambda *a, **k: None,
            "EXE": lambda *a, **k: None,
            "COLLECT": lambda *a, **k: None,
        },
    )
    assert observed == [os.pathsep.join(map(str, (windows / "System32", windows)))]
