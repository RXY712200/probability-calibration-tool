import logging

from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from probability_calibration_tool.application.enums import RecoveryState
from probability_calibration_tool.application.enums import WorkflowState as S
from probability_calibration_tool.application.errors import BusinessRuleError, InputValidationError
from probability_calibration_tool.application.reliability_views import (
    ReliabilityResult,
)
from probability_calibration_tool.application.reliability_views import (
    StartupDisposition as D,
)
from probability_calibration_tool.infrastructure.error_reporting import report_error

from .banners import BannerHost
from .character_matrix import CharacterMatrix
from .close_guard import CloseDecision, close_decision, confirm_close
from .maintenance_page import MaintenancePage
from .presentation import PresentationPorts, calculate_command
from .recovery_page import RecoveryPage
from .round_page import RoundPage
from .startup_pages import EmergencyRecoveryPage, StartupSafetyPage
from .widgets import button


class MainWindow(QMainWindow):
    """Injected public Workflow and presentation ports; no production bootstrap here."""

    def __init__(self, workflow, characters, *, ports=None, close_confirmation=confirm_close):
        super().__init__()
        self.workflow = workflow
        self.ports = ports if ports is not None else PresentationPorts()
        self.close_confirmation = close_confirmation
        self.names = {c.character_id: c.display_name for c in characters}
        # Session preferences and transient page/dialog presentation only, not business facts.
        self._session_character = self._session_reference = None
        self._input_source = object()
        self._page = "round"
        self._void_confirmation = self._regime_confirmation = False
        self._operation_active = False
        self._startup = None
        self._recovery_presentation = None
        self.setWindowTitle("Probability Calibration Tool 1.0")
        self.resize(1100, 800)
        central = QWidget()
        self.setCentralWidget(central)
        outer = QHBoxLayout(central)
        self.characters = CharacterMatrix(characters)
        outer.addWidget(self.characters)
        right = QVBoxLayout()
        outer.addLayout(right, 1)
        navigation = QHBoxLayout()
        self.round_button, self.maintenance_button = button("Round"), button("Maintenance")
        navigation.addWidget(self.round_button)
        navigation.addWidget(self.maintenance_button)
        navigation.addStretch()
        right.addLayout(navigation)
        self.banner = BannerHost()
        right.addWidget(self.banner)
        self.stack = QStackedWidget()
        right.addWidget(self.stack, 1)
        self.round = RoundPage()
        self.maintenance = MaintenancePage()
        self.recovery = RecoveryPage()
        self.recovery_error = StartupSafetyPage()
        self.safety = StartupSafetyPage()
        self.emergency = EmergencyRecoveryPage()
        for page in (
            self.round,
            self.maintenance,
            self.recovery,
            self.recovery_error,
            self.safety,
            self.emergency,
        ):
            self.stack.addWidget(page)
        self._connect()
        self.setStyleSheet(
            "QGroupBox { font-weight: 600; margin-top: 8px; }"
            "QGroupBox::title { subcontrol-origin: margin; }"
            "QPushButton:checked { border: 2px solid #386ca3; }"
        )
        self.render_from_workflow()

    def _connect(self):
        pre, post = self.round.pre, self.round.post
        self.characters.selected.connect(self._select_character)
        pre.reference.chosen.connect(self._select_reference)
        pre.primary.clicked.connect(self._calculate)
        pre.modify.clicked.connect(lambda: self._invoke(self.workflow.modify))
        post.result.chosen.connect(
            lambda value: self._invoke(lambda: self.workflow.choose_result(value))
        )
        post.include.chosen.connect(
            lambda value: self._invoke(lambda: self.workflow.choose_include(value))
        )
        post.back.clicked.connect(lambda: self._invoke(self.workflow.back))
        post.save.clicked.connect(lambda: self._invoke(self.workflow.confirm_save))
        post.void.clicked.connect(lambda: self._show_void(True))
        post.cancel_void.clicked.connect(lambda: self._show_void(False))
        post.confirm_void.clicked.connect(self._void)
        self.round.new_round.clicked.connect(lambda: self._invoke(self.workflow.dismiss_completed))
        self.round_button.clicked.connect(self.show_round)
        self.maintenance_button.clicked.connect(self.show_maintenance)
        self.maintenance.table.itemSelectionChanged.connect(self.render_from_workflow)
        self.maintenance.start.clicked.connect(lambda: self._show_regime(True))
        self.maintenance.back.clicked.connect(lambda: self._show_regime(False))
        self.maintenance.confirm.clicked.connect(self._start_regime)
        self.recovery.continue_button.clicked.connect(self._continue_recovery)
        self.emergency.candidates.itemSelectionChanged.connect(self.render_from_workflow)
        self.emergency.restore.clicked.connect(self._request_restore)
        for page in (self.recovery_error, self.safety, self.emergency):
            page.close_button.clicked.connect(self.close)

    def _select_character(self, value):
        self._session_character = value

    def _select_reference(self, value):
        self._session_reference = value

    def _clear_errors(self):
        self.round.pre.clear_errors()
        self.characters.error.clear()
        self.maintenance.reason_error.clear()
        self.banner.clear()

    def _invoke(self, operation):
        self._clear_errors()
        try:
            return operation()
        except InputValidationError as exc:
            if exc.field == "character_id":
                self.characters.error.setText(str(exc))
            elif exc.field == "reason":
                self.maintenance.reason_error.setText(str(exc))
            else:
                self.round.pre.show_error(exc.field, str(exc))
        except BusinessRuleError as exc:
            self.banner.show_message(str(exc), "error")
        except Exception as exc:  # noqa: BLE001 - GUI boundary logs errors and displays safe DTOs
            reporter = self.ports.report_unexpected
            safe = (
                reporter(exc)
                if reporter is not None
                else report_error(
                    logging.getLogger(__name__), exc, "The operation could not be completed."
                )
            )
            self.banner.show_error(safe)
        finally:
            self.render_from_workflow()

    def _calculate(self):
        pre = self.round.pre

        def calculate():
            command = calculate_command(
                self.characters.value(),
                pre.reference.value(),
                pre.probability.text(),
                pre.win_odds.text(),
                pre.lose_odds.text(),
            )
            self.workflow.set_inputs(command)
            self.workflow.calculate()

        self._invoke(calculate)

    def _show_void(self, show):
        self._void_confirmation = show
        if not show:
            self.round.post.reason.clear()
        self.render_from_workflow()

    def _void(self):
        def execute():
            self.workflow.void_pending(self.round.post.reason.text() or None)
            self._void_confirmation = False

        self._invoke(execute)

    def show_round(self):
        self._page = "round"
        self.render_from_workflow()

    def show_maintenance(self):
        if self.ports.maintenance_rows is None:
            return

        def load():
            self.maintenance.populate(self.ports.maintenance_rows())
            self._page = "maintenance"

        self._invoke(load)

    def _show_regime(self, show):
        self._regime_confirmation = show
        if not show:
            self.maintenance.reason.clear()
        self.render_from_workflow()

    def _start_regime(self):
        def execute():
            selected = self.maintenance.selected()
            self.ports.start_regime(selected.character_id, self.maintenance.reason.text() or None)
            self._regime_confirmation = False
            self.maintenance.reason.clear()
            self.maintenance.populate(self.ports.maintenance_rows())

        self._invoke(execute)

    def present_recovery(self, presentation):
        self._recovery_presentation = presentation
        self.render_from_workflow()

    def inspect_recovery(self):
        def inspect():
            recovery = self.workflow.inspect_recovery()
            if (
                recovery.state == RecoveryState.RECOVERABLE
                and self.ports.recovery_preview is not None
            ):
                self._recovery_presentation = self.ports.recovery_preview()
            else:
                from .presentation import RecoveryPresentation

                self._recovery_presentation = RecoveryPresentation(recovery)

        self._invoke(inspect)

    def _continue_recovery(self):
        def execute():
            self.workflow.continue_recovery()
            self._startup = None
            self._recovery_presentation = None
            self._page = "round"

        self._invoke(execute)

    def present_startup(self, result, *, recovery=None, candidates=()):
        self._startup = result
        self._recovery_presentation = recovery
        self.emergency.populate(candidates)
        if result.error is not None:
            self.banner.show_error(result.error)
        elif result.warnings:
            self.banner.show_message("\n".join(result.warnings), "warning")
        else:
            self.banner.clear()
        self.render_from_workflow()
        if result.disposition == D.EMERGENCY_RECOVERY:
            # Qt may assign a current row when an item view gains initial page focus.
            # Start on the safe Close action, with no candidate selection/current row.
            self.emergency.close_button.setFocus()
            self.emergency.candidates.clearSelection()
            self.emergency.candidates.setCurrentRow(-1)
            self.render_from_workflow()

    def _request_restore(self):
        selected = self.emergency.selected()
        if selected is None or self.ports.request_restore is None:
            return

        def request():
            self._operation_active = True
            self.render_from_workflow()
            try:
                outcome = self.ports.request_restore(selected.candidate_id)
                if outcome is not None:
                    self.banner.show_message(outcome, "information")
            finally:
                self._operation_active = False

        self._invoke(request)

    def render_from_workflow(self):
        state = self.workflow.state
        startup = None if self._startup is None else self._startup.disposition
        safe_only = startup not in (None, D.READY_DRAFT, D.READY_RECOVERY)
        busy = state in (S.CALCULATING, S.COMPLETING) or self._operation_active
        if safe_only:
            page = (
                self.emergency
                if startup == D.EMERGENCY_RECOVERY
                else (self.recovery_error if startup == D.RECOVERY_ERROR else self.safety)
            )
            if page != self.emergency:
                page.render(self._startup)
        elif state == S.RECOVERY_ERROR:
            page = self.recovery_error
            page.render(ReliabilityResult(D.RECOVERY_ERROR))
        elif state == S.RECOVERY or startup == D.READY_RECOVERY:
            page = self.recovery
        elif self._page == "maintenance":
            page = self.maintenance
        else:
            page = self.round
        self.stack.setCurrentWidget(page)
        self.round.setEnabled(not safe_only)
        self.round_button.setEnabled(not safe_only and not busy)
        self.maintenance_button.setEnabled(
            not safe_only
            and not busy
            and state not in (S.RECOVERY, S.RECOVERY_ERROR)
            and self.ports.maintenance_rows is not None
        )
        command = self.workflow.inputs
        if command is not self._input_source:
            if command is None:
                self.round.pre.clear_raw()
                self.round.pre.reference.sync(self._session_reference)
                self.characters.sync(self._session_character, False)
                self.round.post.reason.clear()
                self._void_confirmation = False
                self._clear_errors()
            else:
                self.round.pre.load(command)
            self._input_source = command
        selected = self.characters.value()
        if command is not None and not (state in (S.DRAFT, S.PENDING_EDIT)):
            selected = command.character_id
        elif selected is None:
            selected = self._session_character
        self.characters.sync(selected, page == self.round and state in (S.DRAFT, S.PENDING_EDIT))
        self.round.render(
            self.workflow,
            show_analysis=page == self.round,
            void_confirmation=self._void_confirmation,
        )
        self.recovery.clear_sensitive_data()
        if page == self.recovery:
            self.recovery.render(self._recovery_presentation, self.names)
        self.maintenance.render(
            can_start=state in (S.DRAFT, S.COMPLETED_NOTICE),
            confirmation=self._regime_confirmation,
            connected=self.ports.start_regime is not None,
        )
        self.emergency.render(connected=self.ports.request_restore is not None, active=busy)

    def closeEvent(self, event):
        decision = close_decision(
            self.workflow.state,
            self.workflow.post_run_choices,
            operation_active=self._operation_active,
        )
        if decision == CloseDecision.IGNORE:
            event.ignore()
        elif (
            self.stack.currentWidget() in (self.recovery_error, self.safety, self.emergency)
            or decision == CloseDecision.ACCEPT
            or self.close_confirmation(self, decision)
        ):
            event.accept()
        else:
            event.ignore()
