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

    your_chips = game_state["your_chips"]
    to_call = game_state["to_call"]
    pot = game_state["pot"]
    evRate = expected_value / your_chips * 100

    # 期待値に応じてaction決定
    if evRate > 10:
        if to_call == 0:
            # ベット（チップの1/1.5）
            action = "bet"
            amount = pot // 1.5
            reasoning = f"期待値が高い（{expected_value}(自分のスタックに対して{evRate:.2f}%）ため、ベットします。ベット額: {amount}"
        else:
            # レイズ（3倍）
            action = "raise"
            amount = to_call * 3
            reasoning = f"期待値が高い（{expected_value}(自分のスタックに対して{evRate:.2f}%）ため、3倍レイズします。レイズ額: {amount}"
    elif evRate > 5:
        if to_call == 0:
            # ベット（チップの1/2）
            action = "bet"
            amount = pot // 2
            reasoning = f"期待値が中程度（{expected_value}(自分のスタックに対して{evRate:.2f}%）ため、ベットします。ベット額: {amount}"
        else:
            # コール
            action = "call"
            amount = to_call
            reasoning = f"期待値が中程度（{expected_value}(自分のスタックに対して{evRate:.2f}%）ため、コールします。コール額: {amount}"
    elif evRate >= 2:
        if to_call == 0:
            # ベット（チップの1/3）
            action = "bet"
            amount = pot // 3
            reasoning = f"期待値がそこそこ（{expected_value}(自分のスタックに対して{evRate:.2f}%）のため、ベットします。ベット額: {amount}"
        else:
            # コール
            action = "call"
            amount = to_call
            reasoning = f"期待値がそこそこ（{expected_value}(自分のスタックに対して{evRate:.2f}%）のため、コールします。コール額: {amount}"
    elif evRate > 1:
        if to_call == 0:
            # チェック
            action = "check"
            amount = 0
            reasoning = f"期待値が低い（{expected_value}(自分のスタックに対して{evRate:.2f}%）ため、チェックします"
        else:
            # コール
            action = "call"
            amount = to_call
            reasoning = f"期待値が低い（{expected_value}(自分のスタックに対して{evRate:.2f}%）ため、コールします。コール額: {amount}"
    else:
        if to_call == 0:
            # チェック
            action = "check"
            amount = 0
            reasoning = f"期待値が{expected_value}(自分のスタックに対して{evRate:.2f}%で、マイナスなのでチェック"
        else:
            # フォールド
            action = "fold"
            amount = 0
            reasoning = f"期待値が{expected_value}(自分のスタックに対して{evRate:.2f}%で、マイナスなのでフォールド"

    return {
        "action": action,
        "amount": amount,
        "reasoning": reasoning
    }
