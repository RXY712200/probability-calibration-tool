def test_real_100k_history_startup_repair_calculate_frozen_snapshot_and_backup(tmp_path):
    from tools.release_performance import exercise

    evidence = exercise(tmp_path / "large-history", 100000)
    assert evidence["fixture"]["rounds"] == evidence["fixture"]["snapshots"] == 100000
    assert evidence["fixture"]["wins"] == 70000
    assert evidence["fixture"]["losses"] == 30000
    assert evidence["prediction_sample_size"] == 100000
    assert evidence["eligible_after_completion"] == 100001
    assert evidence["frozen_snapshot_unchanged"]
    assert evidence["final_integrity"]["integrity"] == ["ok"]
    assert evidence["backup_integrity"]["integrity"] == ["ok"]
