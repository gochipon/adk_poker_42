def calc_expected_value(game_state: dict) -> float:
    """
		現在のゲーム状態に基づいて、勝つ確率・ 勝ったときにもらえる額・負けたときに失う額を算出するエージェントロジック

   		 Args:
			game_state (dict): ゲームの状態データ。
				"your_cards": あなた2枚の手札 (例: ["A♥", "K♠"]),
				"community": 場に出ているカード(例:["Q♥", "J♦", "10♣"]),
				"your_chips": 残りチップ(例: 970)
				"pot": 現在のポット額(例: 140)
				"to_call": コールに必要な追加額 (0の場合はチェック/ベットが可能)(例: 20)

		Returns:
			dict:
			{
				"call_amount": コールに必要な正確なチップ額（`to_call` と同じ）。
				"pot_after_call": あなたがコールした場合のポット総額。 Pot before Call + call_amount,
				"equity": 自分がショーダウンで勝つ確率（または勝ち＋引き分けの半分を含む確率）
			}
    """

    lossRate =  1 - equity
    expected_value = equity * pot_after_call - lossRate * call_amount

    return expected_value
