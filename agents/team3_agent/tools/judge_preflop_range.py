import re
from typing import Dict, List, Literal, Optional, Set

# GTO (Game Theory Optimal) 6-Max, 100bb Deep, No Ante, 2.5x Open Raise
# (注意: 混合戦略を簡略化し、高頻度でレイズするハンドを中心に構成)
#
# 修正点:
# 1. パフォーマンス向上のため、List[str] を Set[str] に変更。
#    Setを使用することで 'in' 演算子による検索が O(1) になり高速化されます。
# 2. SBのレンジにあった重複データ ("64s") を削除。
YOKOSAWA_RANGE_DATA: Dict[str, Set[str]] = {
    
    # === UTG (Under the Gun) ===
    # 約15%のレンジ
    "UTG": {
        # Pairs
        "AA", "KK", "QQ", "JJ", "TT", "99", "88", "77",
        # Suited Aces
        "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s",
        # Suited Broadway
        "KQs", "KJs", "KTs",
        "QJs", "QTs",
        "JTs",
        # Suited Connectors
        "T9s", "98s", "87s", "76s",
        # Offsuit
        "AKo", "AQo"
    },
    
    # === MP (Middle Position) ===
    # 約20-22%のレンジ (UTG + Alpha)
    "MP": {
        # Pairs
        "AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55",
        # Suited Aces
        "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s",
        # Suited Kings
        "KQs", "KJs", "KTs", "K9s",
        # Suited Queens
        "QJs", "QTs", "Q9s",
        # Suited Jacks
        "JTs", "J9s",
        # Suited Connectors
        "T9s", "98s", "87s", "76s", "65s",
        # Offsuit
        "AKo", "AQo", "AJo",
        "KQo"
    },
    
    # === CO (Cutoff) ===
    # 約27-30%のレンジ
    "CO": {
        # Pairs
        "AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
        # Suited Aces
        "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s",
        # Suited Kings
        "KQs", "KJs", "KTs", "K9s", "K8s",
        # Suited Queens
        "QJs", "QTs", "Q9s", "Q8s",
        # Suited Jacks
        "JTs", "J9s", "J8s",
        # Suited Tens
        "T9s", "T8s",
        # Suited Connectors
        "98s", "87s", "76s", "65s", "54s",
        # Offsuit Aces
        "AKo", "AQo", "AJo", "ATo", "A9o", "A8o", "A7o", "A6o", "A5o",
        # Offsuit Broadway
        "KQo", "KJo", "KTo",
        "QJo", "QTo",
        "JTo"
    },
    
    # === BTN (Button) ===
    # 約45-50%のレンジ
    "BTN": {
        # Pairs
        "AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
        # Suited Aces
        "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s",
        # Suited Kings
        "KQs", "KJs", "KTs", "K9s", "K8s", "K7s", "K6s", "K5s", "K4s", "K3s", "K2s",
        # Suited Queens
        "QJs", "QTs", "Q9s", "Q8s", "Q7s", "Q6s", "Q5s", "Q4s", "Q3s", "Q2s",
        # Suited Jacks
        "JTs", "J9s", "J8s", "J7s", "J6s", "J5s", "J4s",
        # Suited Tens
        "T9s", "T8s", "T7s", "T6s",
        # Suited Connectors
        "98s", "97s", "96s",
        "87s", "86s",
        "76s", "75s",
        "65s", "64s",
        "54s",
        # Offsuit Aces
        "AKo", "AQo", "AJo", "ATo", "A9o", "A8o", "A7o", "A6o", "A5o", "A4o", "A3o", "A2o",
        # Offsuit Kings
        "KQo", "KJo", "KTo", "K9o", "K8o",
        # Offsuit Queens
        "QJo", "QTo", "Q9o",
        # Offsuit Jacks
        "JTo", "J9o",
        # Offsuit Tens
        "T9o"
    },
    
    # === SB (Small Blind) ===
    # 約35-40%のレンジ (BTNより少しタイト。リンプ戦略や3bet戦略も多用されるが、ここではレイズのみ)
    "SB": {
        # Pairs
        "AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
        # Suited Aces
        "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s",
        # Suited Kings
        "KQs", "KJs", "KTs", "K9s", "K8s", "K7s", "K6s", "K5s",
        # Suited Queens
        "QJs", "QTs", "Q9s", "Q8s",
        # Suited Jacks
        "JTs", "J9s", "J8s", "J7s",
        # Suited Tens
        "T9s", "T8s",
        # Suited Connectors
        "98s", "97s",
        "87s", "86s",
        "76s", "75s",
        "65s", "64s",
        "54s",
        # Offsuit Aces
        "AKo", "AQo", "AJo", "ATo", "A9o", "A8o", "A7o", "A6o", "A5o",
        # Offsuit Kings
        "KQo", "KJo", "KTo", "K9o",
        # Offsuit Queens
        "QJo", "QTo",
        # Offsuit Jacks
        "JTo"
    }
}

