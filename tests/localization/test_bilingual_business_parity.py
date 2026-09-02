from __future__ import annotations

from dataclasses import asdict, replace

import pytest

from probability_calibration_tool.application.commands import CalculateCommand
from probability_calibration_tool.application.reliability_views import StartupDisposition
from probability_calibration_tool.application.restore_service import RestoreService
from probability_calibration_tool.application.startup_service import StartupService
from probability_calibration_tool.desktop_host import DesktopHost
from probability_calibration_tool.infrastructure.backup import (
    BackupCategory,
    BackupService,
    InventoryKind,
    SQLiteSafetyBackupAdapter,
)
from probability_calibration_tool.infrastructure.paths import AppPaths
from probability_calibration_tool.localization import Language

from .qa_helpers import (
    ParityHarness,
    activated_track,
    build_official_qm,
    canonical_database,
    create_seed_database,
    run_bilingual_pair,
)

COMMAND = CalculateCommand(1, False, 70, "2.00", "3.00")


@pytest.fixture(scope="module")
def step6_qm(tmp_path_factory):
    return build_official_qm(tmp_path_factory.mktemp("step6-official-qm"))


def _result(h, machine):
    return {"machine": machine, "database": canonical_database(h.path)}


def _semantic_stats(record):
    values = asdict(record)
    # Same allowlist as canonical_database: this repository timestamp has no
    # injectable clock and therefore differs between sequential language runs.
    values["updated_at"] = "<wall-clock>"
    return values


def _p1_basic_no_history(h):
    workflow = h.workflow()
    workflow.set_inputs(COMMAND)
    view = workflow.calculate()
    return _result(h, {"state": workflow.state, "analysis": asdict(view)})


def _p2_insufficient_history(h):
    h.seed_history(1, 0)
    workflow = h.workflow()
    workflow.set_inputs(replace(COMMAND, reference_history=True))
    view = workflow.calculate()
    snapshot = h.snapshot(view.round_id)
    return _result(
        h,
        {
            "state": workflow.state,
            "history": asdict(view.history),
            "history_snapshot": (
                snapshot.history_wins,
                snapshot.history_losses,
                snapshot.history_sample_size,
                snapshot.history_model_status,
                snapshot.history_probability,
                snapshot.history_lower,
                snapshot.history_upper,
                snapshot.history_statistically_ready,
            ),
        },
    )


def _p3_valid_history(h):
    h.seed_history(19, 1)
    workflow = h.workflow()
    workflow.set_inputs(replace(COMMAND, reference_history=True))
    view = workflow.calculate()
    return _result(
        h,
        {
            "state": workflow.state,
            "history": asdict(view.history),
            "snapshot": asdict(h.snapshot(view.round_id)),
        },
    )


def _p4_modify_recalculate_complete(h):
    workflow = h.workflow()
    workflow.set_inputs(COMMAND)
    locked = workflow.calculate()
    original_snapshot = h.snapshot(locked.round_id)
    workflow.modify()
    workflow.set_inputs(replace(COMMAND, p_h_raw=40, win_odds_raw="4.00"))
    assert h.snapshot(locked.round_id) == original_snapshot
    revised = workflow.calculate()
    workflow.choose_result(False)
    workflow.choose_include(True)
    completed = workflow.confirm_save()
    return _result(
        h,
        {
            "same_round": locked.round_id == revised.round_id == completed.round_id,
            "original_snapshot": asdict(original_snapshot),
            "revised_snapshot": asdict(h.snapshot(locked.round_id)),
            "record": asdict(h.record(locked.round_id)),
            "state": workflow.state,
        },
    )


def _p5_complete_exclude(h):
    workflow = h.workflow()
    workflow.set_inputs(COMMAND)
    view = workflow.calculate()
    workflow.choose_result(True)
    workflow.choose_include(False)
    workflow.confirm_save()
    return _result(
        h,
        {
            "record": asdict(h.record(view.round_id)),
            "stats": _semantic_stats(h.stats()),
            "state": workflow.state,
        },
    )


