"""Production adapters for accepted MainWindow; no SQL or model rules."""

from PySide6.QtCore import QCoreApplication

from probability_calibration_tool.application.enums import WorkflowState as S

from .correction_page import CorrectionPage
from .desktop_boundary import DesktopBoundary
from .language_dialog import LanguageDialog
from .localization import expected_error
from .main_window import MainWindow
from .presentation import CharacterOption, PresentationPorts
from .restore_page import RestorePage
from .widgets import button


class DesktopWindow(DesktopBoundary, MainWindow):
    def __init__(self, session, *, localization=None):
        self.session = session
        self.localization = localization
        self._disposed = self._extensions_ready = False
        self._regime_ticket = self._correction_ticket = self._restore_ticket = None
        self._save_armed = False
        self._last_state = None
        rows = session.maintenance_rows()
        super().__init__(
            session.workflow,
            tuple(CharacterOption(row.character_id) for row in rows),
            ports=PresentationPorts(
                maintenance_rows=session.maintenance_rows,
                start_regime=session.start_regime,
                report_unexpected=session.report_unexpected,
            ),
        )
        self.correction = CorrectionPage()
        self.restore_page = RestorePage()
        self.stack.addWidget(self.correction)
        self.stack.addWidget(self.restore_page)
        self.correction_button, self.restore_button = (
            button(QCoreApplication.translate("AppShell", "Historical Correction")),
            button(QCoreApplication.translate("AppShell", "Restore")),
        )
        # Add to the established right-side navigation; the character matrix never moves.
        navigation = self.round_button.parentWidget().layout().itemAt(1).layout().itemAt(0).layout()
        navigation.insertWidget(2, self.correction_button)
        navigation.insertWidget(3, self.restore_button)
        self.language_button = button(QCoreApplication.translate("Localization", "Language…"))
        navigation.addWidget(self.language_button)
        self.language_button.setEnabled(localization is not None)
        self.language_button.clicked.connect(self._choose_language)
        self.correction_button.clicked.connect(self.show_correction)
        self.restore_button.clicked.connect(self.show_restore)
        self.correction.start.clicked.connect(self._begin_correction)
        self.correction.back.clicked.connect(self._cancel_correction)
        self.correction.confirm.clicked.connect(self._confirm_correction)
        self.correction.candidates.itemSelectionChanged.connect(self.render_from_workflow)
        self.correction.result.chosen.connect(self.render_from_workflow)
        self.correction.include.chosen.connect(self.render_from_workflow)
        self.correction.reason.textChanged.connect(self.render_from_workflow)
        self._connect_restore()
        self.round.post.save.clicked.disconnect()
        self.round.post.save.clicked.connect(self._save)
        self._extensions_ready = True
        self.render_from_workflow()

    def _choose_language(self):
        if self.localization is not None and not self._operation_active and not self.session.busy:
            dialog = LanguageDialog(self.localization, self)
            dialog.saved.connect(lambda message: self.banner.show_message(message, "information"))
            dialog.exec()

    def _clear_errors(self):
        super()._clear_errors()
        if self._extensions_ready:
            self.correction.error.clear()

    def _input_error(self, exc):
        if self._page == "correction":
            self.correction.error.setText(expected_error(exc))
        elif exc.field == "character_id":
            self.characters.error.setText(expected_error(exc))
        elif exc.field == "reason":
            self.maintenance.reason_error.setText(expected_error(exc))
        else:
            self.round.pre.show_error(exc.field, expected_error(exc))

    def _render(self):
        MainWindow.render_from_workflow(self)
        state = self.workflow.state
        if state != self._last_state:
            self._save_armed = state == S.CONFIRM_SAVE
            self._last_state = state
        if not self._extensions_ready:
            return
        busy = self._operation_active or self.session.busy
        admin = self.session.can_admin() and not busy
        extra = {"correction": self.correction, "restore": self.restore_page}.get(self._page)
        if extra is not None and state == S.DRAFT:
            self.stack.setCurrentWidget(extra)
            self.round.analysis.clear_sensitive_data()
            self.characters.setEnabled(False)
        else:
            self.characters.setEnabled(not busy)
        self.round.setEnabled(not busy)
        self.maintenance.setEnabled(not busy)
        self.maintenance.render(
            can_start=admin, confirmation=self._regime_ticket is not None, connected=True
        )
        self.round.post.save.setEnabled(not busy and self._save_armed and state == S.CONFIRM_SAVE)
        self.round_button.setEnabled(not busy)
        self.maintenance_button.setEnabled(not busy and state not in (S.RECOVERY, S.RECOVERY_ERROR))
        self.correction_button.setEnabled(admin)
        self.restore_button.setEnabled(admin)
        self.language_button.setEnabled(self.localization is not None and not busy)
        self.correction.render(
            allowed=admin, confirming=self._correction_ticket is not None, busy=busy
        )
        self.restore_page.render_confirmation(
            allowed=admin, confirming=self._restore_ticket is not None, busy=busy
        )

    def _save(self):
        if self._disposed or not self._save_armed:
            return
        self._save_armed = False
        return self._invoke(self.workflow.confirm_save)

    def _void(self):
        if self._disposed or not self._void_confirmation:
            return
        self._void_confirmation = False
        return self._invoke(
            lambda: self.workflow.void_pending(self.round.post.reason.text() or None)
        )

    def _show_regime(self, show):
        def begin():
            self._revoke_confirmation("regime")
            if show and self.maintenance.selected() is not None:
                self._regime_ticket = self.session.begin_regime(
                    self.maintenance.selected().character_id
                )
            else:
                self.maintenance.reason.clear()

        return self._invoke(begin)

    def _start_regime(self):
        ticket, self._regime_ticket = self._regime_ticket, None
        if ticket is None:
            return

        def execute():
            self.session.start_regime(ticket, self.maintenance.reason.text() or None)
            self.maintenance.reason.clear()
            self.maintenance.populate(self.session.maintenance_rows())

        return self._invoke_confirmation("regime", ticket, execute)

    def _cancel_admin_confirmations(self):
        for kind in ("regime", "correction", "restore"):
            self._revoke_confirmation(kind)
        self.maintenance.reason.clear()
        self.correction.reset_form()

    def show_round(self):
        def load():
            self._cancel_admin_confirmations()
            self._page = "round"

        return self._invoke(load)

    def show_maintenance(self):
        def load():
            self._cancel_admin_confirmations()
            self.maintenance.populate(self.ports.maintenance_rows())
            self._page = "maintenance"

        return self._invoke(load)

    def show_correction(self):
        def load():
            self.session._require_admin()
            self._cancel_admin_confirmations()
            self.correction.populate(self.session.correction_candidates())
            self.correction.notice.clear()
            self._page = "correction"

        return self._invoke(load)

    def _begin_correction(self):
        def begin():
            self._revoke_confirmation("correction")
            selected = self.correction.selected()
            if selected is not None:
                self.correction.reset_form()
                self._correction_ticket = self.session.begin_correction(selected.round_id)

        return self._invoke(begin)

    def _cancel_correction(self):
        def cancel():
            self._revoke_confirmation("correction")
            self.correction.reset_form()

        return self._invoke(cancel)

    def _confirm_correction(self):
        ticket, self._correction_ticket = self._correction_ticket, None
        if ticket is None:
            return

        def execute():
            self.session.correct(
                ticket,
                self.correction.result.value(),
                self.correction.include.value(),
                self.correction.reason.text(),
            )
            self.correction.notice.setText(
                QCoreApplication.translate("Correction", "Correction saved.")
            )
            self.correction.populate(self.session.correction_candidates())
            self.maintenance.populate(self.session.maintenance_rows())

        return self._invoke_confirmation("correction", ticket, execute)

    def show_restore(self):
        def load():
            self.session._require_admin()
            self._cancel_admin_confirmations()
            self.restore_page.populate(self.session.catalog.refresh())
            self._page = "restore"

        return self._invoke(load)

    def closeEvent(self, event):
        if self._disposed:
            event.accept()
        else:
            super().closeEvent(event)
