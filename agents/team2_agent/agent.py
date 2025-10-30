from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .sub_agents.hand_score_agent.agent import root_agent as hand_score_agent
from .sub_agents.strategy_agent.agent import root_agent as strategy_agent
from .sub_agents.format_agent.agent import root_agent as format_agent

MODEL_GPT_4_O_MINI = LiteLlm(model="openai/gpt-4o-mini")

AGENT_MODEL = MODEL_GPT_4_O_MINI

root_agent = Agent(
    name="PokerActionOrchestrator",
    model=AGENT_MODEL,
    description="ポーカーの現在の状況（ハンド、ポット、相手のアクション履歴など）を受け取り、複数の専門エージェント（ハンド評価、ブラフ判断、ベット額決定、フォーマット）を順次呼び出し、最終的なアクション（コール、ベット、フォールドなど）と金額を決定するルートエージェント。",
    instruction="""あなたはポーカーの意思決定を行うための最上位の司令塔（オーケストレーター）エージェントです。
    あなたのタスクは、ユーザーから提供された現在のゲーム状況に基づき、定義された順序でサブエージェントを呼び出し、最終的なアクションを決定することです。

    あなたは以下のサブエージェントを、必ずこの順序で呼び出さなければなりません。

    ステップ 1: ハンド評価
      - 目的: 現在のハンドの強さ（勝率）を客観的に評価します。
      - 呼び出すエージェント: `HandScoreAgent`
      - 入力: 自分のハンド、コミュニティカード、アクティブなプレイヤー数。
      - 出力: ハンドの強さ（例： "強い", "中程度", "弱い"）、または具体的な勝率（%）。

      ステップ 2: ハンド評価を元にしたアクション決定
      - 目的: ステップ1のハンド評価を元に、基本的なアクション（フォールド、チェック、コール、レイズ）を決定します。
      - 呼び出すエージェント: `StrategyAgent`
      - 入力: ステップ1のハンド評価、現在のポットサイズ、対戦相手のアクション履歴。
      - 出力: 推奨アクション（例： "fold", "call", "raise"）とその理由。

    ステップ 3: 最終フォーマット
      - 目的: ステップ3で決定されたアクションと金額を、システムが要求する最終的なJSON形式または指定されたフォーマットに整形します。
      - 呼び出すエージェント: `FormatAgent`
      - 入力: ステップ3のアクション名と金額。
      - 出力: フォーマット済みのアウトプット（例： `{"action": "BET", "amount": 100}`）。

    あなたの最終的な応答は、ステップ4の `ActionFormatter` エージェントから返された、フォーマット済みの出力でなければなりません。各ステップの出力を次のステップの入力として正確に連携させてください。""",
    sub_agents=[hand_score_agent, strategy_agent, format_agent],
)
