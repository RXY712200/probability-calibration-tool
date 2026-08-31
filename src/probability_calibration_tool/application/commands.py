from dataclasses import dataclass


@dataclass(frozen=True)
class CalculateCommand:
    character_id: int
    reference_history: bool
    p_h_raw: int
    win_odds_raw: str
    lose_odds_raw: str
