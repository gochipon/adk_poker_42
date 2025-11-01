# tools/pot_odds_tool.py
def calc_pot_odds(pot_size, call_amount):
    """
    pot_size: 現在のポット（既に積まれている合計）
    call_amount: あなたがコールするのに必要な額
    return: pot_odds（割合） = call_amount / (pot_size + call_amount)
    """
    if pot_size + call_amount <= 0:
        return 0.0
    return round(call_amount / (pot_size + call_amount), 4)
