from typing import Any

def action_decision(expected_value:  float, game_state: dict) -> dict[str, Any]:
    """
    期待値を算出し、その結果からアクションを決定するエージェントロジック。

    Args:
        game_state (dict): ゲームの状態データ。
			"your_chips": 残りチップ(例: 970)
			"pot": 現在のポット額(例: 140)
			"to_call": コールに必要な追加額 (0の場合はチェック/ベットが可能)(例: 20)

    Returns:
        dict: 決定されたアクション、額、理由。
            "action": str ("fold", "call", "raise", "check")
            "amount": int (チップ額)
            "reasoning": str (決定理由: 決定理由には、必ず期待値(expected_value)を入れて下さい)
    """

    your_chips = game_state["your_chips"]
    to_call = game_state["to_call"]
    pot = game_state["pot"]
    evRate = expected_value / your_chips * 100

    # 期待値に応じてaction決定
    if evRate > 10:
        if to_call == 0:
            # ベット（チップの1/2）
            action = "bet"
            amount = pot // 2
            reasoning = f"期待値が高い（{expected_value}(自分のスタックに対して{evRate:.2f}%）ため、ベットします。ベット額: {amount}"
        else:
            # レイズ（3倍）
            action = "raise"
            amount = to_call * 3
            reasoning = f"期待値が高い（{expected_value}(自分のスタックに対して{evRate:.2f}%）ため、3倍レイズします。レイズ額: {amount}"
    elif evRate > 5:
        if to_call == 0:
            # ベット（チップの1/3）
            action = "bet"
            amount = pot // 3
            reasoning = f"期待値が中程度（{expected_value}(自分のスタックに対して{evRate:.2f}%）ため、ベットします。ベット額: {amount}"
        else:
            # コール
            action = "call"
            amount = to_call
            reasoning = f"期待値が中程度（{expected_value}(自分のスタックに対して{evRate:.2f}%）ため、コールします。コール額: {amount}"
    elif evRate > 2:
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
        # フォールド
        action = "fold"
        amount = 0
        reasoning = f"期待値が{expected_value}(自分のスタックに対して{evRate:.2f}%で、マイナスなのでフォールド"

    return {
        "action": action,
        "amount": amount,
        "reasoning": reasoning
    }
