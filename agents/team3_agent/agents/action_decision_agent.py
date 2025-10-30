from google.adk.agents import Agent
from ..tools.action_decision import action_decision

MODEL_GEMINI_2_5_FLASH = "gemini-2.5-flash"
action_decision_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model = MODEL_GEMINI_2_5_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # If you would like to experiment with other models
        name="action_decision_agent",
        instruction="期待値を算出するagent 結果はjsonで返す? actionとreasoningだけ埋めた状態",
        description="Handles simple greetings and hellos using the 'say_hello' tool.", # Crucial for delegation
        tools=[action_decision],
    )
