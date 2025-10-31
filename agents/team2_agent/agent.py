from google.adk.agents import SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from .sub_agents import pre_flop_agent, format_agent

MODEL_GPT_4_O_MINI = LiteLlm(model="openai/gpt-4o-mini")

AGENT_MODEL = MODEL_GPT_4_O_MINI

root_agent = SequentialAgent(
    name="poker_workflow_agent",
    model=AGENT_MODEL,
    sub_agents=[pre_flop_agent.root_agent, format_agent.root_agent],
    description="This agent orchestrates the pre-flop and formatting sub-agents to make decisions in Texas Hold'em poker."
)
