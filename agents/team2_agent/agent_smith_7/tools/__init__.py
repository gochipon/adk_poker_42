"""
Utility wrappers that expose poker calculation helpers as ADK tools.

Each function returns simple JSON-serialisable data so that the LLM agent can
request quantitative support during decision making.
"""

from __future__ import annotations

from .position_tool import get_position_label
from .preflop_hand_value_tool import PreflopHandValueTool
from .preflop_ev_tool import PreflopEVTool
from .pot_odds_tool import calc_pot_odds
from .postflop_ev_tool import PostflopEVTool

_preflop_value_tool = PreflopHandValueTool()
_preflop_ev_tool = PreflopEVTool()
_postflop_ev_tool = PostflopEVTool()


async def get_table_position(
    seat_index: int,
    total_players: int = 5,
    dealer_index: int = 0,
) -> str:
    """
    Determine the relative table position label for the given seat.

    Args:
        seat_index: Your current seat index (0-based).
        total_players: Total number of active seats (default: 5).
        dealer_index: Dealer button seat index.

    Returns:
        Position label such as "UTG", "MP", "CO", "BTN", or "SB".
    """

    return get_position_label(
        seat_index=seat_index,
        total_players=total_players,
        dealer_index=dealer_index,
    )


async def evaluate_preflop_hand_value(hole_cards: list[str]) -> float:
    """
    Rate the intrinsic preflop hand strength on a 0.0–1.0 scale.

    Args:
        hole_cards: Two card strings like ["Ah", "Kd"].

    Returns:
        Strength score where 1.0 is a premium hand and 0.5 is average.
    """

    return _preflop_value_tool.evaluate(list(hole_cards))


async def compute_preflop_ev(
    hole_cards: list[str],
    position: str,
    stack: float,
    call_amount: float,
    num_active_players: int = 5,
    opponent_aggression: float = 0.5,
) -> float:
    """
    Calculate the adjusted preflop expected value for the current situation.

    Args:
        hole_cards: Two card strings like ["Ah", "Kd"].
        position: Table position label (例: "UTG", "MP", "CO", "BTN", "SB").
        stack: Your effective stack size.
        call_amount: Chips required to continue.
        num_active_players: Number of active opponents.
        opponent_aggression: Estimated aggression level (0.0–1.0).

    Returns:
        EV score where 1.0 or higher is strongly profitable.
    """

    effective_call = float(call_amount or 0)
    if effective_call <= 0:
        effective_call = 1.0

    return _preflop_ev_tool.evaluate(
        hole_cards=list(hole_cards),
        position=position,
        stack=float(stack),
        call_amount=effective_call,
        num_active=num_active_players,
        opponent_aggression=float(opponent_aggression),
    )


async def calculate_pot_odds(pot_size: float, call_amount: float) -> float:
    """
    Compute the pot odds required to justify a call.

    Args:
        pot_size: Current pot size before your decision.
        call_amount: Chips required to continue.

    Returns:
        Pot odds ratio (call / (pot + call)).
    """

    return float(calc_pot_odds(float(pot_size), float(call_amount)))


__all__ = [
    "get_table_position",
    "evaluate_preflop_hand_value",
    "compute_preflop_ev",
    "calculate_pot_odds",
]
