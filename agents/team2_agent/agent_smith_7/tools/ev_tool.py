# tools/ev_tool.py
def expected_value(win_rate, pot_size, call_amount):
    """
    EV = win_rate * (pot_size + call_amount) - call_amount
    これは「コールした場合の期待的な純利益」を表します。
    """
    ev = win_rate * (pot_size + call_amount) - call_amount
    return round(ev, 2)
