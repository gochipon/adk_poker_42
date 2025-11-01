import unittest
from typing import Dict, Literal, Optional, List, Tuple
from .judge_preflop_range import calculate_position

# --- テスト対象の関数とデータ ---
# 実際には `poker_range_analyzer` ファイルから import します
# from poker_range_analyzer import calculate_position

# 5-max専用のマップは不要になるため削除
# POSITION_MAP_5MAX: Dict[int, Literal["BTN", "SB", "BB", "MP", "CO"]] = ...

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
# --- テスト対象の定義ここまで ---


class TestCalculatePosition(unittest.TestCase): # クラス名を変更

    def test_6max_positions(self):
        """6-maxでのポジション割り当てをテストします (ID: 0-5)"""
        num_players = 6
        # (dealer_button_id, your_id, expected_position)
        test_cases = [
            (0, 0, "BTN"), (0, 1, "SB"), (0, 2, "BB"), (0, 3, "UTG"), (0, 4, "MP"), (0, 5, "CO"),
            (1, 0, "CO"), (1, 1, "BTN"), (1, 2, "SB"), (1, 3, "BB"), (1, 4, "UTG"), (1, 5, "MP"),
            (2, 0, "MP"), (2, 1, "CO"), (2, 2, "BTN"), (2, 3, "SB"), (2, 4, "BB"), (2, 5, "UTG"),
            (3, 0, "UTG"), (3, 1, "MP"), (3, 2, "CO"), (3, 3, "BTN"), (3, 4, "SB"), (3, 5, "BB"),
            (4, 0, "BB"), (4, 1, "UTG"), (4, 2, "MP"), (4, 3, "CO"), (4, 4, "BTN"), (4, 5, "SB"),
            (5, 0, "SB"), (5, 1, "BB"), (5, 2, "UTG"), (5, 3, "MP"), (5, 4, "CO"), (5, 5, "BTN"),
        ]
        
        for dealer_id, your_id, expected in test_cases:
            with self.subTest(f"6-max: BTN={dealer_id}, YourID={your_id}"):
                self.assertEqual(
                    calculate_position(your_id, dealer_id, num_players),
                    expected
                )

    def test_5max_positions(self):
        """5-maxでのポジション割り当てをテストします (ID: 0-4)"""
        num_players = 5
        # (dealer_button_id, your_id, expected_position)
        test_cases = [
            (0, 0, "BTN"), (0, 1, "SB"), (0, 2, "BB"), (0, 3, "MP"), (0, 4, "CO"),
            (1, 0, "CO"), (1, 1, "BTN"), (1, 2, "SB"), (1, 3, "BB"), (1, 4, "MP"),
            (2, 0, "MP"), (2, 1, "CO"), (2, 2, "BTN"), (2, 3, "SB"), (2, 4, "BB"),
            (3, 0, "BB"), (3, 1, "MP"), (3, 2, "CO"), (3, 3, "BTN"), (3, 4, "SB"),
            (4, 0, "SB"), (4, 1, "BB"), (4, 2, "MP"), (4, 3, "CO"), (4, 4, "BTN"),
        ]
        
        for dealer_id, your_id, expected in test_cases:
            with self.subTest(f"5-max: BTN={dealer_id}, YourID={your_id}"):
                self.assertEqual(
                    calculate_position(your_id, dealer_id, num_players),
                    expected
                )

    def test_4max_positions(self):
        """4-maxでのポジション割り当てをテストします (ID: 0-3)"""
        num_players = 4
        # (dealer_button_id, your_id, expected_position)
        test_cases = [
            (0, 0, "BTN"), (0, 1, "SB"), (0, 2, "BB"), (0, 3, "CO"),
            (1, 0, "CO"), (1, 1, "BTN"), (1, 2, "SB"), (1, 3, "BB"),
            (2, 0, "BB"), (2, 1, "CO"), (2, 2, "BTN"), (2, 3, "SB"),
            (3, 0, "SB"), (3, 1, "BB"), (3, 2, "CO"), (3, 3, "BTN"),
        ]
        
        for dealer_id, your_id, expected in test_cases:
            with self.subTest(f"4-max: BTN={dealer_id}, YourID={your_id}"):
                self.assertEqual(
                    calculate_position(your_id, dealer_id, num_players),
                    expected
                )

    def test_3max_positions(self):
        """3-maxでのポジション割り当てをテストします (ID: 0-2)"""
        num_players = 3
        # (dealer_button_id, your_id, expected_position)
        test_cases = [
            (0, 0, "BTN"), (0, 1, "SB"), (0, 2, "BB"),
            (1, 0, "BB"), (1, 1, "BTN"), (1, 2, "SB"),
            (2, 0, "SB"), (2, 1, "BB"), (2, 2, "BTN"),
        ]
        
        for dealer_id, your_id, expected in test_cases:
            with self.subTest(f"3-max: BTN={dealer_id}, YourID={your_id}"):
                self.assertEqual(
                    calculate_position(your_id, dealer_id, num_players),
                    expected
                )

    # --- 2-max (Heads-Up) のテストを追加 ---
    def test_2max_positions(self):
        """2-max (Heads-Up) でのポジション割り当てをテストします (ID: 0-1)"""
        num_players = 2
        # (dealer_button_id, your_id, expected_position)
        test_cases = [
            (0, 0, "BTN"), (0, 1, "BB"), # BTN=0, SB=0, BB=1
            (1, 0, "BB"), (1, 1, "BTN"), # BTN=1, SB=1, BB=0
        ]
        
        for dealer_id, your_id, expected in test_cases:
            with self.subTest(f"2-max: BTN={dealer_id}, YourID={your_id}"):
                self.assertEqual(
                    calculate_position(your_id, dealer_id, num_players),
                    expected
                )

    def test_invalid_num_players(self):
        """
        サポート範囲外 (2未満または6超) の場合、Noneが返されることをテストします。
        """
        # (your_id, dealer_button_id, num_players)
        invalid_cases = [
            (0, 0, 1), # 1-handed
            (0, 0, 7), # 7-handed
            (0, 0, 0),
        ]
        
        for your_id, dealer_id, num_players in invalid_cases:
            with self.subTest(f"YourID={your_id}, BTN={dealer_id}, Num={num_players}"):
                self.assertIsNone(
                    calculate_position(your_id, dealer_id, num_players),
                    f"{num_players} players should return None"
                )

    # num_players が必須引数になったため、test_default_num_players は削除

if __name__ == '__main__':
    unittest.main()