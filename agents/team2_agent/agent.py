from google.adk.agents.llm_agent import Agent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.models.lite_llm import LiteLlm

from .agent_smith_7 import root_agent as agent_smith_7
from .agent_yuta import root_agent as agent_yuta

MODEL_GPT_4_O_MINI = LiteLlm(model="openai/gpt-4o-mini")

parallel_agent = ParallelAgent(
    name="team2_parallel_agent",
    description="Team2の各エージェントに同じポーカー状況を同時並列で評価させます。",
    sub_agents=[
        agent_yuta,
        agent_smith_7,
    ],
)

consensus_agent = Agent(
    name="team2_consensus_agent",
    model=MODEL_GPT_4_O_MINI,
    description="並列エージェントの出力を比較し、最終的な行動を選択する審判エージェント。",
    instruction="""
    
{agent_yuta_final_decision}
{agent_smith_7_final_decision}
上記はそれぞれTeam2の異なるエージェントが出した提案です。
各エージェントの提案(JSON形式)を読み、行動(action)・金額(amount)・理由(reasoning)を評価してください。

- 各提案の根拠に一貫性があるか、ポーカー戦略として妥当かを確認する
- 金額の整合性やポーカーのルールに違反しないかをチェックする
- 複数の提案から最も合理的なものを選択するか、必要に応じて独自の改善案を提示する
- 最終的な判断に至った理由を簡潔にまとめる
- ドローの可能性は考えないでください

必ず次のJSON形式で回答してください:
{
  "action": "fold|check|call|raise|all_in",
  "amount": <数値>,
  "reasoning": "各エージェントの提案を比較した上で選択した理由を説明"
}

注意:
- amountは数値のみで出力する（単位や文字列を含めない）
- fold / check の場合は amount を 0 にする
- call の場合はコールに必要な正確な金額を指定する
- raise の場合はレイズ後の合計金額を指定する
- all_in の場合は残りスタック全額を指定する
""",
)

root_agent = SequentialAgent(
    name="team2_sequential_controller",
    description="Team2の最終意思決定フロー。まず並列評価を実行し、その結果を基に最終アクションを決定する。",
    sub_agents=[
        parallel_agent,
        consensus_agent,
    ],
)
