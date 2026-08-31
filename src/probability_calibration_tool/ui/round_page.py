from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from probability_calibration_tool.application.enums import WorkflowState as S

from .analysis_panel import AnalysisPanel
from .post_run_panel import PostRunPanel
from .pre_run_panel import PreRunPanel
from .widgets import button, label


class RoundPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.pre = PreRunPanel()
        self.analysis = AnalysisPanel()
        self.post = PostRunPanel()
        self.completed = QWidget()
        notice = QHBoxLayout(self.completed)
        notice.addWidget(label("Round saved successfully."), 1)
        self.new_round = button("New Round")
        notice.addWidget(self.new_round)
        layout.addWidget(self.pre)
        layout.addWidget(self.analysis)
        layout.addWidget(self.post)
        layout.addWidget(self.completed)
        layout.addStretch()
        self.busy = label()
        layout.addWidget(self.busy)

    def render(self, workflow, *, show_analysis=True, void_confirmation=False):
        state = workflow.state
        editable = state in (S.DRAFT, S.PENDING_EDIT)
        self.pre.set_editable(editable)
        self.pre.primary.setText("Recalculate" if state == S.PENDING_EDIT else "Calculate")
        self.pre.primary.setVisible(editable)
        self.pre.primary.setEnabled(editable)
        self.pre.modify.setVisible(workflow.can_modify_prediction)
        self.pre.modify.setEnabled(workflow.can_modify_prediction)
        self.analysis.render(
            workflow.analysis if show_analysis and state != S.DRAFT else None,
            editing=state == S.PENDING_EDIT,
        )
        self.post.setVisible(state in (S.PENDING_LOCKED, S.CONFIRM_SAVE, S.COMPLETING))
        self.post.result.sync(workflow.post_run_choices[0])
        self.post.include.sync(workflow.post_run_choices[1])
        self.post.result.setEnabled(state == S.PENDING_LOCKED)
        self.post.include.setEnabled(state == S.PENDING_LOCKED)
        self.post.confirmation.setVisible(state == S.CONFIRM_SAVE)
        self.post.save.setEnabled(state == S.CONFIRM_SAVE)
        self.post.void.setVisible(state == S.PENDING_LOCKED and not void_confirmation)
        self.post.void_confirmation.setVisible(state == S.PENDING_LOCKED and void_confirmation)
        self.completed.setVisible(state == S.COMPLETED_NOTICE)
        self.busy.setText("Working…" if state in (S.CALCULATING, S.COMPLETING) else "")
