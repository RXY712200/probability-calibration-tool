import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    root: Path

    @classmethod
    def from_root(cls, root: Path | str):
        return cls(Path(root).resolve())

    @classmethod
    def from_local_appdata(cls):
        location = os.environ.get("LOCALAPPDATA")
        if not location or not Path(location).is_absolute():
            raise ValueError("An absolute LOCALAPPDATA path is required.")
        return cls.from_root(Path(location) / "ProbabilityCalibrationTool")

    @property
    def database(self):
        return self.root / "data" / "probability.db"

    @property
    def recent(self):
        return self.root / "backups" / "recent"

    @property
    def daily(self):
        return self.root / "backups" / "daily"

    @property
    def safety(self):
        return self.root / "backups" / "safety"

    @property
    def log_file(self):
        return self.root / "logs" / "app.log"

    @property
    def lock_file(self):
        return self.root / "runtime" / "application.lock"

    def create_directories(self) -> None:
        for directory in (
            self.database.parent,
            self.recent,
            self.daily,
            self.safety,
            self.log_file.parent,
            self.lock_file.parent,
        ):
            directory.mkdir(parents=True, exist_ok=True)
