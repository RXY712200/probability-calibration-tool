"""Prepare a NEW, isolated Phase 7B 19-win/1-loss fixture. Does not run manual acceptance."""

import argparse
import json
import sys
from pathlib import Path


def prepare(localappdata):
    from probability_calibration_tool import core
    from probability_calibration_tool.application.commands import CalculateCommand
    from probability_calibration_tool.application.invariant_service import InvariantService
    from probability_calibration_tool.application.ports import SystemClock, UUIDGenerator
    from probability_calibration_tool.application.reliability_views import StartupDisposition
    from probability_calibration_tool.application.round_service import RoundService
    from probability_calibration_tool.application.startup_service import StartupService
    from probability_calibration_tool.domain.enums import HistoryModelStatus
    from probability_calibration_tool.infrastructure.backup import BackupCategory, BackupService
    from probability_calibration_tool.infrastructure.paths import AppPaths
    from tools.release_verify import verify_database

    localappdata = Path(localappdata).resolve()
    # Deliberately refuse ANY existing root: no mutation of an existing user's application.
    localappdata.mkdir(parents=True, exist_ok=False)
    paths = AppPaths.from_root(localappdata / "ProbabilityCalibrationTool")
    with StartupService(paths).start() as runtime:
        assert runtime.result.disposition == StartupDisposition.READY_DRAFT
        factory = runtime.uow_factory()
        service = RoundService(factory, SystemClock(), UUIDGenerator())
        for index in range(20):
            view = service.calculate(CalculateCommand(1, False, 70, "2.00", "3.00"))
            service.complete_pending(view.round_id, index < 19, True)
        with factory() as uow:
            stats = uow.stats.get(1, "regime-1-1")
            assert (stats.included_games, stats.wins, stats.losses) == (20, 19, 1)
        backup = BackupService(paths, logger=runtime.logger).create(BackupCategory.RECENT)
    assert not InvariantService().inspect(paths.database).issues
    history = core.compute_historical_estimate(19, 1)
    assert history.status == HistoryModelStatus.VALID
    return {
        "status": "Fixture prepared only; packaged GUI acceptance is PENDING",
        "localappdata": str(localappdata),
        "character_id": 1,
        "regime_id": "regime-1-1",
        "database": verify_database(paths.database, final_manual=True),
        "recent": verify_database(backup.path, final_manual=True),
        "wins": 19,
        "losses": 1,
        "history_expected": {
            "sample_size": 20,
            "probability": history.probability,
            "lower": history.lower,
            "upper": history.upper,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--localappdata", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.localappdata), indent=2))


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    main()