def _p6_void_pending(h):
    workflow = h.workflow()
    workflow.set_inputs(COMMAND)
    view = workflow.calculate()
    outcome = workflow.void_pending("用户取消：赔率输入有误")
    return _result(
        h,
        {
            "outcome": asdict(outcome),
            "record": asdict(h.record(view.round_id)),
            "stats": _semantic_stats(h.stats()),
            "state": workflow.state,
        },
    )


def _p7_start_new_regime(h):
    h.seed_history(2, 1)
    with h.factory() as uow:
        old = uow.regimes.get_active(1)
    h.clock.advance()
    reason = "规则调整：第二阶段"
    new = h.regimes.start_new_regime(1, reason)
    pending = h.rounds.calculate(replace(COMMAND, reference_history=True))
    with h.factory() as uow:
        ended = uow.regimes.get(old.regime_id)
    return _result(
        h,
        {
            "old": asdict(ended),
            "new": asdict(new),
            "new_history": asdict(pending.history),
            "reason_exact": new.reason == reason,
        },
    )


def _p8_historical_correction(h):
    view = h.rounds.calculate(COMMAND)
    h.rounds.complete_pending(view.round_id, True, True)
    original_snapshot = h.snapshot(view.round_id)
    reason = "更正原因：局后结果录反"
    corrected = h.corrections.correct_post_run(view.round_id, False, False, reason)
    original = h.record(view.round_id)
    replacement = h.record(corrected.replacement_round_id)
    return _result(
        h,
        {
            "correction": asdict(corrected),
            "original": asdict(original),
            "replacement": asdict(replacement),
            "snapshot_a": asdict(original_snapshot),
            "snapshot_b": asdict(h.snapshot(replacement.round_id)),
            "stats": _semantic_stats(h.stats()),
            "backup_reasons": tuple(h.backup.calls),
            "reason_exact": replacement.void_reason is None and original.void_reason == reason,
        },
    )


def _p9_recovery_continue_complete(h):
    locked = h.rounds.calculate(COMMAND)
    before = canonical_database(h.path)
    id_count = h.ids.count
    workflow = h.workflow()
    inspection = workflow.inspect_recovery()
    recovered = workflow.continue_recovery()
    assert canonical_database(h.path) == before
    assert h.ids.count == id_count
    workflow.choose_result(True)
    workflow.choose_include(True)
    workflow.confirm_save()
    return _result(
        h,
        {
            "inspection": asdict(inspection),
            "same_round": recovered.round_id == locked.round_id,
            "same_snapshot": asdict(h.snapshot(locked.round_id)),
            "round_count": len(canonical_database(h.path)["rounds"][1]),
            "state": workflow.state,
            "stats": _semantic_stats(h.stats()),
        },
    )


P1_P9 = {
    "P1": _p1_basic_no_history,
    "P2": _p2_insufficient_history,
    "P3": _p3_valid_history,
    "P4": _p4_modify_recalculate_complete,
    "P5": _p5_complete_exclude,
    "P6": _p6_void_pending,
    "P7": _p7_start_new_regime,
    "P8": _p8_historical_correction,
    "P9": _p9_recovery_continue_complete,
}


@pytest.mark.parametrize("scenario", P1_P9, ids=P1_P9)
def test_p1_p9_formal_bilingual_business_and_six_table_parity(
    scenario, tmp_path, localization_app, step6_qm
):
    run_bilingual_pair(tmp_path, localization_app, step6_qm, P1_P9[scenario])


