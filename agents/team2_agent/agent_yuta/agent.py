from google.adk.agents import SequentialAgent
from .sub_agents import (
    action_decision_agent,
    board_texture_agent,
    hand_validation_agent,
    bet_amount_agent,
    format_agent,
)

root_agent = SequentialAgent(
    name="team2_poker_workflow_agent",
    description=(
        "This agent orchestrates action selection, board texture analysis, hand validation, "
        "bet sizing, and final formatting sub-agents to make well-structured poker decisions."
    ),
    sub_agents=[
        action_decision_agent.root_agent,
        board_texture_agent.root_agent,
        hand_validation_agent.root_agent,
        bet_amount_agent.root_agent,
        format_agent.root_agent,
    ],
)
