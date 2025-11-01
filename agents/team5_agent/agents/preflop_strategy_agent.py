from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from ..tools.should_raise_on_preflop  import should_raise_on_preflop

AGENT_MODEL = LiteLlm(model="openai/gpt-4o-mini")

preflop_strategy_agent = Agent(
        model = AGENT_MODEL,
        name="preflop_strategy_agent",
        description="戦略的な意思決定を行うテキサスホールデム・ポーカープレイヤー",
        instruction="""あなたはテキサスホールデム・ポーカーのエキスパートプレイヤーです。
あなたのタスクは、preflopにおいて、テーブルの状況を確認しactionを決定することです。

もし、**phaseがpreflopでなければ、このエージェントはアクションを決定せず、処理を終了します。これは制約です。必ず守ってください。**

phaseがpreflopの場合、以下の入力が与えられたときに、最適なアクション（fold / check / call / raise / all_in） と 具体的な金額 を決定してください。
あなたには以下の情報が与えられます:
- あなたの手札（ホールカード）
- 選択可能なアクション
- ポットサイズやベット情報
- 対戦相手の情報

ルール:
- "fold"と"check"の場合: amountは0にしてください
- "call"の場合: コールに必要な正確な金額を指定してください
- "raise"の場合: レイズ後の合計金額を指定してください
- "all_in"の場合: あなたの残りチップ全額を指定してください

## 判断プロセス（Decision Process）

以下の手順で判断します：

1. **自分のポジションを求める**
  position = (your_id - dealer_button) % number_of_players

2. **現在のphaseでraiseがされた回数確認する**
  historyの中で、現在のphaseにおけるraiseの回数を数える
3. 現在のポジションとraise回数に基づきshould_raise_on_preflopツールを使用する。
  戻り値を確認し、Trueの場合は"raise"を選択し、そうでなければ"fold"を選択する
  raiseするamountは、raise回数に応じて以下のように決定する:
- 0回目のraise: 60
- 1回目のraise: 251
- 2回目のraise: 750
- 3回目以降のraise: all_in

ツールの結果に従いアクション決定し、戦略内容を説明してください。

    """,
    tools=[should_raise_on_preflop],
    output_key="strategy_analysis_preflop",
    )