def _restore_track(root, app, candidate_qm, language, *, emergency):
    paths = AppPaths.from_root(root / "business")
    paths.create_directories()
    seed = root.parent / "shared-seed.db"
    if not seed.exists():
        create_seed_database(seed)
    paths.database.write_bytes(seed.read_bytes())
    h = ParityHarness(paths.database)
    h.seed_history(1, 0)
    backup = BackupService(paths, clock=h.clock, ids=h.ids)
    restore_candidate = backup.create(BackupCategory.RECENT).path
    candidate_semantics = canonical_database(restore_candidate)
    h.seed_history(0, 1)
    if emergency:
        paths.database.write_bytes(b"damaged live database")
    with activated_track(app, root / "localization", language, candidate_qm) as context:
        runtime = StartupService(paths).start()
        safety = SQLiteSafetyBackupAdapter(
            BackupService(paths, clock=h.clock, ids=h.ids, logger=runtime.logger)
        )
        host = DesktopHost(
            runtime,
            backup=backup,
            restore=RestoreService(runtime, safety=safety),
        )
        host.bind_localization(context)
        try:
            host.show_initial_state()
            observed_initial_disposition = runtime.result.disposition
            old = host.lease
            handles = old.catalog.refresh()
            handle = next(
                row.candidate_id
                for row in handles
                if old.catalog.resolve(row.candidate_id) == restore_candidate
            )
            result = old.restore(old.begin_restore(handle))
            machine = {
                "initial_disposition": observed_initial_disposition,
                "result": result.disposition,
                "old_disposed": old.disposed,
                "replacement_session": host.session is not None and host.lease is not old,
                "candidate": candidate_semantics,
                "safety_pre_restore": tuple(
                    entry.kind
                    for entry in backup.inventory(BackupCategory.SAFETY)
                    if entry.kind == InventoryKind.VALID and "pre_restore" in entry.path.name
                ),
                "quarantine_count": sum(
                    entry.kind == InventoryKind.QUARANTINE
                    for entry in backup.inventory(BackupCategory.SAFETY)
                ),
            }
        finally:
            host.dispose()
            runtime.close()
    return {"machine": machine, "database": canonical_database(paths.database)}


@pytest.mark.parametrize("emergency", [False, True], ids=["P10-normal", "P11-emergency"])
def test_p10_p11_formal_bilingual_restore_parity(emergency, tmp_path, localization_app, step6_qm):
    outputs = {
        language: _restore_track(
            tmp_path / language.value,
            localization_app,
            step6_qm,
            language,
            emergency=emergency,
        )
        for language in (Language.EN, Language.ZH_CN)
    }
    assert outputs[Language.EN] == outputs[Language.ZH_CN]
    expected = (
        StartupDisposition.EMERGENCY_RECOVERY if emergency else StartupDisposition.READY_DRAFT
    )
    assert outputs[Language.EN]["machine"]["initial_disposition"] == expected
    assert outputs[Language.ZH_CN]["machine"]["initial_disposition"] == expected
    safety = outputs[Language.EN]["machine"]["safety_pre_restore"]
    assert bool(safety) is (not emergency)


@pytest.mark.parametrize(
    "probability,win_odds,lose_odds",
    [
        (0, "2", "3"),
        (1, "2.50", "1"),
        (50, "1", "1.25"),
        (99, "100", "1.01"),
        (100, "1.0", "2.000"),
    ],
)
def test_representative_probability_and_textual_odds_bilingual_parity(
    probability, win_odds, lose_odds, tmp_path, localization_app, step6_qm
):
    command = CalculateCommand(1, False, probability, win_odds, lose_odds)

    def scenario(h):
        view = h.rounds.calculate(command)
        record = h.record(view.round_id)
        snapshot = h.snapshot(view.round_id)
        return _result(
            h,
            {
                "raw_probability": record.p_h_raw,
                "used_probability": snapshot.p_h_used,
                "odds_raw": (record.win_odds_raw, record.lose_odds_raw),
                "odds_parsed": (record.win_odds, record.lose_odds),
                "snapshot": asdict(snapshot),
            },
        )

    run_bilingual_pair(tmp_path, localization_app, step6_qm, scenario)
