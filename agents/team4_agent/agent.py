"""
U2 Agent - Ultra-Nimble Adaptive Gaming Intelligence

Main agent that combines mathematical analysis with LLM decision making.
Optimized for 30-hand tournament format with 5 players.

Strategy:
- Math Brain provides solid baseline recommendations
- LLM makes final decision with tournament context
- Fallback to Math Brain if LLM fails
"""

from typing import Dict, Any
import sys
import signal
from pathlib import Path
from contextlib import contextmanager

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from agents.team4_agent.brains.math_brain import math_brain_analyze
from agents.team4_agent.tools.action_validator import (
    sanitize_recommendation,
    get_safe_fallback_action
)

# Global state for fallback
LAST_RECOMMENDATION: Dict[str, Any] = None


@contextmanager
def timeout_protection(seconds: int):
    """Context manager for timeout protection"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation exceeded {seconds} seconds")

    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def unagi_strategy_tool(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main strategy tool with timeout protection and action validation.

    CRITICAL: Must complete in <25s to leave time for LLM response.
    """
    global LAST_RECOMMENDATION

    try:
        # Timeout protection: max 25 seconds (leave 15s for LLM + network)
        with timeout_protection(25):
            recommendation = math_brain_analyze(game_state)

        # Validate and sanitize action
        safe_recommendation = sanitize_recommendation(recommendation, game_state)

        # Store for fallback
        LAST_RECOMMENDATION = safe_recommendation

        # Return structured recommendation
        return {
            "recommended_action": safe_recommendation["action"],
            "recommended_amount": safe_recommendation["amount"],
            "confidence": safe_recommendation["confidence"],
            "equity": safe_recommendation["equity"],
            "reasoning": safe_recommendation["reasoning"],
            "tournament_phase": safe_recommendation.get("tournament_phase", "unknown"),
            "risk_profile": safe_recommendation.get("risk_profile", "normal"),
            "position": safe_recommendation.get("position", "unknown"),
            "stack_bb": safe_recommendation.get("stack_bb", 0),
            "pot_odds_required": safe_recommendation.get("pot_odds_required", 0),
            "spr": safe_recommendation.get("spr", 0),
        }

    except TimeoutError:
        # TIMEOUT! Use ultra-fast fallback
        fallback = get_safe_fallback_action(game_state)
        fallback["reasoning"] = f"TIMEOUT! {fallback['reasoning']}"
        LAST_RECOMMENDATION = fallback
        return {
            "recommended_action": fallback["action"],
            "recommended_amount": fallback["amount"],
            "confidence": fallback["confidence"],
            "reasoning": fallback["reasoning"]
        }

    except Exception as e:
        # Any other error - safe fallback
        fallback = get_safe_fallback_action(game_state)
        fallback["reasoning"] = f"Error: {type(e).__name__}. {fallback['reasoning']}"
        LAST_RECOMMENDATION = fallback
        return {
            "recommended_action": fallback["action"],
            "recommended_amount": fallback["amount"],
            "confidence": fallback["confidence"],
            "reasoning": fallback["reasoning"]
        }


# Main agent definition
root_agent = Agent(
    name="u2_poker_agent",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    description="U2 - Tournament poker agent optimized for 30-hand format",

    tools=[unagi_strategy_tool],

    instruction="""You are U2, an expert poker agent optimized for MULTI-TOURNAMENT consistency.

FORMAT: 30 tournaments × 30 hands. Total chips across ALL tournaments determines winner.

CRITICAL: This is NOT single-tournament - CONSISTENCY beats variance!

DECISION PROCESS:

1. TOOL CALL (MANDATORY)
Call unagi_strategy_tool with game_state parameter:
unagi_strategy_tool(game_state=<the full JSON from user message>)

CRITICAL: You MUST pass game_state parameter! Do NOT call without it.

2. ANALYZE TOOL OUTPUT
Tool returns recommended_action, equity, position, risk_profile, reasoning.

3. MAKE DECISION
- TRUST the tool - it's optimized for multi-tournament EV
- Avoid coin flips (50/50 gambles) - need EDGE
- Only deviate if tool clearly wrong
- Short stack (<15 BB): Careful aggression
- Critical short (<8 BB): Push/fold

4. RETURN JSON (no markdown)
{
  "action": "fold|check|call|raise|all_in",
  "amount": <number>,
  "reasoning": "Brief explanation"
}

ACTION RULES:
- fold/check: amount = 0
- call: amount = exact to_call
- raise: amount = TOTAL bet
- all_in: amount = remaining chips

STRATEGY: CONSERVATIVE & CONSISTENT

All phases: Solid play, avoid high variance
Stack-based adjustments:
- Deep (>40 BB): Cautious, protect
- Normal (15-40 BB): Balanced
- Short (8-15 BB): Aggressive
- Critical (<8 BB): Push/fold

EQUITY THRESHOLDS (conservative):
- Equity >65%: ALL-IN acceptable
- Equity >60%: RAISE for value
- Equity >45%: CALL (with margin over pot odds)
- Equity <45%: FOLD (unless great pot odds)

KEY PRINCIPLES:
- Multi-tournament = consistency > variance
- Need EDGE (55%+ equity), not coin flips
- Position matters: BTN/CO wider, UTG tight
- Chip EV focus (no ICM)

EXAMPLE:
Hand 15, BTN with A9s, 52% equity vs raise:
{
  "action": "fold",
  "reasoning": "Marginal edge - avoid variance for multi-tournament EV"
}

NOW: Call tool, trust it, return JSON!
""",
)


if __name__ == "__main__":
    print(f"Agent: {root_agent.name}")
    print(f"Model: {root_agent.model}")
    print(f"Tools: {len(root_agent.tools)}")
