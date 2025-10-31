from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from ..tools.action_decision import action_decision

MODEL_GPT_4_o_MINI = LiteLlm(model="openai/gpt-4o-mini")
action_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model = MODEL_GPT_4_o_MINI,
        # model=LiteLlm(model=MODEL_GPT_4O), # If you would like to experiment with other models
        name="action_agent",
        instruction=(
				"あなたは期待値を算出し、最終アクションをjsonで返すエージェントです。\n"
				"厳守事項:\n"
				"- 出力は単一のJSONのみ。前後の説明文・コードフェンスは禁止。\n"
				"- 最終的に返すキーは厳密に {\"action\",\"amount\",\"reasoning\"}。\n"
				"- 必ずツールを次の順序・引数名で呼び出すこと。\n"
				"手順:\n"
				"1) 以下から call_amount, pot_after_call を厳密に算出:\n"
				"   - call_amount = game_state[\"to_call\"]\n"
				"   - pot_after_call = game_state[\"pot\"] + call_amount\n"
				"   - equity は状況から推定して数値[0.0-1.0]で与える（あなたが推定する）。\n"
				"2) action_decision を厳密な名前付き引数で1回だけ呼ぶ:\n"
				"   action_decision(game_state=<受け取ったjsonそのもの>, call_amount=call_amount, pot_after_call=pot_after_call, equity=equity)\n"
				"3) action_decision の返り値(JSON)のみをそのまま出力（説明一切禁止）。\n"
			),
		description=(
			"期待値を算出し、算出した期待値とゲーム状態を用いて action_decision を呼び、"
			"その返り値(JSON)をそのまま返す。"
			),
        tools=[action_decision]
    )
