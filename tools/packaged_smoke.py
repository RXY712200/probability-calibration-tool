"""External onedir launch isolation, observation and exact-child process cleanup only."""

import argparse
import ctypes
import json
import os
import shutil
import subprocess
import tempfile
import time
from ctypes import wintypes
from pathlib import Path

from tools.release_verify import artifact_inventory, audit_artifact, verify_database


def sanitized_environment(localappdata):
    environment = dict(os.environ)
    for key in tuple(environment):
        if key.upper().startswith(
            ("PYTHON", "VIRTUAL_ENV", "QT_", "PYSIDE", "PYINSTALLER", "_PYI")
        ):
            environment.pop(key)
    windows = Path(environment.get("SystemRoot", "C:/Windows"))
    environment.update(
        LOCALAPPDATA=str(localappdata),
        PATH=str(windows / "System32") + os.pathsep + str(windows),
        QT_QPA_PLATFORM="windows",
    )
    return environment


def module_paths(pid):
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.EnumProcessModulesEx.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(wintypes.HMODULE),
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        wintypes.DWORD,
    ]
    psapi.GetModuleFileNameExW.argtypes = [
        wintypes.HANDLE,
        wintypes.HMODULE,
        wintypes.LPWSTR,
        wintypes.DWORD,
    ]
    handle = kernel.OpenProcess(0x0400 | 0x0010, False, pid)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        modules = (wintypes.HMODULE * 4096)()
        needed = wintypes.DWORD()
        if not psapi.EnumProcessModulesEx(
            handle, modules, ctypes.sizeof(modules), ctypes.byref(needed), 3
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        assert needed.value <= ctypes.sizeof(modules)
        paths = []
        for module in modules[: needed.value // ctypes.sizeof(wintypes.HMODULE)]:
            buffer = ctypes.create_unicode_buffer(32768)
            if psapi.GetModuleFileNameExW(handle, module, buffer, len(buffer)):
                paths.append(buffer.value)
        return paths
    finally:
        kernel.CloseHandle(handle)


def window_titles(pid):
    """Read-only process-owned top-level window observation; no clicks or acceptance."""
    user = ctypes.WinDLL("user32", use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    user.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    titles = []

    @callback_type
    def visit(window, extra):
        owner = wintypes.DWORD()
        user.GetWindowThreadProcessId(window, ctypes.byref(owner))
        if owner.value == pid:
            buffer = ctypes.create_unicode_buffer(4096)
            user.GetWindowTextW(window, buffer, len(buffer))
            if buffer.value:
                titles.append(buffer.value)
        return True

    user.EnumWindows(visit, 0)
    return titles


def wait_until(process, condition, *, timeout=60):
    # Bounded liveness guard, NOT a performance acceptance threshold.
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        assert process.poll() is None, f"Packaged child exited early: {process.returncode}"
        if condition():
            return
        time.sleep(0.1)
    raise TimeoutError("Packaged launch observation did not complete")


def launch(artifact, cwd, localappdata):
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0  # Hidden automated smoke, not manual Windows UI acceptance.
    return subprocess.Popen(
        [str(artifact / "ProbabilityCalibrationTool.exe")],
        cwd=cwd,
        env=sanitized_environment(localappdata),
        startupinfo=startup,
    )


def stop_child(process):
    if process is not None and process.poll() is None:
        process.terminate()
        process.wait(timeout=30)


def exercise(artifact, root=None):
    artifact = Path(artifact).resolve(strict=True)
    repository = Path(__file__).resolve().parents[1]
    root = (
        Path(root).resolve()
        if root
        else Path(tempfile.mkdtemp(prefix="Probability Calibration Tool RC "))
    )
    assert not root.is_relative_to(repository), "Outside-repository test root is required"
    root.mkdir(parents=True, exist_ok=True)
    external = root / "Probability Calibration Tool"
    assert not external.exists(), "Never overwrite a previous RC copy"
    shutil.copytree(artifact, external)
    source_audit = audit_artifact(artifact)
    external_audit = audit_artifact(external)
    assert source_audit["inventory"] == external_audit["inventory"]
    cwd = root / "unrelated working directory"
    localappdata = root / "isolated LOCALAPPDATA"
    cwd.mkdir()
    localappdata.mkdir()
    app_root = localappdata / "ProbabilityCalibrationTool"
    database = app_root / "data" / "probability.db"
    lock_file = app_root / "runtime" / "application.lock"
    process_a = process_b = None
    evidence = {
        "external_artifact": str(external),
        "cwd": str(cwd),
        "localappdata": str(localappdata),
        "exe": str(external / "ProbabilityCalibrationTool.exe"),
        "environment": sanitized_environment(localappdata)["PATH"],
        "artifact_sha256_matches": True,
        "shutdown": "Exact child processes terminated; NOT normal GUI-close acceptance",
    }
    try:
        process_a = launch(external, cwd, localappdata)
        wait_until(
            process_a,
            lambda: (
                database.exists()
                and lock_file.exists()
                and any((app_root / "backups" / "daily").glob("*.db"))
            ),
        )
        wait_until(
            process_a, lambda: "Probability Calibration Tool 1.0" in window_titles(process_a.pid)
        )
        modules = module_paths(process_a.pid)
        required = ["qwindows.dll", "Qt6Widgets.dll", "python313.dll", "sqlite3.dll"]
        for name in required:
            assert any(Path(path).name.lower() == name.lower() for path in modules), name
        assert any("scipy" in path.lower() and "_ufuncs" in path.lower() for path in modules)
        assert not any(Path(path).is_relative_to(repository) for path in modules)
        evidence["pid_a"] = process_a.pid
        evidence["windows_a"] = window_titles(process_a.pid)
        evidence["loaded_modules"] = modules
        # OS-level lock observation only: no production test hook or GUI manipulation.
        import msvcrt

        with lock_file.open("r+b") as lock:
            try:
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                evidence["runtime_lock_held"] = True
            else:
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
                raise AssertionError("Packaged runtime lock was not held")
        process_b = launch(external, cwd, localappdata)
        wait_until(
            process_b, lambda: "Probability Calibration Tool" in window_titles(process_b.pid)
        )
        assert "Probability Calibration Tool 1.0" not in window_titles(process_b.pid)
        assert process_a.poll() is None
        evidence["pid_b"] = process_b.pid
        evidence["windows_b"] = window_titles(process_b.pid)
        evidence["single_instance"] = (
            "PENDING manual dismissal/exit acceptance; automatic lock and notification-only second instance observed"
        )
        assert not list(cwd.iterdir())
        assert artifact_inventory(external) == external_audit["inventory"]
    finally:
        stop_child(process_b)
        stop_child(process_a)
    evidence["fresh_database"] = verify_database(database)
    evidence["daily_backups"] = [
        verify_database(path) for path in sorted((app_root / "backups" / "daily").glob("*.db"))
    ]
    evidence["persistent_files"] = [
        str(path.relative_to(localappdata))
        for path in sorted(localappdata.rglob("*"))
        if path.is_file()
    ]
    assert not list(cwd.iterdir())
    assert artifact_inventory(external) == external_audit["inventory"]
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--external-root", type=Path)
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    result = exercise(args.artifact, args.external_root)
    serialized = json.dumps(result, indent=2)
    if args.evidence:
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        args.evidence.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
