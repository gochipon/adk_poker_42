"""
U2 Agent - Math Brain

The mathematical core that handles:
- Equity calculations
- Pot odds analysis
- SPR-based decisions
- Tournament-aware strategy adjustments

This brain ALWAYS runs and provides baseline recommendations.
"""

from typing import Dict, Any, List
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from agents.team4_agent.config.constants import (
    TOURNAMENT_CONFIG, TOURNAMENT_PHASES, STACK_THRESHOLDS,
    RISK_PROFILES, RAISE_SIZING, EQUITY_THRESHOLDS
)
from agents.team4_agent.config.ranges import (
    hand_to_notation, get_hand_strength_category,
    should_open_from_position, should_3bet,
    PREMIUM_HANDS, STRONG_HANDS
)
from agents.team4_agent.tools.equity_calculator import (
    quick_equity_estimate, get_preflop_equity_estimate,
    calculate_pot_odds, calculate_spr
)


class MathBrain:
    """
    Mathematical analysis engine for poker decisions.
    Provides equity-based recommendations with tournament awareness.
    """

    def __init__(self):
        self.bb = TOURNAMENT_CONFIG["big_blind"]

    def analyze(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis entry point.

        Returns a structured recommendation with:
        - action: fold/check/call/raise/all_in
        - amount: bet amount
        - confidence: 0.0-1.0
        - equity: estimated equity
        - reasoning: explanation
        """
        # Extract state
        phase = game_state.get("phase", "preflop")
        hero_cards = game_state.get("your_cards", [])
        community = game_state.get("community", [])
        hero_chips = game_state.get("your_chips", 0)
        pot = game_state.get("pot", 0)
        to_call = game_state.get("to_call", 0)
        players = game_state.get("players", [])
        hand_number = game_state.get("hand_number", 1)
        dealer_button = game_state.get("dealer_button", 0)
        your_id = game_state.get("your_id", 0)

        # Calculate derived metrics
        opponent_count = len([p for p in players if p.get("status") == "active"])
        stack_bb = hero_chips / self.bb
        pot_odds = calculate_pot_odds(to_call, pot)
        spr = calculate_spr(hero_chips, pot)

        # Determine position
        position = self._get_position(your_id, dealer_button, len(players) + 1)

        # Determine tournament phase and risk profile
        tournament_phase = self._get_tournament_phase(hand_number)
        risk_profile = self._get_risk_profile(stack_bb, hand_number, hero_chips, pot, players)

        # Calculate equity with adaptive simulations
        if phase == "preflop":
            hand_notation = hand_to_notation(hero_cards)
            hand_category = get_hand_strength_category(hand_notation)
            equity = get_preflop_equity_estimate(hand_category, opponent_count)
        else:
            # Adaptive simulations based on importance
            sim_count = self._get_simulation_count(phase, pot, to_call)
            equity = quick_equity_estimate(hero_cards, opponent_count, community, simulations=sim_count)

        # Make decision based on phase
        if phase == "preflop":
            decision = self._analyze_preflop(
                hero_cards, to_call, pot, hero_chips, position,
                equity, pot_odds, risk_profile, opponent_count
            )
        else:
            decision = self._analyze_postflop(
                hero_cards, community, to_call, pot, hero_chips,
                equity, pot_odds, spr, risk_profile, phase
            )

        # Add tournament context
        decision["tournament_phase"] = tournament_phase
        decision["risk_profile"] = risk_profile
        decision["position"] = position
        decision["stack_bb"] = stack_bb
        decision["equity"] = equity
        decision["pot_odds_required"] = pot_odds
        decision["spr"] = spr

        return decision

    def _get_position(self, your_id: int, dealer_button: int, total_players: int) -> str:
        """Calculate position relative to button"""
        # In 5-max: BTN, SB, BB, UTG, HJ
        # Fix: Add total_players to avoid negative modulo
        positions_from_button = (your_id - dealer_button + total_players) % total_players

        if positions_from_button == 0:
            return "BTN"
        elif positions_from_button == 1:
            return "SB"
        elif positions_from_button == 2:
            return "BB"
        elif positions_from_button == 3:
            return "UTG"
        else:
            return "HJ"

    def _get_tournament_phase(self, hand_number: int) -> str:
        """Determine tournament phase"""
        for phase_name, (start, end) in TOURNAMENT_PHASES.items():
            if start <= hand_number <= end:
                return phase_name
        return "late"

    def _get_simulation_count(self, phase: str, pot: int, to_call: int) -> int:
        """
        Ultra-fast simulations for timeout safety.
        Multi-match: better fast decision than timeout!
        """
        # Critical decision (big bet)
        if to_call > pot * 0.75:
            return 200  # Was 400 -> 50% reduction
        elif phase == "river":
            return 150  # Was 300 -> 50% reduction
        elif phase == "turn":
            return 125  # Was 250 -> 50% reduction
        else:  # flop
            return 100  # Was 200 -> 50% reduction

    def _get_risk_profile(self, stack_bb: float, hand_number: int,
                         hero_chips: int, pot: int, players: List[Dict]) -> str:
        """Simplified risk profile - ONLY based on stack size (chip EV focus)"""

        # Push/fold zone
        if stack_bb < 8:
            return "push_fold"

        # Short stack
        elif stack_bb < 15:
            return "short_stack"

        # Deep stack
        elif stack_bb > 50:
            return "deep"

        # Normal stack (default)
        else:
            return "normal"

    def _analyze_preflop(self, hero_cards: List[str], to_call: int, pot: int,
                        hero_chips: int, position: str, equity: float,
                        pot_odds: float, risk_profile: str, opponent_count: int) -> Dict:
        """Preflop decision logic"""

        hand_notation = hand_to_notation(hero_cards)
        hand_category = get_hand_strength_category(hand_notation)

        facing_raise = to_call > self.bb

        # Get risk profile settings
        profile = RISK_PROFILES[risk_profile]
        aggression_mult = profile["aggression_multiplier"]

        if not facing_raise:
            # No raise - decide to open or fold
            # BB special case: already invested, can check/raise
            if position == "BB" and to_call == 0:
                # Raise premium/strong hands even from BB
                if hand_notation in (PREMIUM_HANDS | STRONG_HANDS):
                    raise_size = int(self.bb * RAISE_SIZING["preflop_open"] * aggression_mult)
                    raise_size = min(raise_size, hero_chips)
                    return {
                        "action": "raise",
                        "amount": raise_size,
                        "confidence": 0.85,
                        "reasoning": f"Raise {hand_category} from BB"
                    }
                # Check marginal/weak (free to see flop)
                else:
                    return {
                        "action": "check",
                        "amount": 0,
                        "confidence": 0.8,
                        "reasoning": f"Check {hand_category} in BB"
                    }

            # Multi-tournament: only open with solid equity
            if should_open_from_position(hand_notation, position):
                # Premium/strong - always open
                if hand_notation in (PREMIUM_HANDS | STRONG_HANDS):
                    raise_size = int(self.bb * RAISE_SIZING["preflop_open"] * aggression_mult)
                    raise_size = min(raise_size, hero_chips)
                    return {
                        "action": "raise",
                        "amount": raise_size,
                        "confidence": 0.85,
                        "reasoning": f"Open {hand_category} from {position}"
                    }
                # Marginal hands - position matters
                elif equity > 0.52:
                    # Only from CO/BTN (good position)
                    if position in ["CO", "BTN"]:
                        raise_size = int(self.bb * RAISE_SIZING["preflop_open"] * aggression_mult)
                        raise_size = min(raise_size, hero_chips)
                        return {
                            "action": "raise",
                            "amount": raise_size,
                            "confidence": 0.75,
                            "reasoning": f"Open {hand_category} from {position}"
                        }
                    # UTG/HJ/SB - fold marginal (out of position)
                    else:
                        return {
                            "action": "fold",
                            "amount": 0,
                            "confidence": 0.75,
                            "reasoning": f"Fold {hand_category} from {position}"
                        }
                else:
                    # Weak equity - fold
                    return {
                        "action": "fold",
                        "amount": 0,
                        "confidence": 0.7,
                        "reasoning": f"Fold {hand_category}"
                    }
            else:
                # Not in range - fold
                return {
                    "action": "fold",
                    "amount": 0,
                    "confidence": 0.9,
                    "reasoning": f"Fold {hand_category} from {position}"
                }
        else:
            # Facing raise - decide 3bet/call/fold
            # Multi-tournament: conservative 3-betting
            if should_3bet(hand_notation, position):
                # Premium hands - 3-bet for value
                if hand_notation in PREMIUM_HANDS:
                    three_bet_size = int(to_call * 3 * aggression_mult)
                    three_bet_size = min(three_bet_size, hero_chips)
                    return {
                        "action": "raise",
                        "amount": three_bet_size,
                        "confidence": 0.90,
                        "reasoning": f"3-bet {hand_category} for value"
                    }
                # Strong hands - 3-bet if equity strong
                elif hand_notation in STRONG_HANDS and equity > 0.58:
                    three_bet_size = int(to_call * 3 * aggression_mult)
                    three_bet_size = min(three_bet_size, hero_chips)
                    return {
                        "action": "raise",
                        "amount": three_bet_size,
                        "confidence": 0.80,
                        "reasoning": f"3-bet {hand_category} with {equity:.1%} equity"
                    }
                # Bluff 3-bets - skip for multi-tournament consistency
                # Fall through to call logic

            # Check if we should call - only premium hands
            # Multi-tournament: avoid variance on 3-bet calls
            if hand_notation in PREMIUM_HANDS:
                if equity >= pot_odds * 1.10:  # Small edge OK for premium
                    return {
                        "action": "call",
                        "amount": to_call,
                        "confidence": 0.80,
                        "reasoning": f"Call {hand_category} vs 3-bet"
                    }
            # Strong hands - need good equity
            elif hand_notation in STRONG_HANDS and equity >= pot_odds * 1.20:
                return {
                    "action": "call",
                    "amount": to_call,
                    "confidence": 0.70,
                    "reasoning": f"Call {hand_category} {equity:.1%} equity"
                }
            # Marginal hands - fold (too much variance)
            # Don't call 3-bets with speculative hands

            # Otherwise fold
            return {
                "action": "fold",
                "amount": 0,
                "confidence": 0.8,
                "reasoning": f"Fold {hand_category} - insufficient edge for multi-tournament consistency"
            }

    def _analyze_postflop(self, hero_cards: List[str], community: List[str],
                         to_call: int, pot: int, hero_chips: int,
                         equity: float, pot_odds: float, spr: float,
                         risk_profile: str, phase: str) -> Dict:
        """Postflop decision logic - CHIP EV FOCUS (multi-match format)"""

        profile = RISK_PROFILES[risk_profile]
        aggression_mult = profile["aggression_multiplier"]
        equity_margin = profile["equity_margin"]

        # Low SPR - commit if equity good enough
        if spr < 2 and equity > EQUITY_THRESHOLDS["all_in"]:
            return {
                "action": "all_in",
                "amount": hero_chips,
                "confidence": 0.85,
                "reasoning": f"All-in low SPR ({spr:.1f}) {equity:.1%} equity"
            }

        # Facing bet - simple pot odds decision
        if to_call > 0:
            # Calculate required equity (pot odds + margin)
            required_equity = pot_odds * equity_margin

            # Very strong equity - raise for value
            if equity > EQUITY_THRESHOLDS["value_raise"]:
                raise_size = int(pot * RAISE_SIZING["postflop_value"] * aggression_mult)
                raise_size = max(raise_size, to_call * 2)
                raise_size = min(raise_size, hero_chips)
                return {
                    "action": "raise",
                    "amount": raise_size,
                    "confidence": 0.80,
                    "reasoning": f"Value raise {equity:.1%} equity"
                }

            # Good equity - call if +EV
            elif equity >= required_equity:
                return {
                    "action": "call",
                    "amount": to_call,
                    "confidence": 0.75,
                    "reasoning": f"+EV call: {equity:.1%} vs {required_equity:.1%} required"
                }

            # -EV fold
            else:
                return {
                    "action": "fold",
                    "amount": 0,
                    "confidence": 0.85,
                    "reasoning": f"-EV fold: {equity:.1%} < {required_equity:.1%}"
                }

        # No bet to call - betting logic
        else:
            # Strong equity - bet for value
            if equity > EQUITY_THRESHOLDS["raise"]:
                bet_size = int(pot * RAISE_SIZING["postflop_value"] * aggression_mult)
                bet_size = min(bet_size, hero_chips)
                return {
                    "action": "raise",
                    "amount": bet_size,
                    "confidence": 0.75,
                    "reasoning": f"Value bet {equity:.1%} equity"
                }
            # Semi-bluff with decent equity
            elif equity > 0.48 and phase == "flop":
                bet_size = int(pot * RAISE_SIZING["postflop_cbet"] * aggression_mult)
                bet_size = min(bet_size, hero_chips)
                return {
                    "action": "raise",
                    "amount": bet_size,
                    "confidence": 0.65,
                    "reasoning": f"Semi-bluff {equity:.1%} equity"
                }
            # Marginal - check
            else:
                return {
                    "action": "check",
                    "amount": 0,
                    "confidence": 0.70,
                    "reasoning": f"Check {equity:.1%} equity"
                }


def math_brain_analyze(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function for use as a tool.
    """
    brain = MathBrain()
    return brain.analyze(game_state)
