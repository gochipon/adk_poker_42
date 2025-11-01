from google.adk.agents import Agent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from .tools.judge_preflop_range import calculate_position
from .tools.hand_evaluation import hand_evaluation
from .tools.analyze_opponents import analyze_opponents

MODEL_GPT_4_o_MINI = LiteLlm(model="openai/gpt-4o-mini")

strategy_agent = Agent(
    name="poker_strategy_analyzer",
    model=MODEL_GPT_4_o_MINI,
    tools=[calculate_position, hand_evaluation, analyze_opponents],
    description="This is an agent that sequentially executes and utilizes multiple agents and tools to make strategic decisions in Texas Hold'em poker.",
    instruction="""
					あなたはテキサスホールデム・ポーカーのエキスパートプレイヤーです。
					5人のプレイヤーでプレイする際に、長期的に見た時の最終チップ額を最大化することを目的として戦略を考えてください。

					あなたには以下の情報が与えられます:
					- あなたの手札（ホールカード）
					- コミュニティカード（あれば）
					- 選択可能なアクション
					- ポットサイズやベット情報
					- 対戦相手の情報

					さらに、toolsを以下の順で使って状況を整理できます：
					1. calculate_position : 自分のポジション計算
					2. hand_evaluation: フロップ以降で、自分の現在の相対的なハンド強度を厳密比較で把握。プリフロップ(ボード0枚)は相対比較ができないため、レンジ判断を優先。
					3. analyze_opponents : JSON形式のゲーム状態から履歴を取得し、相手プレイヤーのプレイスタイル（タイト/ルーズ、アグレッシブ/パッシブ）、ベッティングパターン、統計指標（VPIP, PFR, AFQ）などを分析します。

					これらの情報・結果から、以下の点を考慮しつつ戦略分析を行なってください:
						- 自分の手札の強さ
						- 手札の役とボードとの絡み
						- ポットオッズと損益分岐点
						- コールに必要な金額に対するポットの比率
						- ドローが完成した場合の期待値（EV）
						- ポジションの有利・不利

					分析結果から、推奨するアクション（fold/check/call/raise/all_in）と具体的な金額、そしてその戦略的理由を詳しく説明してください。
				""",
	output_key="strategy_analysis",
)

json_formatter_agent = Agent(
    name="poker_json_formatter",
    model=MODEL_GPT_4_o_MINI,
    description="ポーカーの戦略分析をJSON形式に整形するエキスパート",
    instruction="""あなたは戦略分析結果を指定されたJSON形式に正確に変換する専門家です。

					戦略分析結果: {strategy_analysis}

					上記の戦略分析を基に、必ず次のJSON形式で正確に回答してください:
					{
					"action": "fold|check|call|raise|all_in",
					"amount": <数値>,
					"reasoning": "戦略分析から導出された決定と戦略的理由の詳細な説明"
					}

					ルール:
					- "fold"と"check"の場合: amountは0にしてください
					- "call"の場合: コールに必要な正確な金額を指定してください
					- "raise"の場合: レイズ後の合計金額を指定してください
					- "all_in"の場合: あなたの残りチップ全額を指定してください
					- "call"や"raise"で指定/必要金額があなたの残りチップを超える場合: 自動的に"all_in"とし、amountは残りチップ全額にしてください
					- reasoningには戦略分析の内容を要約して含めてください
					- 必ずJSONの正確な構文で回答してください

					戦略分析の内容を適切に解釈し、JSON形式で出力してください。
				""",
)

root_agent = SequentialAgent(
    name="poker_workflow_agent",
    sub_agents=[strategy_agent, json_formatter_agent],
)
