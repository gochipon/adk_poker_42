from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from ..tools.pot_odds import pot_odds_tool
from ..tools.hand_score import hand_score_tool
from ..tools.hand_rank import hand_rank_tool

MODEL_GPT_4_O_MINI = LiteLlm(model="openai/gpt-4o-mini")

AGENT_MODEL = MODEL_GPT_4_O_MINI

root_agent = Agent(
    name="PokerActionOrchestrator",
    model=AGENT_MODEL,
    tools=[pot_odds_tool, hand_score_tool, hand_rank_tool],
    description="This is an agent that sequentially executes agents (hand_score_agent, strategy_agent, format_agent) and tools (pot_odds_tool) to make strategic decisions in Texas Hold'em poker.",
    instruction="""
あなたはテキサスホールデム・ポーカーのエキスパートプレイヤーです。

まず以下のツールを使用して情報を収集してください：
1. pot_odds_tool: 必要勝率
2. hand_score_tool: 現在のハンドの強さを評価
3. hand_rank_tool: ハンドのランクを評価

これらの結果を総合的に判断して、最終的なアクションを決定してください。
hand_score_toolの戻り値を確認し、自分のハンドが絡んでいるか絡んでいないかも考慮して下さい。

必ず次のJSON形式で回答してください:
{
  "action": "fold|check|call|raise|all_in",
  "amount": <数値>,
  "reasoning": "あなたの決定の理由を簡潔に説明"
}
ルール:
- "fold"と"check"の場合: amountは0にしてください
- "call"の場合: コールに必要な正確な金額を指定してください
- "raise"の場合: call金額の3倍以上と基本とし,レイズ後の合計金額を指定してください
- "all_in"の場合: あなたの残りチップ全額を指定してください
  """,
  output_key="pre_flop_agent_output",
)
