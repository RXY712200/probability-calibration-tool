from PySide6.QtWidgets import QVBoxLayout, QWidget

from probability_calibration_tool.application.enums import RecoveryState

from .analysis_panel import AnalysisPanel
from .formatting import format_timestamp
from .widgets import button, label


class RecoveryPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(label("Recover pending round"))
        self.facts = label()
        self.analysis = AnalysisPanel()
        self.continue_button = button("Continue")
        layout.addWidget(self.facts)
        layout.addWidget(self.analysis)
        layout.addWidget(self.continue_button)
        layout.addStretch()

    def clear_sensitive_data(self):
        self.facts.clear()
        self.analysis.clear_sensitive_data()

    def render(self, presentation, names):
        self.clear_sensitive_data()
        self.continue_button.setEnabled(False)
        if presentation is None:
            self.facts.setText("A pending round is awaiting recovery.")
            return
        self.continue_button.setEnabled(presentation.recovery.state == RecoveryState.RECOVERABLE)
        view = presentation.analysis
        if view is None:
            self.facts.setText(
                "A committed pending round is available. Continue without recalculation."
            )
            return
        command = view.inputs
        self.facts.setText(
            f"{names[command.character_id]} · Subjective {command.p_h_raw}% · "
            f"Win odds {command.win_odds_raw} · Lose odds {command.lose_odds_raw}\n"
            f"{'Use history' if command.reference_history else 'Do not use history'} · "
            f"Calculated {format_timestamp(view.calculated_at)}"
        )
        self.analysis.render(view)
