from google.adk.agents import Agent
from ..tools.action_decision import action_decision

MODEL_GEMINI_2_5_FLASH = "gemini-2.5-flash"
action_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model = MODEL_GEMINI_2_5_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # If you would like to experiment with other models
        name="action_agent",
        instruction="期待値を算出するし、アクション結果をjson形式で返す",
        description="あなたは期待値を算出して、アクションを決定するエージェントです。"
					"受け取ったjsonの内容から期待値を算出して、action_decisionに引数として渡してください。"
					"これに加え、action_decisionには受け取ったjsonも渡してください。"
					"action_decisionの結果を、ユーザーに出力してください。" ,# Crucial for delegation
        tools=[action_decision]
    )
