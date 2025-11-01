from google.adk.tools.tool_context import ToolContext
from ..agents.preflop_range import range_0_open, range_1_open, range_3_open, range_4_open,range_3bet, range_4bet, range_5bet

from typing import List, Dict, Any, Tuple

def should_raise_on_preflop(cards: List[str], position: int, raise_cnt: int, tool_context: ToolContext) -> bool:
    """
    ポーカーの役判定ツール。
    Args:
        cards (List[str]): 例 ['AS', 'KD', 'QS', 'JH', 'TC']
        position (int): プレイヤーのポジション（例: 0, 1, 2, ...）
    Returns:
        bool: レイズすべきかどうか
    """

    hand_range = get_preflop_hand_range(position, raise_cnt, tool_context)

    # 正規化: your_cards を強い順（ランクの降順）にソートしてからマッチング
    parsed: Tuple[Tuple[int, str], Tuple[int, str]] = (
        parse_card(cards[0]),
        parse_card(cards[1]),
    )
    sorted_pair: Tuple[Tuple[int, str], Tuple[int, str]] = tuple(sorted(parsed, key=lambda x: x[0], reverse=True))  # type: ignore

    # 一部のレンジデータではキーのタプル順序が一定でない可能性があるため、
    # 念のため逆順もチェックして堅牢性を上げる
    candidates = [sorted_pair, (sorted_pair[1], sorted_pair[0])]

    for d in hand_range["hand_range"]:
        if not isinstance(d, dict):
            continue
        for key, value in d.items():
            if key in candidates:
                return value

    return False

def parse_card(token):
    # 例: 'A♥', '10♣', 'T♣', 'AH', 'Ts', 'qd' などを受け付ける
    if not token or len(token) < 2:
        raise ValueError(f"不正なカード表記: {token}")

    rank_to_num = {'A': 14, 'K': 13, 'Q': 12, 'J': 11,'T': 10, '10': 10, '9': 9, '8': 8, '7': 7,
                '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}
    unicode_suits = {'♠': 'S', '♥': 'H', '♦': 'D', '♣': 'C'}
    ascii_suits = {'S': 'S', 'H': 'H', 'D': 'D', 'C': 'C','s': 'S', 'h': 'H', 'd': 'D', 'c': 'C'}

    suit_char = token[-1]
        # スート正規化
    if suit_char in unicode_suits:
            suit = unicode_suits[suit_char]
            rank_str = token[:-1]
    elif suit_char in ascii_suits:
            suit = ascii_suits[suit_char]
            rank_str = token[:-1]
    else:
            # 末尾がスートでない場合のフォールバック（従来仕様: 2文字固定 like 'AS'）
            # ただし新仕様では基本的に末尾がスートのはず
            if len(token) == 2:
                rank_str, suit_raw = token[0], token[1]
                suit = ascii_suits.get(suit_raw, unicode_suits.get(suit_raw, None))
                if suit is None:
                    raise ValueError(f"不正なスート表記: {suit_raw}")
            else:
                raise ValueError(f"不正なカード表記: {token}")

        # ランク正規化（'10' と 'T' を同一視、英字は大文字化）
    rank_str = rank_str.upper()
    if rank_str == '10':
        rank_key = '10'
    elif len(rank_str) == 1 and rank_str in {'A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'}:
        rank_key = rank_str
    else:
        # 例えば 't' などは upper 済みなのでこの条件に入らない
        raise ValueError(f"不正なランク表記: {rank_str}")

    return rank_to_num[rank_key], suit

def get_preflop_hand_range(position: int, raise_cnt: int, tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieves hand range, converts based on session state."""
    print(f"--- Tool: get_preflop_hand_range called for position {position} ---")

    srp_hand_range_db = {
        0: range_0_open,
        1: range_1_open,
        3: range_3_open,
        4: range_4_open,
    }

    nrp_hand_range_db = {
        1: range_3bet,
        2: range_4bet,
        3: range_5bet,
    }

    if raise_cnt >= 1:
        tool_context.state["hand_range"] = nrp_hand_range_db[raise_cnt]
        result = {
            "status": "success",
            "hand_range": tool_context.state["hand_range"],
            "message": f"Hand range for raise count {raise_cnt} retrieved.",
        }
        return result
    elif position in srp_hand_range_db:
        tool_context.state["hand_range"] = srp_hand_range_db[position]

        print(f"--- Tool: Updated state 'hand_range': ---")

        result = {"status": "success", "hand_range": tool_context.state["hand_range"], "message": f"Hand range for position {position} retrieved."}
        return result
    else:
        # Handle position not found
        error_msg = f"Sorry, I don't have hand range information for position {position}."
        print(f"--- Tool: Position '{position}' not found. ---")
        return {"status": "error", "hand_range": [], "error_message": error_msg}
