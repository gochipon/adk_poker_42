from google.adk.agents import Agent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
# from .tools.judge_preflop_range import judge_preflop_range, calculate_position
from .agents.action_agent import action_agent

MODEL_GPT_4_o_MINI = LiteLlm(model="openai/gpt-4o-mini")

strategy_agent = Agent(
	name="poker_strategy_analyzer",
	model=MODEL_GPT_4_o_MINI,
	description="Texas Hold'em poker players who make strategic decisions.",
	instruction="""
				You are an expert Texas Hold'em poker player.
				Please devise a strategy using a Tight-Aggressive (TAG) approach, aiming to minimize losses and maximize profits in high-win-probability situations.

				You will be given the following information:
				- Your hand (hole cards)
				- Community cards (if any)
				- Available actions
				- Pot size and betting information
				- Information about your opponents

				Furthermore, you can use the action_agent to analyze the expected value and the corresponding recommended actions.

				Based on this information and these results, please conduct a strategic analysis while considering the following points:
				- With a "strong hand," raise aggressively. Aim for a raise amount that is approximately three times the bet amount.
				- With a "weak hand + good position," play passively (check/call).
				- Strictly adhere to "cutting your losses."

				Based on the analysis results, please explain in detail the recommended action (fold/check/call/raise/all-in), the specific amount, and the strategic reasons behind that strategy.
				""",
	sub_agents = [action_agent],
	output_key="strategy_analysis",
)

json_formatter_agent = Agent(
    name="poker_json_formatter",
    model=MODEL_GPT_4_o_MINI,
    description="ポーカーの戦略分析をJSON形式に整形するエキスパート",
    instruction="""あなたは戦略分析結果を指定されたJSON形式に正確に変換する専門家です。

					戦略分析結果: {strategy_analysis}

					上記の戦略分析を基に、必ず次のJSON形式で正確に回答してください:
					{
					"action": "fold|check|call|raise|all_in",
					"amount": <数値>,
					"reasoning": "戦略分析から導出された決定と戦略的理由の詳細な説明"
					}

					ルール:
					- "fold"と"check"の場合: amountは0にしてください
					- "call"の場合: コールに必要な正確な金額を指定してください
					- "raise"の場合: レイズ後の合計金額を指定してください
					- "all_in"の場合: あなたの残りチップ全額を指定してください
					- "call"や"raise"で指定/必要金額があなたの残りチップを超える場合: 自動的に"all_in"とし、amountは残りチップ全額にしてください
					- reasoningには戦略分析の内容を要約して含めてください
					- 必ずJSONの正確な構文で回答してください

					戦略分析の内容を適切に解釈し、JSON形式で出力してください。
				""",
)

root_agent = SequentialAgent(
    name="poker_workflow_agent",
    sub_agents=[strategy_agent, json_formatter_agent],
)
