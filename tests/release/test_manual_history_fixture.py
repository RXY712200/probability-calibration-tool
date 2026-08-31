import hashlib
from pathlib import Path

import pytest


def test_manual_fixture_is_verified_valid_history_and_never_overwrites_existing_root(tmp_path):
    from tools.prepare_manual_history import prepare

    root = tmp_path / "new isolated LOCALAPPDATA"
    evidence = prepare(root)
    assert (evidence["wins"], evidence["losses"]) == (19, 1)
    assert evidence["database"]["completed"] == evidence["database"]["snapshots"] == 20
    assert evidence["database"]["pending"] == 0
    assert evidence["recent"]["integrity"] == ["ok"]
    assert evidence["history_expected"]["sample_size"] == 20
    database = Path(evidence["database"]["path"])
    digest = hashlib.sha256(database.read_bytes()).digest()
    with pytest.raises(FileExistsError):
        prepare(root)
    assert hashlib.sha256(database.read_bytes()).digest() == digest
