import os
import subprocess
import sys
import tomllib
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import pytest
from PySide6 import __version__ as pyside_version
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from probability_calibration_tool.localization import APP_QM_NAME


@pytest.fixture(scope="session")
def localization_app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
    return app


@pytest.fixture(autouse=True)
def isolated_localization(tmp_path, monkeypatch, localization_app):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "localappdata"))


@pytest.fixture
def real_contexts(localization_app):
    contexts = []
    yield contexts
    for context in reversed(contexts):
        for translator in (context.app_translator, context.qt_translator):
            if translator is not None:
                localization_app.removeTranslator(translator)


@pytest.fixture
def compile_qm(tmp_path):
    """Invoke the existing locked venv tool, never install or skip a missing tool."""
    repository = Path(__file__).parents[2]
    executable = Path(sys.executable).parent / "pyside6-lrelease.exe"
    assert executable.is_file()
    assert executable.resolve().is_relative_to((repository / ".venv").resolve())
    lock = tomllib.loads((repository / "uv.lock").read_text(encoding="utf-8"))
    locked_version = next(p["version"] for p in lock["package"] if p["name"] == "pyside6")
    assert pyside_version == locked_version
    version = subprocess.run(
        [str(executable), "-version"], capture_output=True, text=True, timeout=30, check=True
    )
    assert f"lrelease version {locked_version}" in version.stdout
    index = 0

    def compile_catalog(
        directory=None,
        *,
        locale="zh_CN",
        context="Localization",
        source="Language",
        translation="Temporary test translation",
        empty=False,
        name=APP_QM_NAME,
    ):
        nonlocal index
        index += 1
        directory = directory or tmp_path / f"catalog-{index}"
        directory.mkdir(parents=True, exist_ok=True)
        ts_path = tmp_path / f"smoke-{index}.ts"
        qm_path = directory / name
        language = "" if locale is None else f" language={quoteattr(locale)}"
        message = (
            ""
            if empty
            else (
                f"<context><name>{escape(context)}</name><message><source>{escape(source)}</source>"
                f"<translation>{escape(translation)}</translation></message></context>"
            )
        )
        ts_path.write_text(
            f'<?xml version="1.0" encoding="utf-8"?><TS version="2.1"{language} '
            f'sourcelanguage="en">{message}</TS>',
            encoding="utf-8",
        )
        process = subprocess.run(
            [str(executable), str(ts_path), "-qm", str(qm_path)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert process.returncode == 0, process.stdout + process.stderr
        assert qm_path.is_file()
        return qm_path

    return compile_catalog
