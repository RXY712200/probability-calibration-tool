import os
import subprocess
import sys
from pathlib import Path

from probability_calibration_tool.infrastructure.runtime_lock import RuntimeLock

SCRIPT = """
import sys
from pathlib import Path
from probability_calibration_tool.infrastructure.runtime_lock import RuntimeLock
lock = RuntimeLock(Path(sys.argv[1]))
acquired = lock.acquire()
print('acquired' if acquired else 'blocked', flush=True)
if acquired and sys.argv[2] == 'hold':
    sys.stdin.readline()
lock.release()
"""


def test_real_subprocess_forced_death_releases_os_lock(rig):
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[3] / "src"))
    # Resolve against the actual project rather than any production path.
    env["PYTHONPATH"] = str(Path.cwd() / "src")
    args = [sys.executable, "-u", "-c", SCRIPT, str(rig.paths.lock_file)]
    with subprocess.Popen(
        args + ["hold"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    ) as owner:
        assert owner.stdout.readline().strip() == "acquired"
        second = subprocess.run(
            args + ["once"], capture_output=True, text=True, env=env, timeout=15, check=True
        )
        assert second.stdout.strip() == "blocked"
        owner.kill()  # No release/finally path in the owning process.
        owner.wait(timeout=15)
    assert rig.paths.lock_file.exists()
    third = subprocess.run(
        args + ["once"], capture_output=True, text=True, env=env, timeout=15, check=True
    )
    assert third.stdout.strip() == "acquired"


def test_stale_file_and_normal_release(rig):
    rig.paths.lock_file.write_bytes(b"stale")
    lock = RuntimeLock(rig.paths.lock_file)
    assert lock.acquire()
    second = RuntimeLock(rig.paths.lock_file)
    assert not second.acquire()
    lock.release()
    assert second.acquire()
    second.release()
