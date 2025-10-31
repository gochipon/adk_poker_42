from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from ..tools.pot_odds import pot_odds_tool

MODEL_GPT_4_O_MINI = LiteLlm(model="openai/gpt-4o-mini")

AGENT_MODEL = MODEL_GPT_4_O_MINI

root_agent = Agent(
    name="forecast_agent",
    model=AGENT_MODEL,
    description="戦略的な意思決定を行うテキサスホールデム・ポーカープレイヤー",
    instruction="""あなたはテキサスホールデム・ポーカーのエキスパートプレイヤーです。

ボードテクスチャ評価: {board_texture}

あなたのタスクは、ボードテクスチャと、ハンド履歴を元に対戦相手のハンドを予想することです。

以下のtoolsを使用してアクションを確認することで意思決定に役立ててください。
- history_tool: 最近のハンド履歴を取得するツール

必ず次のJSON形式で回答してください:
{
  "forecast": "bluff|strong_hand|medium_hand|weak_hand",
}
""",
tools=[pot_odds_tool],
output_key="forecast",
)
