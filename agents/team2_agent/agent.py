from google.adk.agents import SequentialAgent
from .sub_agents import (
    action_decision_agent,
    hand_validation_agent,
    bet_amount_agent,
    format_agent,
)

root_agent = SequentialAgent(
    name="team2_poker_workflow_agent",
    description=(
        "This agent orchestrates the action decision, hand validation, bet sizing, "
        "and formatting sub-agents to make well-structured poker decisions."
    ),
    sub_agents=[
        action_decision_agent.root_agent,
        hand_validation_agent.root_agent,
        bet_amount_agent.root_agent,
        format_agent.root_agent,
    ],
)
