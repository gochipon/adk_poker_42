from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .tools.judge_preflop_range import judge_preflop_range, calculate_position
from .tools.hand_evaluation import hand_evaluation
# from .agents.action_agent import action_agent

MODEL_GPT_4_o_MINI = LiteLlm(model="openai/gpt-4o-mini")

root_agent = Agent(
    name="beginner_poker_agent",
    model=MODEL_GPT_4_o_MINI,
    tools=[calculate_position, judge_preflop_range, hand_evaluation],
    description="This is an agent that sequentially executes and utilizes multiple agents and tools to make strategic decisions in Texas Hold'em poker.",
    instruction="""
					あなたはテキサスホールデム・ポーカーのエキスパートプレイヤーです。
					5人のプレイヤーで30ハンドする際に、最終チップ額を最大化することを目的として戦略を考えてください。

					まず、以下のツールをこの順で使って状況を整理してください：
					1. calculate_position: 自分のテーブルポジション名（例: UTG, MP, CO, BTN, SB, BB）常に最初に実行。
					2. judge_preflop_range : 推奨アクションとその根拠範囲
					3. hand_evaluation: フロップ以降で、自分の現在の相対的なハンド強度を厳密比較で把握。プリフロップ(ボード0枚)は相対比較ができないため、レンジ判断を優先。

					これらの結果を総合的に判断して、最終的なアクションを決定してください。
					hand_evaluationの戻り値を確認し、自分のハンドが絡んでいるか絡んでいないかも考慮して下さい。

					必ず次のJSON形式で回答してください:
					{
					"action": "fold|check|call|raise|all_in",
					"amount": <数値>,
					"reasoning": "あなたの決定の理由を簡潔に説明"
					}

					ルール:
					- "fold"と"check"の場合: amountは0にしてください
					- "call"の場合: コールに必要な正確な金額を指定してください
					- "raise"の場合: レイズ後の合計金額を指定してください
					- "all_in"の場合: あなたの残りチップ全額を指定してください
					- "call"や"raise"で指定/必要金額があなたの残りチップを超える場合: 自動的に"all_in"とし、amountは残りチップ全額にしてください
				""",
)
