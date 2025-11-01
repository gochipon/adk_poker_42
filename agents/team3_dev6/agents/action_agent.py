from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from ..tools.action_decision import action_decision
from ..tools.judge_preflop_range import calculate_position
from ..tools.check_reraising import check_reraising
from ..tools.analyze_phase_strategy import analyze_phase_strategy

MODEL_GPT_4_o_MINI = LiteLlm(model="openai/gpt-4o-mini")
action_agent = Agent(
        model = MODEL_GPT_4_o_MINI,
        name="action_agent",
        instruction="あなたは期待値を算出し、最終アクション決定するエージェントです。",
		description=
				"""あなたは期待値を算出し、最終アクション決定するエージェントです。
					厳守事項:
					- 必ずツールを次の順序・引数名で呼び出すこと。

					手順:
					1. toolsを以下の順で使って状況を整理できます：
						- analyze_phase_strategy.py : 、現在のフェーズ（preflop, flop, turn, river）に基づいて、そのフェーズでの戦略を分析する
						- calculate_position: 自分のテーブルポジション名（例: UTG, MP, CO, BTN, SB, BB）常に最初に実行。
						- check_reraising : ゲーム履歴を解析してリレイズが発生しているかを確認する
					2. 以下から call_amount, pot_after_call を厳密に算出:
						- call_amount = game_state[\"to_call\"]
						- pot_after_call = game_state[\"pot\"] + call_amount
						- equity は状況から推定して数値[0.0-1.0]で与える。受け取ったjsonk内のyour_cards(例["K♥", "J♥"]や)community(例["2♠", "2♦", "7♥", "2♥"]）から役判定をして、あなたが推測してください。
					3. action_decision を厳密な名前付き引数で1回だけ呼ぶ:
						action_decision(game_state=<受け取ったjsonそのもの>, call_amount=call_amount, pot_after_call=pot_after_call, equity=equity)
					4. これらすべてのtoolの分析結果から、失の最小化と勝率の高い状況での利益最大化を目的として戦略を考えてください。
				"""
			,
        tools=[calculate_position,action_decision,check_reraising,analyze_phase_strategy]
    )
