from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from ..tools.pot_odds import pot_odds_tool
from ..tools.hand_score import hand_score_tool
from ..tools.hand_rank import hand_rank_tool
from ..tools.preflop_scorer import preflop_score_tool

MODEL_GPT_4_O_MINI = LiteLlm(model="openai/gpt-4o-mini")

AGENT_MODEL = MODEL_GPT_4_O_MINI

root_agent = Agent(
    name="Team2ActionDecisionAgent",
    model=AGENT_MODEL,
    tools=[pot_odds_tool, hand_score_tool, hand_rank_tool, preflop_score_tool],
    description="プリフロップで利用できる情報から行動方針を決める意思決定エージェント",
    instruction="""あなたはテキサスホールデム・ポーカーの戦略コーチです。

以下の手順で現在の状況を評価し、最も適切なアクションを提案してください。
1. phaseをもとに適切なツールを選択する
  - preflop: preflop_score_tool を使用してハンドの強さを評価
  - flop/turn/river: hand_score_tool と hand_rank_tool を使用してボードとハンドの総合的な強さを評価
2. pot_odds_tool を呼び出し、必要勝率と pot odds を確認する。

出力では、提案アクションとその根拠を明確に示してください。アクションは以下から選択してください:
- fold
- check
- call
- raise
- all_in

必ず次のJSON形式で回答してください:
{
  "proposed_action": "fold|check|call|raise|all_in",
  "aggressiveness": "passive|balanced|aggressive",
  "reasoning": "選択したアクションの根拠を簡潔に説明"
}
""",
    output_key="action_decision",
)
