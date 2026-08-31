"""Read-only release inspection. Never migrates, repairs, or rebuilds a database."""

import argparse
import hashlib
import json
import sqlite3
import struct
from contextlib import closing
from pathlib import Path


def inspect_database(path):
    path = Path(path).resolve(strict=True)
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as db:
        db.execute("PRAGMA query_only=ON")
        return {
            "path": str(path),
            "integrity": [row[0] for row in db.execute("PRAGMA integrity_check")],
            "foreign_key_violations": [list(row) for row in db.execute("PRAGMA foreign_key_check")],
            "schema_version": db.execute("PRAGMA user_version").fetchone()[0],
            "rounds": db.execute("SELECT count(*) FROM rounds").fetchone()[0],
            "snapshots": db.execute("SELECT count(*) FROM round_analysis_snapshots").fetchone()[0],
            "pending": db.execute("SELECT count(*) FROM rounds WHERE status='pending'").fetchone()[
                0
            ],
            "completed": db.execute(
                "SELECT count(*) FROM rounds WHERE status='completed'"
            ).fetchone()[0],
        }


def verify_database(path, *, final_manual=False):
    result = inspect_database(path)
    assert result["integrity"] == ["ok"], result
    assert not result["foreign_key_violations"], result
    assert result["schema_version"] == 1, result
    assert result["rounds"] == result["snapshots"], result
    if final_manual:
        assert result["pending"] == 0 and result["completed"] >= 1, result
    return result


def artifact_inventory(root):
    root = Path(root).resolve(strict=True)
    files = []
    for path in sorted(root.rglob("*")):
        assert not path.is_symlink(), f"Unexpected artifact symlink: {path}"
        if path.is_file():
            with path.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            files.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "size": path.stat().st_size,
                    "sha256": digest,
                }
            )
    return files


def inspect_executable(path):
    """Read the PE header: AMD64 GUI subsystem, not a console or other architecture."""
    with Path(path).open("rb") as stream:
        assert stream.read(2) == b"MZ", "Missing DOS header"
        stream.seek(0x3C)
        offset = struct.unpack("<I", stream.read(4))[0]
        stream.seek(offset)
        assert stream.read(4) == b"PE\0\0", "Missing PE header"
        machine = struct.unpack("<H", stream.read(2))[0]
        stream.seek(offset + 24)
        magic = struct.unpack("<H", stream.read(2))[0]
        stream.seek(offset + 24 + 68)
        subsystem = struct.unpack("<H", stream.read(2))[0]
    assert (machine, magic, subsystem) == (0x8664, 0x20B, 2), "Expected x64 Windows GUI PE"
    return {"machine": "AMD64", "optional_header": "PE32+", "subsystem": "Windows GUI"}


def audit_artifact(root):
    files = artifact_inventory(root)
    forbidden_files = {
        "probability.db",
        "app.log",
        "application.lock",
        "pyproject.toml",
        "uv.lock",
        "spec_1.0.md",
    }
    forbidden_roots = {".venv", "src", "tests", "work", "outputs", ".pytest_cache", ".ruff_cache"}
    leaks = []
    for entry in files:
        path = Path(entry["path"])
        if path.name.lower() in forbidden_files or path.parts[0].lower() in forbidden_roots:
            leaks.append(entry["path"])
        if any(part.lower() in {".pytest_cache", ".ruff_cache", ".venv"} for part in path.parts):
            leaks.append(entry["path"])
        # SQLite payloads are never legitimate runtime assets in this product bundle.
        if path.suffix.lower() in {".db", ".sqlite", ".sqlite3"}:
            leaks.append(entry["path"])
        if path.name.startswith(("phase7", "phase6", "release_dpi_")):
            leaks.append(entry["path"])
    assert not leaks, f"Project/user data leaked into artifact: {leaks}"
    names = [entry["path"].lower() for entry in files]
    required = {
        "exe": any(name == "probabilitycalibrationtool.exe" for name in names),
        "python": any(name.endswith("/python313.dll") for name in names),
        "qt_windows_plugin": any(name.endswith("/platforms/qwindows.dll") for name in names),
        "qt_widgets": any(name.endswith("/qt6widgets.dll") for name in names),
        "scipy_special": any(
            "scipy/special/_ufuncs" in name and name.endswith(".pyd") for name in names
        ),
        "scipy_stats": any("scipy/stats/" in name and name.endswith(".pyd") for name in names),
        "sqlite": any(name.endswith("/sqlite3.dll") for name in names),
    }
    assert all(required.values()), required
    return {
        "root": str(Path(root).resolve()),
        "files": len(files),
        "bytes": sum(e["size"] for e in files),
        "required_components": required,
        "leaks": leaks,
        "inventory": files,
        "pe_header": inspect_executable(Path(root) / "ProbabilityCalibrationTool.exe"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path)
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--recent", type=Path)
    parser.add_argument("--final-manual", action="store_true")
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    if args.final_manual and (args.database is None or args.recent is None):
        parser.error("--final-manual requires both --database and --recent")
    result = {}
    if args.database:
        result["database"] = verify_database(args.database, final_manual=args.final_manual)
    if args.artifact:
        result["artifact"] = audit_artifact(args.artifact)
    if args.recent:
        result["recent"] = verify_database(args.recent, final_manual=args.final_manual)
    if not result:
        parser.error("Supply --database or --artifact")
    serialized = json.dumps(result, indent=2)
    if args.evidence:
        # Only the separate evidence report is writable; inputs remain read-only.
        destination = args.evidence.resolve()
        inputs = [p.resolve() for p in (args.database, args.recent) if p is not None]
        if destination in inputs or (
            args.artifact and destination.is_relative_to(args.artifact.resolve())
        ):
            parser.error("Evidence must not overwrite an inspected input or enter the artifact")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
