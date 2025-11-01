# tools/position_tool.py
def get_position_label(seat_index, total_players=5, dealer_index=0):
    """
    seat_index: あなたの座席インデックス（0..total_players-1）
    dealer_index: ディーラーボタンのインデックス
    returns: "UTG"|"MP"|"CO"|"BTN"|"SB" など（5人想定）
    """
    # 5人用の一般的ラベル（状況に応じて調整可）
    positions = ["UTG", "MP", "CO", "BTN", "SB"]
    # Normalize index relative to dealer
    rel = (seat_index - dealer_index) % total_players
    return positions[rel]