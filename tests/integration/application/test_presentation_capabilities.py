import pytest

from application.helpers import COMMAND
from probability_calibration_tool.application.enums import WorkflowState as S


@pytest.mark.parametrize("reset", ["complete", "void"])
def test_can_modify_prediction_tracks_existing_lock_and_reset(h, reset):
    workflow = h.workflow()
    assert not workflow.can_modify_prediction
    workflow.set_inputs(COMMAND)
    workflow.calculate()
    assert workflow.can_modify_prediction
    workflow.modify()
    assert workflow.state == S.PENDING_EDIT and not workflow.can_modify_prediction
    workflow.calculate()
    assert workflow.can_modify_prediction
    if reset == "complete":
        workflow.choose_result(True)
        assert not workflow.can_modify_prediction
        workflow.choose_include(True)
        workflow.back()
        assert not workflow.can_modify_prediction
        workflow.choose_result(False)
        workflow.confirm_save()
        workflow.dismiss_completed()
    else:
        workflow.void_pending()
    assert not workflow.can_modify_prediction
    workflow.set_inputs(COMMAND)
    workflow.calculate()
    assert workflow.can_modify_prediction


def test_recovery_capability_never_unlocks_prediction(h):
    h.rounds.calculate(COMMAND)
    workflow = h.workflow()
    workflow.inspect_recovery()
    assert not workflow.can_modify_prediction
    workflow.continue_recovery()
    assert not workflow.can_modify_prediction
    workflow.choose_result(False)
    workflow.choose_include(False)
    workflow.back()
    assert not workflow.can_modify_prediction


def test_can_modify_prediction_is_read_only(h):
    workflow = h.workflow()
    with pytest.raises(AttributeError):
        workflow.can_modify_prediction = True
