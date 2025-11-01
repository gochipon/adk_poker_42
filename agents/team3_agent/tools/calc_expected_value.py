def calc_expected_value(call_amount: float, pot_after_call: float, equity: float) -> float:
    """
		現在のゲーム状態に基づいて、期待値(EV)を算出する。

   		 Args:
			call_amount (float): コールに必要な正確なチップ額。
			pot_after_call (float): 自分がコール（あるいは同額投入）した後のポット総額。
			equity (float): ショーダウンで勝つ確率（引き分けの0.5加味など、適用する定義に従う）。


		Returns:
			float: 期待値（EV）。
               EV = equity * pot_after_call - (1 - equity) * call_amount
    """

    lossRate =  1 - equity
    expected_value = equity * pot_after_call - lossRate * call_amount

    return expected_value
