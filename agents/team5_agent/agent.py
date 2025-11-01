from google.adk.agents import Agent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from team5_agent.agents.poker_rank_agent import hand_rank_evaluator_agent
from .agents.preflop_strategy_agent import preflop_strategy_agent
from .agents.postflop_strategy_agent import postflop_strategy_agent
from .agents.poker_rank_agent import hand_rank_evaluator_agent

AGENT_MODEL = LiteLlm(model="openai/gpt-4o-mini")

return_agent = Agent(
    name="team5_agent",
    model=AGENT_MODEL,
    description="ポーカーの戦略分析をJSON形式に整形するエキスパート",
    instruction="""あなたは戦略分析結果を指定されたJSON形式に正確に変換する専門家です。

戦略分析結果：{strategy_analysis}
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
    """,
    )

root_agent = SequentialAgent(
    name="poker_workflow_agent",
    sub_agents=[hand_rank_evaluator_agent, preflop_strategy_agent, postflop_strategy_agent, return_agent],
)
