from probability_calibration_tool.infrastructure.paths import AppPaths


def test_explicit_and_production_paths_are_isolated_and_creation_idempotent(tmp_path):
    for paths in (AppPaths.from_root(tmp_path / "explicit"), AppPaths.from_local_appdata()):
        assert paths.root.is_relative_to(tmp_path)
        paths.create_directories()
        paths.create_directories()
        assert paths.database == paths.root / "data/probability.db"
        assert paths.log_file == paths.root / "logs/app.log"
        assert paths.lock_file == paths.root / "runtime/application.lock"
        assert all(path.is_dir() for path in (paths.recent, paths.daily, paths.safety))
        assert not paths.database.exists()
