"""Version 1 explicit SQLite schema and atomic initialization."""

import sqlite3
from collections.abc import Callable
from datetime import UTC, datetime

from .database import serialize_utc
from .seed import CHARACTERS

SCHEMA_VERSION = 1

_DDL = (
    """
    CREATE TABLE characters (
        character_id INTEGER PRIMARY KEY CHECK(character_id BETWEEN 1 AND 34),
        internal_code TEXT NOT NULL UNIQUE,
        display_name TEXT NOT NULL,
        tainted INTEGER NOT NULL CHECK(tainted IN (0, 1)),
        pair_row INTEGER NOT NULL CHECK(pair_row BETWEEN 1 AND 17),
        active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0, 1)),
        UNIQUE(pair_row, tainted)
    )
    """,
    """
    CREATE TABLE history_regimes (
        regime_id TEXT PRIMARY KEY,
        character_id INTEGER NOT NULL,
        regime_number INTEGER NOT NULL CHECK(regime_number >= 1),
        started_at TEXT NOT NULL,
        ended_at TEXT NULL,
        active INTEGER NOT NULL CHECK(active IN (0, 1)),
        reason TEXT NULL,
        FOREIGN KEY(character_id) REFERENCES characters(character_id) ON DELETE RESTRICT,
        UNIQUE(character_id, regime_number),
        UNIQUE(character_id, regime_id),
        CHECK((active = 1 AND ended_at IS NULL) OR (active = 0 AND ended_at IS NOT NULL))
    )
    """,
    """
    CREATE TABLE rounds (
        round_id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL,
        calculated_at TEXT NOT NULL,
        last_updated_at TEXT NOT NULL,
        completed_at TEXT NULL,
        voided_at TEXT NULL,
        void_reason TEXT NULL,
        character_id INTEGER NOT NULL,
        history_regime_id TEXT NOT NULL,
        reference_history INTEGER NOT NULL CHECK(reference_history IN (0, 1)),
        p_h_raw INTEGER NOT NULL CHECK(p_h_raw BETWEEN 0 AND 100),
        win_odds_raw TEXT NOT NULL,
        lose_odds_raw TEXT NOT NULL,
        win_odds REAL NOT NULL CHECK(win_odds >= 1.0 AND win_odds <= 1.7976931348623157e308),
        lose_odds REAL NOT NULL CHECK(lose_odds >= 1.0 AND lose_odds <= 1.7976931348623157e308),
        status TEXT NOT NULL CHECK(status IN ('pending', 'completed', 'voided')),
        revision_count INTEGER NOT NULL DEFAULT 0 CHECK(revision_count >= 0),
        result INTEGER NULL CHECK(result IS NULL OR result IN (0, 1)),
        include_character_history INTEGER NULL CHECK(include_character_history IS NULL OR include_character_history IN (0, 1)),
        history_exposed INTEGER NOT NULL DEFAULT 0 CHECK(history_exposed IN (0, 1)),
        history_exposed_at TEXT NULL,
        subjective_independence_compromised INTEGER NOT NULL DEFAULT 0 CHECK(subjective_independence_compromised IN (0, 1)),
        supersedes_round_id TEXT NULL,
        FOREIGN KEY(character_id) REFERENCES characters(character_id) ON DELETE RESTRICT,
        FOREIGN KEY(character_id, history_regime_id) REFERENCES history_regimes(character_id, regime_id) ON DELETE RESTRICT,
        FOREIGN KEY(supersedes_round_id) REFERENCES rounds(round_id) ON DELETE RESTRICT,
        CHECK(round_id <> supersedes_round_id OR supersedes_round_id IS NULL),
        CHECK((history_exposed = 0 AND history_exposed_at IS NULL) OR (history_exposed = 1 AND history_exposed_at IS NOT NULL)),
        CHECK(
            (status = 'pending' AND result IS NULL AND include_character_history IS NULL
             AND completed_at IS NULL AND voided_at IS NULL AND void_reason IS NULL)
            OR
            (status = 'completed' AND result IS NOT NULL AND include_character_history IS NOT NULL
             AND completed_at IS NOT NULL AND voided_at IS NULL AND void_reason IS NULL)
            OR
            (status = 'voided' AND voided_at IS NOT NULL AND (
                (result IS NULL AND include_character_history IS NULL AND completed_at IS NULL)
                OR
                (result IS NOT NULL AND include_character_history IS NOT NULL AND completed_at IS NOT NULL)
            ))
        )
    )
    """,
    """
    CREATE TABLE round_analysis_snapshots (
        round_id TEXT PRIMARY KEY,
        p_h_used INTEGER NOT NULL CHECK(p_h_used BETWEEN 1 AND 99),
        subjective_probability REAL NOT NULL CHECK(subjective_probability BETWEEN 0 AND 1),
        subjective_p_min REAL NOT NULL CHECK(subjective_p_min > 0 AND subjective_p_min < 1),
        subjective_p_max REAL NOT NULL CHECK(subjective_p_max > 0 AND subjective_p_max < 1),
        subjective_logit_half_width REAL NOT NULL CHECK(subjective_logit_half_width > 0),
        subjective_model_version INTEGER NOT NULL CHECK(subjective_model_version >= 1),
        odds_analysis_version INTEGER NOT NULL CHECK(odds_analysis_version >= 1),
        break_even_win REAL NOT NULL CHECK(break_even_win BETWEEN 0 AND 1),
        break_even_lose_event REAL NOT NULL CHECK(break_even_lose_event BETWEEN 0 AND 1),
        break_even_lose_as_win_probability REAL NOT NULL CHECK(break_even_lose_as_win_probability BETWEEN 0 AND 1),
        subjective_win_ev_center REAL NOT NULL,
        subjective_win_ev_min REAL NOT NULL,
        subjective_win_ev_max REAL NOT NULL,
        subjective_win_margin_index REAL NULL,
        subjective_win_ev_state TEXT NOT NULL CHECK(subjective_win_ev_state IN ('robust_positive', 'robust_negative', 'crosses_threshold')),
        subjective_lose_ev_center REAL NOT NULL,
        subjective_lose_ev_min REAL NOT NULL,
        subjective_lose_ev_max REAL NOT NULL,
        subjective_lose_margin_index REAL NULL,
        subjective_lose_ev_state TEXT NOT NULL CHECK(subjective_lose_ev_state IN ('robust_positive', 'robust_negative', 'crosses_threshold')),
        odds_combination_status TEXT NOT NULL CHECK(odds_combination_status IN ('normal_overlap', 'critical', 'double_positive_window')),
        history_model_status TEXT NOT NULL CHECK(history_model_status IN ('no_history', 'insufficient', 'valid')),
        history_statistically_ready INTEGER NOT NULL CHECK(history_statistically_ready IN (0, 1)),
        history_wins INTEGER NOT NULL CHECK(history_wins >= 0),
        history_losses INTEGER NOT NULL CHECK(history_losses >= 0),
        history_sample_size INTEGER NOT NULL CHECK(history_sample_size >= 0),
        history_model_version INTEGER NOT NULL CHECK(history_model_version >= 1),
        history_gate_version INTEGER NOT NULL CHECK(history_gate_version >= 1),
        history_probability REAL NULL CHECK(history_probability BETWEEN 0 AND 1),
        history_lower REAL NULL CHECK(history_lower BETWEEN 0 AND 1),
        history_upper REAL NULL CHECK(history_upper BETWEEN 0 AND 1),
        history_data_through_at TEXT NOT NULL,
        last_included_historical_round_id TEXT NULL,
        historical_win_ev_center REAL NULL,
        historical_win_ev_min REAL NULL,
        historical_win_ev_max REAL NULL,
        historical_win_ev_state TEXT NULL CHECK(historical_win_ev_state IN ('robust_positive', 'robust_negative', 'crosses_threshold')),
        historical_win_threshold_posterior_probability REAL NULL CHECK(historical_win_threshold_posterior_probability BETWEEN 0 AND 1),
        historical_lose_ev_center REAL NULL,
        historical_lose_ev_min REAL NULL,
        historical_lose_ev_max REAL NULL,
        historical_lose_ev_state TEXT NULL CHECK(historical_lose_ev_state IN ('robust_positive', 'robust_negative', 'crosses_threshold')),
        historical_lose_threshold_posterior_probability REAL NULL CHECK(historical_lose_threshold_posterior_probability BETWEEN 0 AND 1),
        win_model_relation TEXT NOT NULL CHECK(win_model_relation IN ('agreement_positive', 'agreement_negative', 'conflict', 'uncertain', 'history_unavailable')),
        lose_model_relation TEXT NOT NULL CHECK(lose_model_relation IN ('agreement_positive', 'agreement_negative', 'conflict', 'uncertain', 'history_unavailable')),
        FOREIGN KEY(round_id) REFERENCES rounds(round_id) ON DELETE RESTRICT,
        FOREIGN KEY(last_included_historical_round_id) REFERENCES rounds(round_id) ON DELETE RESTRICT,
        CHECK(subjective_p_min < subjective_probability AND subjective_probability < subjective_p_max),
        CHECK(subjective_win_ev_min <= subjective_win_ev_center AND subjective_win_ev_center <= subjective_win_ev_max),
        CHECK(subjective_lose_ev_min <= subjective_lose_ev_center AND subjective_lose_ev_center <= subjective_lose_ev_max),
        CHECK(history_sample_size = history_wins + history_losses),
        CHECK(history_probability IS NULL OR (history_lower <= history_probability AND history_probability <= history_upper)),
        CHECK(historical_win_ev_min IS NULL OR (historical_win_ev_min <= historical_win_ev_center AND historical_win_ev_center <= historical_win_ev_max)),
        CHECK(historical_lose_ev_min IS NULL OR (historical_lose_ev_min <= historical_lose_ev_center AND historical_lose_ev_center <= historical_lose_ev_max)),
        CHECK(
            (history_model_status = 'no_history' AND history_sample_size = 0 AND history_wins = 0 AND history_losses = 0
             AND history_statistically_ready = 0 AND history_probability IS NULL AND history_lower IS NULL AND history_upper IS NULL
             AND last_included_historical_round_id IS NULL AND historical_win_ev_center IS NULL AND historical_win_ev_min IS NULL
             AND historical_win_ev_max IS NULL AND historical_win_ev_state IS NULL AND historical_win_threshold_posterior_probability IS NULL
             AND historical_lose_ev_center IS NULL AND historical_lose_ev_min IS NULL AND historical_lose_ev_max IS NULL
             AND historical_lose_ev_state IS NULL AND historical_lose_threshold_posterior_probability IS NULL
             AND win_model_relation = 'history_unavailable' AND lose_model_relation = 'history_unavailable')
            OR
            (history_model_status = 'insufficient' AND history_sample_size >= 1 AND history_statistically_ready = 0
             AND history_probability IS NOT NULL AND history_lower IS NOT NULL AND history_upper IS NOT NULL
             AND historical_win_ev_center IS NULL AND historical_win_ev_min IS NULL AND historical_win_ev_max IS NULL
             AND historical_win_ev_state IS NULL AND historical_win_threshold_posterior_probability IS NULL
             AND historical_lose_ev_center IS NULL AND historical_lose_ev_min IS NULL AND historical_lose_ev_max IS NULL
             AND historical_lose_ev_state IS NULL AND historical_lose_threshold_posterior_probability IS NULL
             AND win_model_relation = 'history_unavailable' AND lose_model_relation = 'history_unavailable')
            OR
            (history_model_status = 'valid' AND history_sample_size >= 1 AND history_statistically_ready = 1
             AND history_probability IS NOT NULL AND history_lower IS NOT NULL AND history_upper IS NOT NULL
             AND historical_win_ev_center IS NOT NULL AND historical_win_ev_min IS NOT NULL AND historical_win_ev_max IS NOT NULL
             AND historical_win_ev_state IS NOT NULL AND historical_win_threshold_posterior_probability IS NOT NULL
             AND historical_lose_ev_center IS NOT NULL AND historical_lose_ev_min IS NOT NULL AND historical_lose_ev_max IS NOT NULL
             AND historical_lose_ev_state IS NOT NULL AND historical_lose_threshold_posterior_probability IS NOT NULL
             AND win_model_relation <> 'history_unavailable' AND lose_model_relation <> 'history_unavailable')
        )
    )
    """,
    """
    CREATE TABLE character_stats (
        character_id INTEGER NOT NULL,
        regime_id TEXT NOT NULL,
        included_games INTEGER NOT NULL DEFAULT 0 CHECK(included_games >= 0),
        wins INTEGER NOT NULL DEFAULT 0 CHECK(wins >= 0),
        losses INTEGER NOT NULL DEFAULT 0 CHECK(losses >= 0),
        last_included_round_id TEXT NULL,
        updated_at TEXT NOT NULL,
        stats_version INTEGER NOT NULL CHECK(stats_version >= 1),
        PRIMARY KEY(character_id, regime_id),
        FOREIGN KEY(character_id, regime_id) REFERENCES history_regimes(character_id, regime_id) ON DELETE RESTRICT,
        FOREIGN KEY(last_included_round_id) REFERENCES rounds(round_id) ON DELETE RESTRICT,
        CHECK(included_games = wins + losses),
        CHECK((included_games = 0 AND last_included_round_id IS NULL) OR (included_games > 0 AND last_included_round_id IS NOT NULL))
    )
    """,
    """
    CREATE TABLE meta (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
)

_INDEX_DDL = (
    "CREATE UNIQUE INDEX ux_history_regimes_active ON history_regimes(character_id) WHERE active = 1",
    "CREATE UNIQUE INDEX ux_rounds_pending ON rounds(status) WHERE status = 'pending'",
    "CREATE UNIQUE INDEX ux_rounds_supersedes ON rounds(supersedes_round_id) WHERE supersedes_round_id IS NOT NULL",
    "CREATE INDEX ix_rounds_calculated_at ON rounds(calculated_at)",
    "CREATE INDEX ix_rounds_eligible_history ON rounds(character_id, history_regime_id, calculated_at, round_id) WHERE status = 'completed' AND include_character_history = 1",
)


def initialize_v1(
    connection: sqlite3.Connection, fault_hook: Callable[[], None] | None = None
) -> None:
    """Create and seed schema v1 as one explicit transaction."""
    now = serialize_utc(datetime.now(UTC))
    connection.execute("BEGIN IMMEDIATE")
    try:
        for statement in _DDL:
            connection.execute(statement)
        for statement in _INDEX_DDL:
            connection.execute(statement)
        connection.executemany(
            "INSERT INTO characters(character_id, internal_code, display_name, tainted, pair_row, active) VALUES (?, ?, ?, ?, ?, 1)",
            CHARACTERS,
        )
        regimes = [
            (f"regime-1-{character_id}", character_id, 1, now, 1) for character_id, *_ in CHARACTERS
        ]
        connection.executemany(
            "INSERT INTO history_regimes(regime_id, character_id, regime_number, started_at, active) VALUES (?, ?, ?, ?, ?)",
            regimes,
        )
        connection.executemany(
            "INSERT INTO character_stats(character_id, regime_id, updated_at, stats_version) VALUES (?, ?, ?, 1)",
            [(character_id, f"regime-1-{character_id}", now) for character_id, *_ in CHARACTERS],
        )
        connection.execute(
            "INSERT INTO meta(key, value, updated_at) VALUES ('schema_initialized', '1', ?)", (now,)
        )
        if fault_hook is not None:
            fault_hook()
        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