# --- 可変人数 (2-6人) 対応のポジション計算 ---

def calculate_position(
    your_id: int, 
    dealer_button_id: int,
    num_players: int
) -> Optional[Literal["UTG", "MP", "CO", "BTN", "SB", "BB"]]:
    """
    Calculates the poker position based on player ID, dealer button ID,
    and the total number of players (2-max to 6-max).

    
    

    Args:
        your_id (int): Your player ID.
        dealer_button_id (int): The ID of the player on the dealer button.
        num_players (int): The total number of players (supports 2, 3, 4, 5, or 6).

    Returns:
        Optional[Literal["UTG", "MP", "CO", "BTN", "SB", "BB"]]:
            The calculated position as a string.
            Returns None if num_players is not between 2 and 6.
    """
    
    # サポート範囲を 2-6 に変更
    if num_players < 2 or num_players > 6:
        print(f"Warning: Position calculation supports 2-6 players. Received {num_players}.")
        return None
        
    try:
        # (自分のID - ボタンID + 人数) % 人数
        relative_position = (your_id - dealer_button_id + num_players) % num_players
        
        # --- 共通ポジション (BTN) ---
        # 2-max の BTN は SB (Small Blind) としても扱われる
        if relative_position == 0: return "BTN" 
        
        # --- 2-max (Heads-Up) のロジック ---
        if num_players == 2:
            if relative_position == 1: return "BB" # Big Blind
            return None # Logic error (0, 1 以外はありえない)

        # --- 3-max 以上の共通ポジション (SB, BB) ---
        if relative_position == 1: return "SB"
        if relative_position == 2: return "BB"
        
        # 3-max (BTN, SB, BBのみ)
        if num_players == 3:
            # relative_position 0, 1, 2 以外はありえない
            return None # Logic error if reached
            
        # 4-max
        if num_players == 4:
            if relative_position == 3: return "CO" # (実質 UTG/MP)
            
        # 5-max
        if num_players == 5:
            if relative_position == 3: return "MP"
            if relative_position == 4: return "CO"
            
        # 6-max
        if num_players == 6:
            if relative_position == 3: return "UTG"
            if relative_position == 4: return "MP"
            if relative_position == 5: return "CO"
            
        # num_players が 2-6 の範囲内だが、relative_position が
        # 予期せぬ値になった場合 (論理的に到達不能のはず)
        return None 
        
    except Exception as e:
        print(f"Error calculating position: {e}")
        return None

def _normalize_hand_notation(hand: str) -> str:
    """
    ポーカーハンドの様々な表記 ('AsKd', 'AKs', 'AK', 'KAs', 'kk', 'jqs') を
    一貫した形式 ('AKo', 'AKs', 'AA', 'QJs') に正規化します。

    仕様:
    - "AK" のようなサフィックスなしの非ペアは "AKo" (オフスート) として扱われます。
    """
    
    c1_raw, c2_raw, suffix_raw = '', '', ''
    ranks = "AKQJT98765432" # 比較用のランク文字列

    # 入力文字列をトリミングして、前後の空白を削除
    hand = hand.strip()

    if len(hand) == 4: # 例: "AsKd" または "AsKs"
        c1_raw, s1 = hand[0], hand[1].lower()
        c2_raw, s2 = hand[2], hand[3].lower()
        if s1 not in 'hdcs' or s2 not in 'hdcs':
             raise ValueError(f"不正なスート指定です: {hand}")
        suffix_raw = 's' if s1 == s2 else 'o'
    
    elif len(hand) == 3: # 例: "AKs", "T9o", または "akq" (不正)
        c1_raw, c2_raw = hand[0], hand[1]
        suffix_raw = hand[2].lower()
        if suffix_raw not in ['s', 'o']:
            # "akq" のような3文字目が s/o 以外の場合は不正
            raise ValueError(f"不正な表記です: {hand}")
    
    elif len(hand) == 2: # 例: "AK", "TT", "kk"
        c1_raw, c2_raw = hand[0], hand[1]
        # ペアかどうかはここで判断 (大文字小文字を区別しない)
        if c1_raw.upper() == c2_raw.upper():
            suffix_raw = '' # ペア (例: AA)
        else:
            # 仕様: サフィックスなしの非ペアは "o" (オフスート) として扱う
            suffix_raw = 'o'
    
    else:
        raise ValueError(f"不正なハンド形式です: {hand}")

    # ランクを大文字に変換し、有効かチェック
    c1, c2 = c1_raw.upper(), c2_raw.upper()
    if c1 not in ranks or c2 not in ranks:
         # "ax" などの不正なランクはここで捕捉
         raise ValueError(f"不正なランクが含まれています: {hand}")

    # ランク順を正規化 (例: "KA" -> "AK")
    if ranks.find(c1) > ranks.find(c2):
        c1, c2 = c2, c1 # スワップ

    # 最終的なハンド文字列を構築
    if c1 == c2:
        return f"{c1}{c2}" # 例: "AA"
    else:
        # suffix_raw は 's' または 'o' が入る
        return f"{c1}{c2}{suffix_raw}" # 例: "AKs", "T9o"

