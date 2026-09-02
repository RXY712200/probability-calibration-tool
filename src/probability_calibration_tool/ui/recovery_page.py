from PySide6.QtCore import QT_TRANSLATE_NOOP, QCoreApplication
from PySide6.QtWidgets import QVBoxLayout, QWidget

from probability_calibration_tool.application.enums import RecoveryState

from .analysis_panel import AnalysisPanel
from .formatting import format_timestamp
from .localization import character_name, template
from .widgets import button, label


class RecoveryPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(label(QCoreApplication.translate("Recovery", "Recover pending round")))
        self.facts = label()
        self.analysis = AnalysisPanel()
        self.continue_button = button(QCoreApplication.translate("Recovery", "Continue"))
        layout.addWidget(self.facts)
        layout.addWidget(self.analysis)
        layout.addWidget(self.continue_button)
        layout.addStretch()

    def clear_sensitive_data(self):
        self.facts.clear()
        self.analysis.clear_sensitive_data()

    def render(self, presentation):
        self.clear_sensitive_data()
        self.continue_button.setEnabled(False)
        if presentation is None:
            self.facts.setText(
                QCoreApplication.translate("Recovery", "A pending round is awaiting recovery.")
            )
            return
        self.continue_button.setEnabled(presentation.recovery.state == RecoveryState.RECOVERABLE)
        view = presentation.analysis
        if view is None:
            self.facts.setText(
                QCoreApplication.translate(
                    "Recovery",
                    "A committed pending round is available. Continue without recalculation.",
                )
            )
            return
        command = view.inputs
        self.facts.setText(
            template(
                "Recovery",
                QT_TRANSLATE_NOOP(
                    "Recovery",
                    "%1 · Subjective %2% · Win odds %3 · Lose odds %4\n%5 · Calculated %6",
                ),
                character_name(command.character_id),
                command.p_h_raw,
                command.win_odds_raw,
                command.lose_odds_raw,
                QCoreApplication.translate("Recovery", "Use history")
                if command.reference_history
                else QCoreApplication.translate("Recovery", "Do not use history"),
                format_timestamp(view.calculated_at),
            )
        )
        self.analysis.render(view)
