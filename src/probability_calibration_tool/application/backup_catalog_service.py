"""Session-local opaque handles. Restore still independently verifies the file."""

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from probability_calibration_tool.infrastructure.backup import BackupCategory, InventoryKind

from .errors import BusinessRuleError, ErrorCode


@dataclass(frozen=True)
class CatalogCandidate:
    candidate_id: str
    category: str
    created_at: datetime
    reason: str | None = None
    valid: bool = True


class BackupCatalogService:
    def __init__(self, backup, guard):
        self._backup, self._guard = backup, guard
        self._paths = {}

    def refresh(self) -> tuple[CatalogCandidate, ...]:
        self._guard()
        # Invalidate the old generation even when inventory fails midway.
        self._paths.clear()
        rows, paths = [], {}
        for category in BackupCategory:
            for entry in self._backup.inventory(category):
                if entry.kind == InventoryKind.VALID:
                    handle = str(uuid4())
                    paths[handle] = entry.path
                    rows.append(CatalogCandidate(handle, category.value, entry.created_at))
        self._paths = paths
        return tuple(rows)

    def resolve(self, candidate_id):
        self._guard()
        if candidate_id not in self._paths:
            raise BusinessRuleError(
                "Backup selection expired. Reload and select again.", code=ErrorCode.BACKUP_EXPIRED
            )
        return self._paths[candidate_id]
