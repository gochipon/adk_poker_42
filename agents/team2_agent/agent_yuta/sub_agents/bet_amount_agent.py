from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from ..tools.pot_odds import pot_odds_tool

MODEL_GPT_4_O_MINI = LiteLlm(model="openai/gpt-4o-mini")

AGENT_MODEL = MODEL_GPT_4_O_MINI

root_agent = Agent(
    name="Team2BetAmountAgent",
    model=AGENT_MODEL,
    tools=[pot_odds_tool],
    description="最終アクションに沿った適切なベットサイズを提案するエージェント",
    instruction="""あなたはベットサイズ設計のスペシャリストです。以下の検証済みアクションを基に、適切なベット額を提案してください。

参照情報:
- 検証済みアクションの詳細: {validated_action}
- ボードテクスチャー診断: {board_texture}
- 現在のポットサイズ、相手のベット金額、スタックサイズなど提供情報
- pot_odds_tool を利用して、必要勝率やリスク・リワードを定量的に確認する

ガイドライン:
- fold / check の場合: ベット額は 0 とする
- call の場合: コールに必要な金額をそのまま提示する
- raise の場合: 相手のベット+コール額を基準に、2.5倍〜4倍程度を目安に調整
- all_in の場合: 残りスタック全額を指定

必ず次のJSON形式で回答してください:
{
  "bet_amount": 数値,
  "sizing_reason": "ベット額の根拠を簡潔に説明"
}
""",
    output_key="bet_recommendation",
)
