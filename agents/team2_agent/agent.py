from google.adk.agents import SequentialAgent
from .sub_agents import pre_flop_agent, format_agent

root_agent = SequentialAgent(
    name="poker_workflow_agent",
    sub_agents=[pre_flop_agent.root_agent, format_agent.root_agent],
    description="This agent orchestrates the pre-flop and formatting sub-agents to make decisions in Texas Hold'em poker."
)
