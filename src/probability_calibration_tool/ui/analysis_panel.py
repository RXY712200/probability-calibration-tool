from PySide6.QtWidgets import QFormLayout, QGroupBox, QVBoxLayout, QWidget

from probability_calibration_tool.application.enums import HistoricalDisplayState as H
from probability_calibration_tool.domain.enums import OddsCombinationStatus

from .formatting import format_ev as ev
from .formatting import format_label, format_timestamp
from .formatting import format_probability as prob
from .widgets import label


class AnalysisCard(QGroupBox):
    def __init__(self, title, fields):
        super().__init__(title)
        self.values = {}
        self.captions = {}
        self.caption_text = dict(fields)
        self.form = QFormLayout(self)
        self.form.setVerticalSpacing(2)
        for name, caption in fields:
            title_label, value = label(caption), label()
            self.values[name], self.captions[name] = value, title_label
            self.form.addRow(title_label, value)
        self.message = label()
        self.form.addRow(self.message)
        self.clear_sensitive_data()

    def clear_sensitive_data(self):
        for key, widget in self.values.items():
            widget.clear()
            widget.hide()
            self.captions[key].clear()
            self.captions[key].hide()
        self.message.clear()
        self.message.hide()

    def fill(self, values):
        for key, text in values.items():
            self.values[key].setText(text)
            self.values[key].show()
            self.captions[key].setText(self.caption_text[key])
            self.captions[key].show()

    def say(self, text):
        self.message.setText(text)
        self.message.show()


class AnalysisPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.edit_note = label()
        layout.addWidget(self.edit_note)
        self.subjective = AnalysisCard(
            "Subjective Analysis",
            (
                ("probability", "Probability"),
                ("interval", "Uncertainty interval"),
                ("win", "Win-side EV / S"),
                ("lose", "Lose-side EV / S"),
                ("thresholds", "Break-even thresholds"),
                ("combination", "Odds combination"),
                ("calculated", "Calculated locally"),
            ),
        )
        self.historical = AnalysisCard(
            "Historical Analysis — independent model",
            (
                ("samples", "Eligible observations"),
                ("probability", "Historical probability"),
                ("interval", "Historical interval"),
                ("win", "Win-side EV / posterior"),
                ("lose", "Lose-side EV / posterior"),
                ("relations", "Model relations"),
                ("through", "Data through locally"),
            ),
        )
        layout.addWidget(self.subjective)
        self.combination_warning = label()
        layout.addWidget(self.combination_warning)
        layout.addWidget(self.historical)
        self.clear_sensitive_data()

    def clear_sensitive_data(self):
        self.edit_note.clear()
        self.edit_note.hide()
        self.combination_warning.clear()
        self.combination_warning.hide()
        self.subjective.clear_sensitive_data()
        self.historical.clear_sensitive_data()
        self.hide()

    def render(self, view, *, editing=False):
        self.clear_sensitive_data()
        if view is None:
            return
        self.show()
        if editing:
            self.edit_note.setText(
                "Locked analysis from the last successful calculation. "
                "Pending edits are not reflected until Recalculate succeeds."
            )
            self.edit_note.show()
        subject, odds = view.subjective, view.subjective_odds

        def side_text(side):
            return (
                f"{ev(side.ev_center)} [{ev(side.ev_min)}, {ev(side.ev_max)}] · "
                f"{format_label(side.ev_state)}"
            )

        def margin(side):
            value = side.robust_margin_index
            return "N/A" if value is None else f"{value:+.3f}"

        self.subjective.fill(
            {
                "probability": prob(subject.probability),
                "interval": f"{prob(subject.p_min)} – {prob(subject.p_max)}",
                "win": f"{side_text(odds.win)} · S {margin(odds.win)}",
                "lose": f"{side_text(odds.lose)} · S {margin(odds.lose)}",
                "thresholds": (
                    f"Win {prob(odds.break_even_win)}; loss event {prob(odds.break_even_lose_event)}; "
                    f"loss as win-probability {prob(odds.break_even_lose_as_win_probability)}"
                ),
                "combination": format_label(odds.odds_combination_status),
                "calculated": format_timestamp(view.calculated_at),
            }
        )
        if subject.p_h_raw in (0, 100):
            self.subjective.say(
                f"{subject.p_h_raw}% entered; {subject.p_h_used}% used for mathematical calculation."
            )
        if odds.odds_combination_status == OddsCombinationStatus.DOUBLE_POSITIVE_WINDOW:
            self.combination_warning.setText(
                "Warning: Double-positive window detected. Check the input/multiplier timing."
            )
            self.combination_warning.show()
        history = view.history
        messages = {
            H.HIDDEN: "Historical reference was not requested for this prediction.",
            H.NO_HISTORY: "No eligible history is available for the current character/regime.",
            H.INSUFFICIENT: "Historical data is not yet sufficient for numerical reference.",
        }
        if history.state != H.VISIBLE:
            self.historical.say(messages[history.state])
            return
        self.historical.fill(
            {
                "samples": f"Wins {history.wins}; losses {history.losses}; samples {history.sample_size}",
                "probability": prob(history.probability),
                "interval": f"{prob(history.lower)} – {prob(history.upper)}",
                "win": f"{side_text(history.odds.win)} · {prob(history.odds.win.threshold_posterior_probability)}",
                "lose": f"{side_text(history.odds.lose)} · {prob(history.odds.lose.threshold_posterior_probability)}",
                "relations": (
                    f"Win: {format_label(history.win_model_relation)}; "
                    f"Loss: {format_label(history.lose_model_relation)}"
                ),
                "through": format_timestamp(history.data_through_at),
            }
        )
