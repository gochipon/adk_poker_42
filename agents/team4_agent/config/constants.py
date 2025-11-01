"""
U2 Agent - Tournament Constants and Thresholds

Optimized for 30-hand tournament format with 5 players.
"""

# Tournament Configuration
TOURNAMENT_CONFIG = {
    "starting_stack": 2000,
    "small_blind": 10,
    "big_blind": 20,
    "total_hands": 30,
    "players": 5,
    "time_limit_seconds": 40,
}

# Tournament Phases (critical for 30-hand format)
TOURNAMENT_PHASES = {
    "early": (1, 10),      # Hands 1-10: Build stack, gather intel
    "middle": (11, 20),    # Hands 11-20: Exploit opponents
    "late": (21, 30),      # Hands 21-30: Aggressive maximization
}

# Stack Thresholds (in BB)
STACK_THRESHOLDS = {
    "critical_short": 8,    # <8 BB: Push/fold mode
    "short": 15,            # <15 BB: Aggressive mode
    "medium": 40,           # 15-40 BB: Balanced
    "deep": 100,            # >40 BB: Deep stack play
}

# Risk Profiles - Simplified for chip EV (based on stack size only)
RISK_PROFILES = {
    "push_fold": {
        "description": "Critical short stack (<8 BB) - push/fold only",
        "aggression_multiplier": 2.5,
        "equity_margin": 1.0,  # Play strict pot odds
    },
    "short_stack": {
        "description": "Short stack (8-15 BB) - aggressive",
        "aggression_multiplier": 1.5,
        "equity_margin": 1.05,  # 5% margin
    },
    "normal": {
        "description": "Normal stack (15-50 BB) - chip EV optimal",
        "aggression_multiplier": 1.0,
        "equity_margin": 1.10,  # 10% margin
    },
    "deep": {
        "description": "Deep stack (>50 BB) - wider ranges",
        "aggression_multiplier": 0.9,
        "equity_margin": 1.10,
    },
}

# Raise Sizing (in BB)
RAISE_SIZING = {
    "preflop_open": 3.0,        # Standard open raise
    "preflop_3bet": 8.0,        # 3-bet sizing
    "preflop_4bet": 18.0,       # 4-bet sizing
    "postflop_cbet": 0.66,      # C-bet as % of pot
    "postflop_value": 0.75,     # Value bet as % of pot
    "postflop_bluff": 0.50,     # Bluff sizing as % of pot
}

# Equity thresholds - Chip EV focus (multi-match format)
# NOTE: 30+ matches means each chip has LINEAR value (not ICM)
# Lower thresholds = more +EV decisions = higher average profit
EQUITY_THRESHOLDS = {
    "fold": 0.30,      # Fold if clearly -EV
    "call": 0.40,      # Call with margin over pot odds
    "raise": 0.52,     # Raise with slight edge
    "value_raise": 0.58,  # Value raises
    "all_in": 0.60,    # All-in only needs 60% (not 65%!)
}
