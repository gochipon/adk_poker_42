from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

MODEL_GPT_4_O_MINI = LiteLlm(model="openai/gpt-4o-mini")

AGENT_MODEL = MODEL_GPT_4_O_MINI

root_agent = Agent(
    name="beginner_poker_agent",
    model=AGENT_MODEL,
    description="戦略的な意思決定を行うテキサスホールデム・ポーカープレイヤー",
    instruction="""あなたはテキサスホールデム・ポーカーのエキスパートプレイヤーです。

選択したアクション{action}
F（フォールド）| C（チェック/コール）| RS（小レイズ）| RM（中レイズ）| RB（大レイズ）

あなたのタスクは、決定されたアクションから最適なベットサイズを決定することです。
- RS（小レイズ）の場合: ポットの約15%をベットサイズとして提案してください
- RM（中レイズ）の場合: ポットの約50%をベットサイズとして提案してください
- RB（大レイズ）の場合: ポットの約100~200%をベットサイズとして提案してください
以下のJSON形式で回答してください:
{
  "bet_size": 数値
}

""",
output_key="bet_size",
)
