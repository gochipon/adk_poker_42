from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from ..tools.hand_score import hand_score_tool
from ..tools.hand_rank import hand_rank_tool

MODEL_GPT_4_O_MINI = LiteLlm(model="openai/gpt-4o-mini")

AGENT_MODEL = MODEL_GPT_4_O_MINI

root_agent = Agent(
    name="Team2HandValidationAgent",
    model=AGENT_MODEL,
    tools=[hand_score_tool, hand_rank_tool],
    description="ハンドとボードの絡みを検証し、アクションの妥当性を判断するゲートキーパーエージェント",
    instruction="""あなたはハンド評価の専門家です。以下の情報を基に、提案されたアクションがハンド状況に適しているかを確認してください。

参照情報:
- 提案アクションの詳細: {action_decision}
- 現在利用できるカード情報（ホールカードとボードカード）
- hand_score_tool / hand_rank_toolで得られる定量的な評価

手順:
1. hand_score_tool と hand_rank_tool を活用し、ハンドがボードと絡んでいるか、また実戦的な強さがあるかを判断する。
2. 提案されたアクションがハンドの強さ・ドロー状況と整合しているか検証する。
3. 不適切な場合は、より安全かつ論理的な代替アクションを提案する。

必ず次のJSON形式で回答してください:
{
  "final_action": "fold|check|call|raise|all_in",
  "hand_involvement": "strong|medium|weak|none",
  "approval": true|false,
  "justification": "承認・却下の理由"
}

final_action は approval=false の場合でも、推奨したいアクションを記載してください。
""",
    output_key="validated_action",
)
