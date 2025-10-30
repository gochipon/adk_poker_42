from typing import Any

def action_decision(expected_value:  float, game_state: dict) -> dict[str, Any]:
    """
    期待値を算出し、その結果からアクションを決定するエージェントロジック。

    Args:
        game_state (dict): ゲームの状態データ。
            "your_cards": 2枚の手札 (例: ["As", "Kd"])
            "pot": 現在のポット額
            "to_call": コールに必要な追加額 (0の場合はチェック/ベットが可能)
            "your_chips": 残りチップ
            "actions": 許容されるアクションリスト (例: ["fold", "call", "raise"])

    Returns:
        dict: 決定されたアクション、額、理由。
            "action": str ("fold", "call", "raise", "check")
            "amount": int (チップ額)
            "reasoning": str (決定理由)
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
        reasoning = "期待値が負なのでフォールド"
    elif ...:
        action = "call"
        amount = to_call
        reasoning = "..."  # ロジックの理由
    # ... 以降全部の分岐
    return {
        "action": action,
        "amount": amount,
        "reasoning": reasoning
    }