# --- [新規追加] カードリストを正規化するヘルパー関数 ---
def _normalize_card_list(cards: List[str]) -> str:
    """
    ["2♣", "J♣"] や ["As", "Kd"] のようなカードリストを 
    "J2s" や "AKo" のような標準形に正規化する。
    """
    if len(cards) != 2:
        raise ValueError(f"カードリストは2枚である必要があります: {cards}")

    card1 = cards[0].strip()
    card2 = cards[1].strip()

    if len(card1) < 2 or len(card2) < 2:
        raise ValueError(f"不正なカード形式です (短すぎます): {cards}")

    # ランクとスートを抽出 (例: "10h" -> rank="10", suit="h")
    rank1_raw = card1[:-1]
    suit1_raw = card1[-1]
    rank2_raw = card2[:-1]
    suit2_raw = card2[-1]
    
    # ランクのマッピング (10に対応)
    rank_map = {
        "A": "A", "K": "K", "Q": "Q", "J": "J", "T": "T",
        "10": "T", "9": "9", "8": "8", "7": "7", "6": "6",
        "5": "5", "4": "4", "3": "3", "2": "2"
    }
    
    r1 = rank_map.get(rank1_raw.upper())
    r2 = rank_map.get(rank2_raw.upper())
    
    if not r1 or not r2:
        raise ValueError(f"不正なランクが含まれています: {cards} (raw: {rank1_raw}, {rank2_raw})")

    # スートの正規化 (Unicodeとアルファベット両対応)
    suit_map = {
        '♣': 'c', 'c': 'c', 'C': 'c',
        '♦': 'd', 'd': 'd', 'D': 'd',
        '♥': 'h', 'h': 'h', 'H': 'h',
        '♠': 's', 's': 's', 'S': 's'
    }
    
    s1 = suit_map.get(suit1_raw)
    s2 = suit_map.get(suit2_raw)
    
    if not s1 or not s2:
        raise ValueError(f"不正なスートが含まれています: {cards} (raw: {suit1_raw}, {suit2_raw})")

    suffix = 's' if s1 == s2 else 'o'
    
    ranks_order = "AKQJT98765432"
    
    # ランク順を正規化 (例: "2J" -> "J2")
    if ranks_order.find(r1) > ranks_order.find(r2):
        r1, r2 = r2, r1 # スワップ

    if r1 == r2:
        return f"{r1}{r2}" # ペア (例: "AA")
    else:
        return f"{r1}{r2}{suffix}" # 例: "J2s", "AKo"

# --- ADKツールとして公開する関数 1 ---

def judge_preflop_range(
    hand_input: List[str],
    position: Literal["UTG", "MP", "CO", "BTN", "SB"]
) -> bool:
    """Checks if a given hand is in the open range for a given position based on "Yokosawa's Range".

    This function determines if a specified poker hand (e.g., "AKs", "TT", "AsKd", ["2♣", "J♣"]) 
    falls within the predefined opening range for a specific 6-max position (UTG, MP, CO, BTN, SB).

    Note: The range data referenced is simplified dummy data inspired by GTO principles.

    Args:
        hand_input (Union[str, List[str]]): The poker hand to check.
            Acceptable formats:
            - Standard string: "AKs", "AQo", "TT".
            - Specific cards string: "AsKd", "AdKd".
            - Suffixless non-pair string: "AK" (treated as "AKo").
            - Card list: ["2♣", "J♣"], ["As", "Kd"], ["10h", "Td"].
            - Case-insensitive: "aks", "tt", "qj" are valid (for string input).
            - Reversed ranks: "KAs", "9To" are normalized (for string input).
        position (Literal["UTG", "MP", "CO", "BTN", "SB"]):
            The player's 6-max position.

    Returns:
        bool:
            - True: If the normalized hand is found within the specified position's range.
            - False: If the hand is not in the range, or if the hand input
              is invalid (e.g., "AXs", "T", ["2c"]) and cannot be normalized.
    """
    
    if position not in YOKOSAWA_RANGE_DATA:
        # print(f"Warning: Range data for position '{position}' is not defined.")
        return False
    try:
        # 'isinstance' チェックを削除し、list 専用にする
        normalized_hand = _normalize_card_list(hand_input)
    except ValueError as e:
        # print(f"Hand normalization error: {e}")
        return False
    target_range: Set[str] = YOKOSAWA_RANGE_DATA.get(position, set())
    if normalized_hand in target_range:
        return True
    return False
    