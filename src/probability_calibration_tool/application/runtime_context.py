"""Long-lived lock/logger owner with explicit managed-UoW quiescence for restore."""

from contextlib import contextmanager
from threading import RLock

from probability_calibration_tool.infrastructure.logging_setup import close_logger
from probability_calibration_tool.persistence.unit_of_work import UnitOfWork

from .reliability_views import StartupDisposition


class RuntimeBusyError(RuntimeError):
    pass


class RuntimeContext:
    def __init__(self, paths, lock, logger):
        self.paths, self.lock, self.logger = paths, lock, logger
        self.result = None
        self.unsafe_database = False
        self._active = 0
        self._paused = False
        self._guard = RLock()
        self._closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def uow_factory(self):
        runtime = self

        class ManagedUow(UnitOfWork):
            def __enter__(self):
                with runtime._guard:
                    if (
                        runtime._closed
                        or runtime._paused
                        or not runtime.lock.held
                        or runtime.unsafe_database
                        or runtime.result is None
                        or runtime.result.disposition
                        not in (StartupDisposition.READY_DRAFT, StartupDisposition.READY_RECOVERY)
                    ):
                        raise RuntimeBusyError("Runtime is not available for database access.")
                    runtime._active += 1
                try:
                    return super().__enter__()
                except BaseException:
                    with runtime._guard:
                        runtime._active -= 1
                    raise

            def __exit__(self, *args):
                try:
                    super().__exit__(*args)
                finally:
                    with runtime._guard:
                        runtime._active -= 1

        return lambda: ManagedUow(self.paths.database)

    @contextmanager
    def quiescent(self):
        with self._guard:
            if self._closed or self._active or self._paused or not self.lock.held:
                raise RuntimeBusyError(
                    "Cannot establish exclusive, connection-free restore access."
                )
            self._paused = True
        try:
            yield
        finally:
            with self._guard:
                self._paused = False

    def close(self):
        with self._guard:
            if self._active or self._paused:
                raise RuntimeBusyError("Close active database operations before closing runtime.")
            if self._closed:
                return
            self._closed = True
            try:
                close_logger(self.logger)
            finally:
                self.lock.release()
