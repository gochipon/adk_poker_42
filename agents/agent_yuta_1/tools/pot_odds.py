async def pot_odds_tool(pot: int, to_call: int) -> int:
    """
    ポットオッズを計算します。

    Args:
        pot: 現在のポット額
        to_call: コールするために必要な額

    Returns:
        ポットオッズの値（コール額 / (コール額 + ポット額)）
        -1を返す場合は、コール額が0であることを示します。
    """
    if to_call == 0:
        result = int('-1')
    else:
        result = to_call / (to_call + pot)

    return result