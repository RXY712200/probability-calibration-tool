from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).parents[2]
TS_PATH = ROOT / "translations" / "probability_calibration_tool_zh_CN.ts"
INACTIVE_TYPES = {"vanished", "obsolete"}
CONTEXTS = {
    "AppShell",
    "Round",
    "Analysis",
    "Maintenance",
    "Correction",
    "Restore",
    "Recovery",
    "StartupSafety",
    "Errors",
    "Characters",
    "DomainLabels",
    "Localization",
}


@dataclass(frozen=True)
class Unit:
    context: str
    source: str
    translation: str
    translation_type: str | None
    numerus: str | None
    forms: tuple[str, ...]


def load_catalog(path: Path = TS_PATH) -> tuple[ET.Element, tuple[Unit, ...]]:
    root = ET.parse(path).getroot()
    units = []
    for context in root.findall("context"):
        name = context.findtext("name") or ""
        for message in context.findall("message"):
            translation = message.find("translation")
            assert translation is not None
            if translation.get("type") in INACTIVE_TYPES:
                continue
            units.append(
                Unit(
                    name,
                    message.findtext("source") or "",
                    "".join(translation.itertext()),
                    translation.get("type"),
                    message.get("numerus"),
                    tuple("".join(form.itertext()) for form in translation.findall("numerusform")),
                )
            )
    return root, tuple(units)


def catalog_map(path: Path = TS_PATH) -> dict[tuple[str, str], str]:
    return {(unit.context, unit.source): unit.translation for unit in load_catalog(path)[1]}
