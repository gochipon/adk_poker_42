# …（省略：インポート・build_input_for_llmなど既存部分）…

def decide_action(game_state):
    data = build_input_for_llm(game_state)

    if data["stage"] == "preflop":
        pf = data["preflop_strength"]
        pos = data["position"]
        stack = data["stack"]
        call_amt = data["call_amount"] or 10
        pot = data["pot_size"] or (game_state.get("blinds",0) * game_state.get("num_active_players",5))
        # 補正ファクター
        pos_factor = {"UTG":0.8, "MP":0.9, "CO":1.0, "BTN":1.1, "SB":0.95}.get(pos, 1.0)
        stack_factor = min(stack / (call_amt * 20), 2.0)  # スタックが深いとレイズ余地あり
        adj_strength = pf * pos_factor * stack_factor

        reasoning = (f"プリフロップ強度 {pf:.2f} × ポジション補正 {pos_factor:.2f} × "
                     f"スタック補正 {stack_factor:.2f} = 補正値 {adj_strength:.2f}")

        # 閾値設定
        if adj_strength >= 1.0:
            return {"action":"raise", "amount":3 * call_amt,
                    "reasoning": reasoning + " → 補正値高く、3倍レイズします。"}
        elif adj_strength >= 0.7:
            return {"action":"call", "amount":call_amt,
                    "reasoning": reasoning + " → 補正値中程度なのでコールします。"}
        else:
            return {"action":"fold", "amount":0,
                    "reasoning": reasoning + " → 補正値低いためフォールドします。"}

    # …（ポストフロップ部分は変わらず）…

}