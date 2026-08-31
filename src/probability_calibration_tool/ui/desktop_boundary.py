"""One execution, one authoritative re-render, then errors/warnings. Never retry."""

from probability_calibration_tool.application.errors import BusinessRuleError, InputValidationError
from probability_calibration_tool.application.reliability_views import ReliabilityResult


class DesktopBoundary:
    def _show_error(self, message, warnings=(), *, error_id=None):
        if error_id is not None:
            message = f"{message} Error ID: {error_id}"
        if warnings:
            message += "\nWarnings:\n" + "\n".join(warnings)
        try:
            self.banner.show_message(message, "error")
        except Exception:
            # The error presentation itself failed. Log once; do not recurse into rendering.
            self.session.runtime.logger.exception("Error presentation failed: %s", error_id)

    def _report(self, exc, warnings=()):
        safe = self.session.report_unexpected(exc)
        self._show_error(safe.message, warnings, error_id=safe.error_id)

    def _invoke(self, operation):
        if self._disposed or self._operation_active:
            return
        result, failure = None, None
        self._operation_active = True
        try:
            self._clear_errors()
            if self.render_from_workflow() is False:
                return
            result = operation()
        except Exception as exc:  # noqa: BLE001 - defer safe reporting until authoritative render
            failure = exc
        finally:
            self._operation_active = False
        if self._disposed:
            return result
        if self.render_from_workflow() is False:
            return result
        warnings = ()
        try:
            warnings = self.session.take_warnings()
            if isinstance(failure, InputValidationError):
                self._input_error(failure)
                if warnings:
                    self._show_error(str(failure), warnings)
            elif isinstance(failure, BusinessRuleError):
                self._show_error(str(failure), warnings)
            elif failure is not None:
                self._report(failure, warnings)
            elif isinstance(result, ReliabilityResult) and result.error is not None:
                self._show_error(result.error.message, warnings, error_id=result.error.error_id)
            elif warnings:
                self.banner.show_message("\n".join(warnings), "warning")
        except Exception as exc:  # noqa: BLE001 - report presentation failure without retry
            self._report(exc, warnings)
        return result

    def render_from_workflow(self):
        if self._disposed:
            return False
        try:
            self._render()
            return True
        except Exception as exc:  # noqa: BLE001 - top-level nonrecursive rendering boundary
            self._report(exc, self.session.take_warnings())
            return False

    def close_for_session_replacement(self):
        # Not a user close. Never consult Workflow or Close Guard after revocation.
        self._disposed = True
        self.setEnabled(False)
        self.hide()
        self.deleteLater()

    def _load_backups(self):
        def load():
            self._revoke_confirmation("restore")
            self.restore_page.populate(self.session.catalog.refresh())

        return self._invoke(load)

    def _begin_restore(self):
        def begin():
            self._revoke_confirmation("restore")
            selected = self.restore_page.selected()
            if selected is not None:
                self._restore_ticket = self.session.begin_restore(selected.candidate_id)

        return self._invoke(begin)

    def _cancel_restore(self):
        return self._invoke(lambda: self._revoke_confirmation("restore"))

    def _revoke_confirmation(self, kind):
        """Keep the local presentation and matching Session authority in sync."""
        ticket = getattr(self, f"_{kind}_ticket")
        getattr(self.session, f"cancel_{kind}")(ticket)
        setattr(self, f"_{kind}_ticket", None)

    def _invoke_confirmation(self, kind, ticket, operation):
        try:
            return self._invoke(operation)
        finally:
            # Confirm remains one-shot even if a pre-action render/precondition fails.
            # Successful Restore already disposed its old Session and all its tickets.
            if not self._disposed:
                getattr(self.session, f"cancel_{kind}")(ticket)

    def _confirm_restore(self):
        ticket, self._restore_ticket = self._restore_ticket, None
        if ticket is not None:
            return self._invoke_confirmation(
                "restore", ticket, lambda: self.session.restore(ticket)
            )

    def _connect_restore(self):
        page = self.restore_page
        page.restore.clicked.connect(self._begin_restore)
        page.confirm.clicked.connect(self._confirm_restore)
        page.back.clicked.connect(self._cancel_restore)
        page.refresh.clicked.connect(self._load_backups)
        page.candidates.itemSelectionChanged.connect(self.render_from_workflow)
