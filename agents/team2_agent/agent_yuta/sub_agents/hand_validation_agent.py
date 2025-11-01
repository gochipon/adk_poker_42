from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

MODEL_GPT_4_O_MINI = LiteLlm(model="openai/gpt-4o-mini")

AGENT_MODEL = MODEL_GPT_4_O_MINI

root_agent = Agent(
    name="Team2HandValidationAgent",
    model=AGENT_MODEL,
    description="ハンドとボードの絡みを検証し、アクションの妥当性を判断するゲートキーパーエージェント",
    instruction="""あなたはハンド評価の専門家です。以下の情報を基に、提案されたアクションがハンド状況に適しているかを確認してください。

提案アクションの詳細: {action_decision}
ボードテクスチャー診断: {board_texture}


手順:
1. 提案されたアクションを検証する。
2. テーブル状況（ポジション、スタック、ベット履歴）を考慮しながら、全体のリスクとリターンを評価する。



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
