from typing import Any

def action_decision(expected_value:  float, game_state: dict) -> dict[str, Any]:
    """
    期待値を算出し、その結果からアクションを決定するエージェントロジック。

    Args:
        game_state (dict): ゲームの状態データ。
			"your_cards": あなた2枚の手札 (例: ["A♥", "K♠"]),
			"community": 場に出ているカード(例:["Q♥", "J♦", "10♣"]),
			"your_chips": 残りチップ(例: 970)
			"pot": 現在のポット額(例: 140)
			"to_call": コールに必要な追加額 (0の場合はチェック/ベットが可能)(例: 20)
            "actions": 許容されるアクションリスト (例: ["fold", "call", "raise"])

    Returns:
        dict: 決定されたアクション、額、理由。
            "action": str ("fold", "call", "raise", "check")
            "amount": int (チップ額)
            "reasoning": str (決定理由: 決定理由には、必ず期待値(expected_value)を入れて下さい)
    """
    # 入力情報からデータ取得
    # hand = game_state["your_cards"]
    # pot = game_state["pot"]
    to_call = game_state["to_call"]
    # your_chips = game_state["your_chips"]
    # actions = game_state["actions"]

    # 期待値に応じてaction決定
    if expected_value < 0:
        action = "fold"
        amount = 0
        reasoning = f"期待値が{expected_value}で、マイナスなのでフォールド"
    elif ...:
        action = "call"
        amount = to_call
        reasoning = f"期待値が{expected_value}で、プラスなのでコール"

    # ... 以降全部の分岐
    return {
        "action": action,
        "amount": amount,
        "reasoning": reasoning
    }
