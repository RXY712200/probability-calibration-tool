"""Display-only conversion; never changes model inputs or stored values."""


def format_probability(value: float) -> str:
    return f"{value:.1%}"


def format_ev(value: float) -> str:
    return f"{value:+.3f}"


def format_odds(value: float) -> str:
    return f"{value:.4g}"


def format_timestamp(value, timezone=None) -> str:
    return value.astimezone(timezone).strftime("%Y-%m-%d %H:%M:%S")
