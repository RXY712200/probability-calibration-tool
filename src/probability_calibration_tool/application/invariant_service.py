"""Inspect source facts without repairing or recomputing saved predictions."""

from collections import Counter
from contextlib import closing

from probability_calibration_tool.infrastructure.sqlite_health import open_existing
from probability_calibration_tool.persistence.reliability import (
    SourceInventory,
    read_source_inventory,
)
from probability_calibration_tool.persistence.seed import CHARACTERS

from .errors import ApplicationInvariantError
from .reliability_views import InvariantReport


class InvariantService:
    def inspect(self, path) -> InvariantReport:
        with closing(open_existing(path)) as connection:
            connection.execute("BEGIN")
            return self.inspect_inventory(read_source_inventory(connection))

    def require_valid(self, path) -> InvariantReport:
        report = self.inspect(path)
        if report.issues:
            raise ApplicationInvariantError("; ".join(report.issues))
        return report

    def inspect_inventory(self, data: SourceInventory) -> InvariantReport:
        issues = []
        identities = {
            (r["character_id"], r["internal_code"], r["display_name"], r["tainted"], r["pair_row"])
            for r in data.characters
        }
        if len(data.characters) != 34 or identities != set(CHARACTERS):
            issues.append("Frozen character identities differ.")
        character_ids = {r["character_id"] for r in data.characters}
        regimes = {r["regime_id"]: r for r in data.regimes}
        active = Counter(r["character_id"] for r in data.regimes if r["active"] == 1)
        if any(active[r["character_id"]] != 1 for r in data.characters if r["active"] == 1):
            issues.append("Active character must have exactly one active regime.")
        if len(regimes) != len(data.regimes) or any(
            r["character_id"] not in character_ids
            or r["active"] not in (0, 1)
            or (r["active"] == 1) != (r["ended_at"] is None)
            for r in data.regimes
        ):
            issues.append("Regime source structure is inconsistent.")
        rounds = {r["round_id"]: r for r in data.rounds}
        snapshots = {r["round_id"]: r for r in data.snapshots}
        if (
            len(rounds) != len(data.rounds)
            or len(snapshots) != len(data.snapshots)
            or rounds.keys() != snapshots.keys()
        ):
            issues.append("Every round must own exactly one snapshot, with no orphans.")
        replacements = Counter(
            r["supersedes_round_id"] for r in data.rounds if r["supersedes_round_id"] is not None
        )
        if any(count > 1 for count in replacements.values()):
            issues.append("Supersede audit graph branches.")
        copy_fields = (
            "character_id",
            "history_regime_id",
            "reference_history",
            "p_h_raw",
            "win_odds_raw",
            "lose_odds_raw",
            "win_odds",
            "lose_odds",
            "calculated_at",
            "revision_count",
            "history_exposed",
            "history_exposed_at",
            "subjective_independence_compromised",
        )
        for row in data.rounds:
            regime = regimes.get(row["history_regime_id"])
            if regime is None or regime["character_id"] != row["character_id"]:
                issues.append("Round character/regime relationship is invalid.")
            status = row["status"]
            facts = (row["result"], row["include_character_history"], row["completed_at"])
            empty = all(value is None for value in facts)
            full = (
                row["result"] in (0, 1)
                and row["include_character_history"] in (0, 1)
                and row["completed_at"] is not None
            )
            if not (
                (status == "pending" and empty and row["voided_at"] is None)
                or (status == "completed" and full and row["voided_at"] is None)
                or (status == "voided" and row["voided_at"] is not None and (empty or full))
            ):
                issues.append("Round lifecycle facts are inconsistent.")
            if bool(row["history_exposed"]) != (row["history_exposed_at"] is not None) or (
                row["subjective_independence_compromised"] and not row["history_exposed"]
            ):
                issues.append("Exposure audit facts are inconsistent.")
            snapshot = snapshots.get(row["round_id"])
            if snapshot is not None:
                if (
                    row["reference_history"]
                    and snapshot["history_model_status"] == "valid"
                    and not row["history_exposed"]
                ):
                    issues.append("Visible history lacks durable exposure authority.")
                last = rounds.get(snapshot["last_included_historical_round_id"])
                if snapshot["last_included_historical_round_id"] is not None and (
                    last is None
                    or last["round_id"] == row["round_id"]
                    or last["character_id"] != row["character_id"]
                    or last["history_regime_id"] != row["history_regime_id"]
                    or last["calculated_at"] > row["calculated_at"]
                ):
                    issues.append("Historical snapshot source link is inconsistent.")
            parent_id = row["supersedes_round_id"]
            if parent_id is not None:
                parent = rounds.get(parent_id)
                if (
                    parent is None
                    or parent["status"] != "voided"
                    or status == "pending"
                    or any(row[field] != parent[field] for field in copy_fields)
                ):
                    issues.append("Supersede prediction facts are inconsistent.")
                elif (
                    snapshot is not None
                    and parent_id in snapshots
                    and {k: v for k, v in snapshot.items() if k != "round_id"}
                    != {k: v for k, v in snapshots[parent_id].items() if k != "round_id"}
                ):
                    issues.append("Supersede snapshots do not preserve the original prediction.")
        # Linear-time color walk, including disconnected components and self cycles.
        done = set()
        for start in rounds:
            visiting = set()
            node = start
            while node in rounds and node not in done:
                if node in visiting:
                    issues.append("Supersede audit graph contains a cycle.")
                    break
                visiting.add(node)
                node = rounds[node]["supersedes_round_id"]
            done.update(visiting)
        if data.source_fk_violations:
            issues.append("Source foreign-key relationships are invalid.")
        return InvariantReport(
            tuple(dict.fromkeys(issues)), sum(r["status"] == "pending" for r in data.rounds)
        )
