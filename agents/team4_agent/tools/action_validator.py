"""
U2 Agent - Action Validator

Validates and sanitizes actions to prevent disqualification.
CRITICAL: Invalid actions can lead to timeout or forfeit.
"""

from typing import Dict, Tuple, Any


def validate_and_fix_action(action: str, amount: int, game_state: Dict[str, Any]) -> Tuple[str, int, str]:
    """
    Validates and corrects invalid actions.

    Returns: (safe_action, safe_amount, fix_message)
    """
    your_chips = game_state.get("your_chips", 0)
    to_call = game_state.get("to_call", 0)
    pot = game_state.get("pot", 0)

    # Calculate min_raise
    current_bet = game_state.get("your_bet_this_round", 0)
    min_raise = to_call * 2 if to_call > 0 else 20  # BB if no raise

    # Fix 1: amount exceeds stack -> all-in
    if amount > your_chips:
        return "all_in", your_chips, f"Fixed: amount {amount} > stack {your_chips}"

    # Fix 2: raise too small -> call instead
    if action == "raise":
        if amount < min_raise:
            if to_call <= your_chips:
                return "call", to_call, f"Fixed: raise {amount} < min {min_raise}, calling"
            else:
                return "fold", 0, f"Fixed: raise invalid, insufficient chips"

        # Fix: raise amount exceeds stack -> all-in
        if amount > your_chips:
            return "all_in", your_chips, f"Fixed: raise amount > stack"

    # Fix 3: call amount incorrect -> use exact to_call
    if action == "call":
        if to_call > your_chips:
            # Check if we should call all-in
            pot_odds = to_call / (pot + to_call) if (pot + to_call) > 0 else 1.0
            if pot_odds < 0.33:  # Good pot odds
                return "all_in", your_chips, f"Fixed: calling all-in with good pot odds"
            else:
                return "fold", 0, f"Fixed: insufficient chips to call"

        # Always use exact to_call amount
        if amount != to_call:
            return "call", to_call, f"Fixed: call amount {amount} -> {to_call}"

    # Fix 4: fold when can check (free) -> check
    if action == "fold" and to_call == 0:
        return "check", 0, f"Fixed: checking instead of folding (free)"

    # Fix 5: check when facing bet -> fold
    if action == "check" and to_call > 0:
        return "fold", 0, f"Fixed: cannot check when facing bet"

    # Fix 6: negative or zero raise -> fold
    if action == "raise" and amount <= 0:
        return "fold", 0, f"Fixed: invalid raise amount {amount}"

    # Fix 7: all-in with amount != stack
    if action == "all_in" and amount != your_chips:
        return "all_in", your_chips, f"Fixed: all-in amount {amount} -> {your_chips}"

    # Action is valid
    return action, amount, ""


def sanitize_recommendation(recommendation: Dict[str, Any], game_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitizes recommendation dict from math_brain.

    Returns: cleaned recommendation with valid action/amount
    """
    action = recommendation.get("action", "fold")
    amount = recommendation.get("amount", 0)
    reasoning = recommendation.get("reasoning", "")

    # Validate and fix
    safe_action, safe_amount, fix_msg = validate_and_fix_action(action, amount, game_state)

    # Update reasoning if fixed
    if fix_msg:
        reasoning = f"{fix_msg}. {reasoning}"

    # Return sanitized recommendation
    return {
        "action": safe_action,
        "amount": safe_amount,
        "confidence": recommendation.get("confidence", 0.5),
        "equity": recommendation.get("equity", 0.5),
        "reasoning": reasoning,
        "tournament_phase": recommendation.get("tournament_phase", "unknown"),
        "risk_profile": recommendation.get("risk_profile", "normal"),
        "position": recommendation.get("position", "unknown"),
        "stack_bb": recommendation.get("stack_bb", 0),
        "pot_odds_required": recommendation.get("pot_odds_required", 0),
        "spr": recommendation.get("spr", 0),
    }


def get_safe_fallback_action(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns ultra-safe fallback action when everything fails.

    Priority: check > fold > call (never raise without calculation)
    """
    to_call = game_state.get("to_call", 0)
    pot = game_state.get("pot", 0)
    your_chips = game_state.get("your_chips", 0)

    # No bet - check (safest)
    if to_call == 0:
        return {
            "action": "check",
            "amount": 0,
            "confidence": 0.5,
            "reasoning": "Emergency fallback: check"
        }

    # Small bet with good pot odds - call
    pot_odds = to_call / (pot + to_call) if (pot + to_call) > 0 else 1.0
    bet_ratio = to_call / your_chips if your_chips > 0 else 1.0

    if pot_odds < 0.25 and bet_ratio < 0.15:  # Great pot odds + small risk
        return {
            "action": "call",
            "amount": to_call,
            "confidence": 0.4,
            "reasoning": f"Emergency fallback: calling good pot odds ({pot_odds:.1%})"
        }

    # Otherwise fold
    return {
        "action": "fold",
        "amount": 0,
        "confidence": 0.6,
        "reasoning": "Emergency fallback: fold"
    }
