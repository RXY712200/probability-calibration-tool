import pytest
from infrastructure.helpers import make_rig


@pytest.fixture(autouse=True)
def isolated_localappdata(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "test-localappdata"))


@pytest.fixture
def rig(tmp_path):
    return make_rig(tmp_path / "app")
