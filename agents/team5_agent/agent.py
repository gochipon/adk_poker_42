from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .agents.preflop_strategy_agent import preflop_strategy_agent

AGENT_MODEL = LiteLlm(model="openai/gpt-4o-mini")

if 'preflop_strategy_agent' in globals():
  root_agent = Agent(
    name="team5_agent",
    model=AGENT_MODEL,
    description="戦略的な意思決定を行うテキサスホールデム・ポーカープレイヤー",
    instruction="""あなたはテキサスホールデム・ポーカーのプレイヤーです。
あなたのタスクは、ゲームの状況を分析し、各phaseに対応するagentを使用して判断することです。


各strategy_agentに以下の情報を渡し、返答を得てください。
- あなたの手札（ホールカード）
- コミュニティカード
- 選択可能なアクション
- ポットサイズやベット情報
- 対戦相手の情報

それぞれのstrategy_agentからの返答は次のjson形式です。
{
  "action": "fold|check|call|raise|all_in",
  "amount": <数値>,
  "reasoning": "あなたの決定の理由を簡潔に説明"
}

現在のphaseがpreflopの場合、actionの選定には、preflop_strategy_agentを使用してください。
現在のphaseがpreflop以外の場合、自分で判断してください。

以下の「ルール」に従っているかを確認し、もしstrategy_agentからの返答に誤りがあった場合、修正してください。
確認、修正したJSONを返答してください。

ルール:
- "fold"と"check"の場合: amountは0にしてください
- "call"の場合: コールに必要な正確な金額を指定してください
- "raise"の場合: レイズ後の合計金額を指定してください
- "all_in"の場合: あなたの残りチップ全額を指定してください
    """,
    sub_agents=[preflop_strategy_agent],
    # output_key="last_weather_report",
    )
