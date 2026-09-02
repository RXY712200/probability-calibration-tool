"""Generate the Step 5 human-review inventory from the authoritative Qt TS."""

from __future__ import annotations

import argparse
import hashlib
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

INACTIVE_TYPES = {"vanished", "obsolete"}


def _active_messages(root: ET.Element):
    for context in root.findall("context"):
        name = context.findtext("name") or ""
        for message in context.findall("message"):
            translation = message.find("translation")
            if translation is not None and translation.get("type") not in INACTIVE_TYPES:
                yield name, message.findtext("source") or "", "".join(translation.itertext())


def _cell(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>")


def generate(ts_path: Path, output_path: Path) -> None:
    payload = ts_path.read_bytes()
    root = ET.fromstring(payload)
    units = list(_active_messages(root))
    digest = hashlib.sha256(payload).hexdigest()
    relative = ts_path.as_posix().replace("/", "\\")
    lines = [
        "# Localization Step 5 Translation Inventory",
        "",
        f"- Source TS: `{relative}`",
        f"- TS SHA-256: `{digest}`",
        f"- Active units: **{len(units)}**",
        f"- Generated (UTC): `{datetime.now(UTC).isoformat(timespec='seconds')}`",
        "",
        "> Generated automatically from the TS. This evidence is not a second translation authority.",
        "",
    ]
    for context in root.findall("context"):
        name = context.findtext("name") or ""
        rows = [unit for unit in units if unit[0] == name]
        if not rows:
            continue
        lines.extend(
            [
                f"## {name} ({len(rows)})",
                "",
                "| Context | Canonical English source | Simplified Chinese translation |",
                "|---|---|---|",
            ]
        )
        lines.extend(
            f"| {_cell(ctx)} | {_cell(source)} | {_cell(target)} |" for ctx, source, target in rows
        )
        lines.append("")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ts", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    generate(args.ts, args.output)


if __name__ == "__main__":
    main()
