import hashlib
import sqlite3
from contextlib import closing

import pytest

from probability_calibration_tool.persistence.database import create_connection
from probability_calibration_tool.persistence.schema import initialize_v1


def test_verifier_does_not_repair_a_version_mismatched_stats_cache(tmp_path):
    from tools.release_verify import verify_database

    path = tmp_path / "verify.db"
    with closing(create_connection(path)) as db:
        initialize_v1(db)
        db.execute("UPDATE character_stats SET stats_version=99 WHERE character_id=1")
        db.commit()
    before = hashlib.sha256(path.read_bytes()).digest()
    result = verify_database(path)
    assert result["integrity"] == ["ok"]
    assert hashlib.sha256(path.read_bytes()).digest() == before
    with closing(sqlite3.connect(path)) as db:
        assert (
            db.execute("SELECT stats_version FROM character_stats WHERE character_id=1").fetchone()[
                0
            ]
            == 99
        )
    with pytest.raises(AssertionError):
        verify_database(path, final_manual=True)


def test_verifier_never_creates_a_missing_database(tmp_path):
    from tools.release_verify import inspect_database

    path = tmp_path / "missing.db"
    with pytest.raises(FileNotFoundError):
        inspect_database(path)
    assert not path.exists()
