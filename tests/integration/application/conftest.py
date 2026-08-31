import pytest

from .helpers import Harness


@pytest.fixture
def h(tmp_path):
    return Harness(tmp_path / "application.db")
