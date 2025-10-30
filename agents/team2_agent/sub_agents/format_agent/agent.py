from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

MODEL_GPT_4_O_MINI = LiteLlm(model="openai/gpt-4o-mini")

AGENT_MODEL = MODEL_GPT_4_O_MINI

root_agent = Agent(
    name="FormatAgent",
    model=AGENT_MODEL,
    description="戦略的な意思決定を行うテキサスホールデム・ポーカープレイヤー",
    instruction="""あなたはテキサスホールデム・ポーカーのエキスパートプレイヤーです。

    {strategy_analysis}
入力を元に以下のJSON形式で回答して下さい:
{
  "action": "fold|check|call|raise|all_in",
  "amount": <数値>,
  "reasoning": "あなたの決定の理由を簡潔に説明"
}

ルール:
- "fold"と"check"の場合: amountは0にしてください
- "call"の場合: コールに必要な正確な金額を指定してください
- "raise"の場合: レイズ後の合計金額を指定してください
- "all_in"の場合: あなたの残りチップ全額を指定してください
- ハンドの評価はhand_evaluator_toolを使用してください
""",
    output_key="final_action",
)