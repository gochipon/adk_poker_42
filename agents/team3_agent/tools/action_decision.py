from typing import Any

def action_decision(game_state: dict, call_amount: float, pot_after_call: float, equity: float) -> dict[str, Any]:
    """
    期待値を算出し、その結果からアクションを決定するエージェントロジック。

    Args:
        game_state (dict): json形式のゲームの状態データ。
							例)
							{
								"your_id": 0,
								"phase": "flop",
								"your_cards": ["K♥", "J♥"],
								"community": ["2♠", "2♦", "7♥"],
								"your_chips": 1980,
								"your_bet_this_round": 0,
								"your_total_bet_this_hand": 20,
								"pot": 50,
								"to_call": 0,
								"dealer_button": 3,
								"current_turn": 0,
								"players": [
									{"id": 1, "chips": 1980, "bet": 0, "status": "active"},
									{"id": 2, "chips": 2000, "bet": 0, "status": "folded"},
									{"id": 3, "chips": 2000, "bet": 0, "status": "folded"},
									{"id": 4, "chips": 1990, "bet": 0, "status": "folded"}
								],
								"actions": ["fold", "check", "raise (min 20)", "all-in (1980)"],
								"history": [
									"Player 4 posted small blind 10",
									"Player 0 posted big blind 20",
									"Player 1 called 20",
									"Player 2 folded",
									"Player 3 folded",
									"Player 4 folded",
									"Player 0 checked",
									"Flop dealt: 2♠, 2♦, 7♥"
								]
								}
		call_amount (float): コールに必要な正確なチップ額。
		pot_after_call (float): 自分がコール（あるいは同額投入）した後のポット総額。
		equity (float): ショーダウンで勝つ確率（引き分けの0.5加味など、適用する定義に従う）。


    Returns:
        dict: 決定されたアクション、額、理由を記述したJSON
		{
            "action": str ("fold", "call", "raise", "check")
            "amount": int (チップ額)
            "reasoning": str (決定理由: 決定理由には、必ず期待値(expected_value)を入れて下さい)
		}

	"""

    lossRate =  1 - equity
    expected_value = equity * pot_after_call - lossRate * call_amount

    # your_chips = game_state["your_chips"]
    to_call = game_state["to_call"]
    pot = game_state["pot"]
    phase = game_state.get("phase", "flop").lower()

    # ポットに対するEV比率（%）
    valueRate = (expected_value / pot * 100) if pot > 0 else 0.0

    # ポットオッズしきい値（equity）: コールに必要
    pot_odds_threshold = 0.0 if pot_after_call <= 0 else (to_call / pot_after_call)

    # 1) 相手ベットなし（to_call==0）→ ベット/チェックのみ
    if to_call == 0:
        # フロップ/ターンやや緩め、リバーは厳しめ
        value_thresh = 0.65 if phase in ("flop", "turn") else 0.70
        semi_thresh_low, semi_thresh_high = ((0.50, 0.65) if phase in ("flop", "turn") else (0.55, 0.68))

        if equity >= value_thresh:
            # バリュー: 2/3ポット
            bet_size = max(1, int(pot * 0.66))
            reasoning = f"期待値が高い（{expected_value:.2f}(ポットに対して{valueRate:.2f}%）ため、2/3ポットでベットします。ベット額: {bet_size}"
            return {"action": "raise", "amount": bet_size, "reasoning": reasoning}

        if semi_thresh_low <= equity < semi_thresh_high and phase in ("flop", "turn"):
            # セミブラフ: 1/2ポット
            bet_size = max(1, int(pot * 0.50))
            reasoning = f"期待値が見込める（{expected_value:.2f}(ポットに対して{valueRate:.2f}%）ため、1/2ポットでセミブラフします。ベット額: {bet_size}"
            return {"action": "raise", "amount": bet_size, "reasoning": reasoning}

        reasoning = f"期待値が低い（{expected_value:.2f}(ポットに対して{valueRate:.2f}%）ため、チェックします"
        return {"action": "check", "amount": 0, "reasoning": reasoning}

    # 2) 相手のベットがある（to_call>0）→ コール/レイズ/フォールド
    if equity >= pot_odds_threshold:
        # 強いときだけバリューレイズ（2.5x）
        strong_thresh = 0.62 if phase in ("flop", "turn") else 0.68
        if equity >= strong_thresh:
            raise_amount = max(1, int(to_call * 2.5))
            reasoning = f"期待値が高い（{expected_value:.2f}(ポットに対して{valueRate:.2f}%）ため、2.5倍でバリューレイズします。レイズ額: {raise_amount}"
            return {"action": "raise", "amount": raise_amount, "reasoning": reasoning}

        reasoning = f"ポットオッズを満たしており（{expected_value:.2f}(ポットに対して{valueRate:.2f}%）、コールが妥当と判断。コール額: {to_call}"
        return {"action": "call", "amount": to_call, "reasoning": reasoning}

    # しきい値未満 → フォールド
    reasoning = f"期待値が{expected_value:.2f}(ポットに対して{valueRate:.2f}%で、マイナスなのでフォールド"
    return {"action": "fold", "amount": 0, "reasoning": reasoning}


      # valueRate = expected_value / pot * 100

    # # 期待値に応じてaction決定
    # if valueRate > 90:
    #     if to_call == 0:
    #         # ベット（pot分）
    #         action = "raise"
    #         amount = pot
    #         reasoning = f"期待値が高い（{expected_value}(ポットに対して{valueRate:.2f}%）ため、ベットします。ベット額: {amount}"
    #     else:
    #         # レイズ（3倍）
    #         action = "raise"
    #         amount = to_call * 3
    #         reasoning = f"期待値が高い（{expected_value}(ポットに対して{valueRate:.2f}%）ため、3倍レイズします。レイズ額: {amount}"
    # elif valueRate > 70:
    #     if to_call == 0:
    #         # ベット（potの1/2）
    #         action = "raise"
    #         amount = pot // 2
    #         reasoning = f"期待値が中程度（{expected_value}(ポットに対して{valueRate:.2f}%）ため、ベットします。ベット額: {amount}"
    #     else:
    #         # コール
    #         action = "call"
    #         amount = to_call
    #         reasoning = f"期待値が中程度（{expected_value}(ポットに対して{valueRate:.2f}%）ため、コールします。コール額: {amount}"
    # elif valueRate > 50:
    #     if to_call == 0:
    #         # ベット（potの1/3）
    #         action = "raise"
    #         amount = pot // 3
    #         reasoning = f"期待値がそこそこ（{expected_value}(ポットに対して{valueRate:.2f}%）ため、ベットします。ベット額: {amount}"
    #     else:
    #         # コール
    #         action = "call"
    #         amount = to_call
    #         reasoning = f"期待値がそこそこ（{expected_value}(ポットに対して{valueRate:.2f}%）ため、コールします。コール額: {amount}"
    # elif valueRate > 30:
    #     if to_call == 0:
    #         # チェック
    #         action = "check"
    #         amount = 0
    #         reasoning = f"期待値が低い（{expected_value}(ポットに対して{valueRate:.2f}%）ため、チェックします"
    #     else:
    #         # コール
    #         action = "call"
    #         amount = to_call
    #         reasoning = f"期待値が低い（{expected_value}(ポットに対して{valueRate:.2f}%）ため、コールします。コール額: {amount}"
    # else:
    #     # フォールド
    #     action = "fold"
    #     amount = 0
    #     reasoning = f"期待値が{expected_value}(ポットに対して{valueRate:.2f}%で、マイナスなのでフォールド"


    # evRate = expected_value / your_chips * 100
    # # 期待値に応じてaction決定
    # if evRate > 10:
    #     if to_call == 0:
    #         # ベット（チップの1/2）
    #         action = "bet"
    #         amount = pot // 2
    #         reasoning = f"期待値が高い（{expected_value}(自分のスタックに対して{evRate:.2f}%）ため、ベットします。ベット額: {amount}"
    #     else:
    #         # レイズ（3倍）
    #         action = "raise"
    #         amount = to_call * 3
    #         reasoning = f"期待値が高い（{expected_value}(自分のスタックに対して{evRate:.2f}%）ため、3倍レイズします。レイズ額: {amount}"
    # elif evRate > 5:
    #     if to_call == 0:
    #         # ベット（チップの1/3）
    #         action = "bet"
    #         amount = pot // 3
    #         reasoning = f"期待値が中程度（{expected_value}(自分のスタックに対して{evRate:.2f}%）ため、ベットします。ベット額: {amount}"
    #     else:
    #         # コール
    #         action = "call"
    #         amount = to_call
    #         reasoning = f"期待値が中程度（{expected_value}(自分のスタックに対して{evRate:.2f}%）ため、コールします。コール額: {amount}"
    # elif evRate > 2:
    #     if to_call == 0:
    #         # チェック
    #         action = "check"
    #         amount = 0
    #         reasoning = f"期待値が低い（{expected_value}(自分のスタックに対して{evRate:.2f}%）ため、チェックします"
    #     else:
    #         # コール
    #         action = "call"
    #         amount = to_call
    #         reasoning = f"期待値が低い（{expected_value}(自分のスタックに対して{evRate:.2f}%）ため、コールします。コール額: {amount}"
    # else:
    #     # フォールド
    #     action = "fold"
    #     amount = 0
    #     reasoning = f"期待値が{expected_value}(自分のスタックに対して{evRate:.2f}%で、マイナスなのでフォールド"

    return {
        "action": action,
        "amount": amount,
        "reasoning": reasoning
    }
