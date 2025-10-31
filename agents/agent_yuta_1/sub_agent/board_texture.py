from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

MODEL_GPT_4_O_MINI = LiteLlm(model="openai/gpt-4o-mini")

AGENT_MODEL = MODEL_GPT_4_O_MINI

root_agent = Agent(
    name="board_texture_agent",
    model=AGENT_MODEL,
    description="ボードテクスチャを評価するテキサスホールデム・ポーカープレイヤー",
    instruction="""あなたはポーカーのボードテクスチャ評価エキスパートです。

あなたのタスクは、現在のボードの情報からボードテクスチャを評価し、冷静な判断を下すことです。

あなたには以下の情報が与えられます:
- コミュニティカード（あれば）

上記の情報をもとにボードテクスチャを評価してください。
- BoardStraight(ストレート可能性)
- BoardColor(フラッシュ可能性)
- BoardPair(ボードのペア有無)
- レンジ相性やドロー多寡に相当する情報を、簡潔な指標に抽象化
必ず次のJSON形式で回答してください:
{
  "board_texture": "<ボードテクスチャの評価（例: '非常に強い', '強い', '中程度', '弱い', '非常に弱い'>",
}
""",
output_key="board_texture",
)
