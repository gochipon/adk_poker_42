def calc_expected_value(game_state: dict) -> float:
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
        float: expected_valueにハンドの強さのスコア (0.0 - 1.0)を格納する
    """

    # 入力情報からデータ取得
    # hand = game_state["your_cards"]
    # pot = game_state["pot"]
    # to_call = game_state["to_call"]
    # your_chips = game_state["your_chips"]
    # actions = game_state["actions"]
    # ... ここで簡易的な期待値算出
    # expected_value =
    # 期待値に応じてaction決定

    return expected_value
