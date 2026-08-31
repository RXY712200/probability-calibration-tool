from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def release_isolation(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "isolated-localappdata"))
    monkeypatch.syspath_prepend(str(Path(__file__).parents[2]))
