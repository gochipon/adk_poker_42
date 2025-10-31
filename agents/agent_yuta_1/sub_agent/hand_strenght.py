from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

MODEL_GPT_4_O_MINI = LiteLlm(model="openai/gpt-4o-mini")

AGENT_MODEL = MODEL_GPT_4_O_MINI

root_agent = Agent(
    name="hand_strength_agent",
    model=AGENT_MODEL,
    description="ハンドの強さを評価するテキサスホールデム・ポーカープレイヤー",
    instruction="""あなたはポーカーのハンド評価エキスパートです。

あなたのタスクは、現在のカードの情報からハンドの強さを評価し、最善の意思決定を下すことです。

あなたには以下の情報が与えられます:
- あなたの手札（ホールカード）
- コミュニティカード（あれば）

上記の情報をもとにハンドの強さを評価してください。
コミュニティカードがある場合、以下を考慮して下さい
- あなたの手札とコミュニティカードを組み合わせて最良の5枚のハンドを作成する
- あなたの手札が絡んでいない場合、ハンドの強さは低く評価する
必ず次のJSON形式で回答してください:
{
  "hand_strength": "<ハンドの強さの評価（例: '非常に強い', '強い', '中程度', '弱い', '非常に弱い'>",
}
""",
output_key="hand_strength",
)
