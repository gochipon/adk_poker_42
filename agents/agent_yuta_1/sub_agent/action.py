from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

MODEL_GPT_4_O_MINI = LiteLlm(model="openai/gpt-4o-mini")

AGENT_MODEL = MODEL_GPT_4_O_MINI

root_agent = Agent(
    name="beginner_poker_agent",
    model=AGENT_MODEL,
    description="戦略的な意思決定を行うテキサスホールデム・ポーカープレイヤー",
    instruction="""あなたはテキサスホールデム・ポーカーのエキスパートプレイヤーです。

ハンドの強さ評価: {hand_strength}
ボードテクスチャ評価: {board_texture}
相手のハンド予想: {forecast}

あなたのタスクは、ハンドの強さとボードテクスチャとハンド予想から、最善の意思決定を下すことです。
F（フォールド）| C（チェック/コール）| RS（小レイズ）| RM（中レイズ）| RB（大レイズ）
ハイカードやペアの場合、慎重にプレイすることを検討してください。

以下のtoolsを使用して、ポットオッズを計算し、意思決定に役立ててください。
- pot_odds_tool: ポットオッズを計算するツール

必ず次のJSON形式で回答してください:
{
  "action": "<あなたの意思決定（F、C、RS、RM、RBのいずれか）>"
}
""",
output_key="action",
)
