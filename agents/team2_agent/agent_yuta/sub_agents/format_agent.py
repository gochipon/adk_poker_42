from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

MODEL_GPT_4_O_MINI = LiteLlm(model="openai/gpt-4o-mini")

AGENT_MODEL = MODEL_GPT_4_O_MINI

root_agent = Agent(
    name="Team2FormatAgent",
    model=AGENT_MODEL,
    description="前段の意思決定結果を受け取り、ゲームエンジン向けの最終JSONを生成するフォーマッタ",
    instruction="""あなたはテキサスホールデム・ポーカーのエキスパートです。

意思決定の途中結果:
- ハンド評価による承認: {validated_action}
- ベット額の提案: {bet_recommendation}

これらの情報を整理し、整合性の取れた最終判断をまとめてください。

必ず次のJSON形式で回答してください:
{
  "action": "fold|check|call|raise|all_in",
  "amount": <数値>,
  "reasoning": "最終判断の理由を簡潔に説明"
}

注意:
- "fold" と "check" の場合は amount を 0 に設定すること
- "call" の場合はコールに必要な正確な金額を指定すること
- "raise" の場合はレイズ後の合計金額を指定すること
- "all_in" の場合は残りスタック全額を指定すること
- validated_action に記載された final_action を尊重し、必要に応じて bet_recommendation を参照すること
""",
output_key="agent_yuta_final_decision",
)
