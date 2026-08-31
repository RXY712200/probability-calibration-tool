"""OS-owned byte-range lock. A stale filename does not imply a live owner."""

import errno
import os
from contextlib import ExitStack
from pathlib import Path

if os.name == "nt":
    import msvcrt
else:
    import fcntl


class RuntimeLock:
    def __init__(self, path: Path):
        self.path = path
        self._file = None
        self._stack = None

    @property
    def held(self):
        return self._file is not None

    def acquire(self) -> bool:
        if self.held:
            raise RuntimeError("This lock object already owns a lock.")
        stack = ExitStack()
        stream = stack.enter_context(open(self.path, "a+b"))  # noqa: SIM115 - runtime-owned ExitStack
        try:
            if os.fstat(stream.fileno()).st_size == 0:
                stream.write(b"\0")
                stream.flush()
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            stack.close()
            if exc.errno in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                return False
            raise
        self._file = stream
        self._stack = stack
        return True

    def release(self) -> None:
        if self._file is None:
            return
        stream, self._file = self._file, None
        try:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        finally:
            self._stack.close()
            self._stack = None
