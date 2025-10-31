import unittest
from typing import Dict, List, Literal, Optional, Set, Union
# テスト対象のモジュール（上記ファイルが 'poker_range_analyzer.py' として保存されている想定）
from .judge_preflop_range import _normalize_hand_notation, judge_preflop_range, YOKOSAWA_RANGE_DATA

class TestNormalizeHandNotation(unittest.TestCase):
    """
    _normalize_hand_notation 関数の厳格なテスト。
    あらゆる表記パターンと不正な入力をテストします。
    """

    def test_valid_pairs(self):
        self.assertEqual(_normalize_hand_notation("AA"), "AA")
        self.assertEqual(_normalize_hand_notation("kk"), "KK")
        self.assertEqual(_normalize_hand_notation("22"), "22")
        self.assertEqual(_normalize_hand_notation(" qQ "), "QQ") # 空白トリムのテスト

    def test_valid_suited(self):
        self.assertEqual(_normalize_hand_notation("AKs"), "AKs")
        self.assertEqual(_normalize_hand_notation("aks"), "AKs")
        self.assertEqual(_normalize_hand_notation("T9s"), "T9s")
        self.assertEqual(_normalize_hand_notation("t9s"), "T9s")

    def test_valid_offsuit(self):
        self.assertEqual(_normalize_hand_notation("AKo"), "AKo")
        self.assertEqual(_normalize_hand_notation("ako"), "AKo")
        self.assertEqual(_normalize_hand_notation("T9o"), "T9o")
        self.assertEqual(_normalize_hand_notation("t9o"), "T9o")

    def test_valid_suffixless_non_pair(self):
        """仕様: サフィックスなしの非ペアはオフスート(o)として扱われる"""
        self.assertEqual(_normalize_hand_notation("AK"), "AKo")
        self.assertEqual(_normalize_hand_notation("ak"), "AKo")
        self.assertEqual(_normalize_hand_notation("T9"), "T9o")
        self.assertEqual(_normalize_hand_notation("t9"), "T9o")

    def test_valid_rank_order_swap(self):
        """ランク順が逆でも正しく正規化されるか"""
        # Suited
        self.assertEqual(_normalize_hand_notation("KAs"), "AKs")
        self.assertEqual(_normalize_hand_notation("kAs"), "AKs")
        self.assertEqual(_normalize_hand_notation("9Ts"), "T9s")
        # Offsuit
        self.assertEqual(_normalize_hand_notation("KAo"), "AKo")
        self.assertEqual(_normalize_hand_notation("kAo"), "AKo")
        self.assertEqual(_normalize_hand_notation("9To"), "T9o")
        # Suffixless
        self.assertEqual(_normalize_hand_notation("KA"), "AKo")
        self.assertEqual(_normalize_hand_notation("kA"), "AKo")
        self.assertEqual(_normalize_hand_notation("9T"), "T9o")

    def test_valid_four_char_notation(self):
        """4文字表記 (例: AsKd) のテスト"""
        # Suited
        self.assertEqual(_normalize_hand_notation("AsKs"), "AKs")
        self.assertEqual(_normalize_hand_notation("khqh"), "KQs")
        self.assertEqual(_normalize_hand_notation("2d2d"), "22")
        # Offsuit
        self.assertEqual(_normalize_hand_notation("AsKd"), "AKo")
        self.assertEqual(_normalize_hand_notation("khqc"), "KQo")
        self.assertEqual(_normalize_hand_notation("2d2h"), "22") # ペアの場合はスートが違っても 'o' は付かない
        # Rank swap
        self.assertEqual(_normalize_hand_notation("KdAs"), "AKo")
        self.assertEqual(_normalize_hand_notation("KsAs"), "AKs")
        self.assertEqual(_normalize_hand_notation("JhTh"), "JTs")

    def test_invalid_length(self):
        with self.assertRaises(ValueError):
            _normalize_hand_notation("")
        with self.assertRaises(ValueError):
            _normalize_hand_notation("A")
        with self.assertRaises(ValueError):
            _normalize_hand_notation("AKQ") # 3文字だが末尾が s/o ではない
        with self.assertRaises(ValueError):
            _normalize_hand_notation("AsKdh")

    def test_invalid_ranks(self):
        with self.assertRaises(ValueError):
            _normalize_hand_notation("AXs")
        with self.assertRaises(ValueError):
            _normalize_hand_notation("A1o")
        with self.assertRaises(ValueError):
            _normalize_hand_notation("K0")
        with self.assertRaises(ValueError):
            _normalize_hand_notation("AsXd")
        with self.assertRaises(ValueError):
            _normalize_hand_notation("Ax")

    def test_invalid_suffix_or_suit(self):
        with self.assertRaises(ValueError):
            _normalize_hand_notation("AKx") # 不正なサフィックス
        with self.assertRaises(ValueError):
            _normalize_hand_notation("T9z")
        with self.assertRaises(ValueError):
            _normalize_hand_notation("AsKx") # 不正なスート
        with self.assertRaises(ValueError):
            _normalize_hand_notation("Ashd") # s がスート (スペード) なのかサフィックスなのか曖昧 (この実装ではスートとして解釈)
        with self.assertRaises(ValueError):
            _normalize_hand_notation("AcQz")


class TestJudgePreflopRange(unittest.TestCase):
    """
    judge_preflop_range 関数の厳格なテスト。
    各ポジションの境界値（含まれるハンド、含まれないハンド）をテストします。
    """

    def test_utg_range(self):
        pos = "UTG"

        # リスト形式 (True)
        self.assertTrue(judge_preflop_range(["As", "Ks"], pos)) # AKs
        self.assertTrue(judge_preflop_range(["Ac", "Qd"], pos)) # AQo
        
        # リスト形式 (False)
        self.assertFalse(judge_preflop_range(["6c", "6d"], pos)) # 66
        self.assertFalse(judge_preflop_range(["Kc", "9c"], pos)) # K9s

    def test_mp_range(self):
        pos = "MP"
        # リスト形式
        self.assertTrue(judge_preflop_range(["5c", "5h"], pos)) # 55
        self.assertTrue(judge_preflop_range(["Ad", "Jc"], pos)) # AJo
        self.assertFalse(judge_preflop_range(["4s", "4d"], pos)) # 44
        self.assertFalse(judge_preflop_range(["Ac", "Td"], pos)) # ATo

    def test_co_range(self):
        pos = "CO"

        # リスト形式
        self.assertTrue(judge_preflop_range(["2c", "2d"], pos)) # 22
        self.assertTrue(judge_preflop_range(["Ac", "Tc"], pos)) # ATs
        self.assertFalse(judge_preflop_range(["Ks", "7s"], pos)) # K7s
        self.assertFalse(judge_preflop_range(["Ad", "4c"], pos)) # A4o
        
    def test_btn_range(self):
        pos = "BTN"

        # リスト形式
        self.assertTrue(judge_preflop_range(["Kc", "2c"], pos)) # K2s
        self.assertTrue(judge_preflop_range(["Ad", "2h"], pos)) # A2o
        self.assertTrue(judge_preflop_range(["Tc", "9d"], pos)) # T9o
        self.assertFalse(judge_preflop_range(["Jd", "3d"], pos)) # J3s
        self.assertFalse(judge_preflop_range(["Qc", "8d"], pos)) # Q8o

    def test_sb_range(self):
        pos = "SB"

        # リスト形式
        self.assertTrue(judge_preflop_range(["Kd", "5d"], pos)) # K5s
        self.assertTrue(judge_preflop_range(["Ac", "5h"], pos)) # A5o
        self.assertFalse(judge_preflop_range(["Kh", "4h"], pos)) # K4s
        self.assertTrue(judge_preflop_range(["Ac", "4c"], pos)) # A4s (これはTrueのはず)
        self.assertTrue(judge_preflop_range(["Ac", "4c"], pos))  # A4s (SBレンジ内)
        self.assertFalse(judge_preflop_range(["Ac", "4d"], pos)) # A4o (SBレンジ外)

    def test_invalid_and_edge_cases(self):
        pos = "UTG"
        
        # 無効なリスト
        self.assertFalse(judge_preflop_range(["As"], pos)) # 1枚
        self.assertFalse(judge_preflop_range(["As", "Kd", "Qc"], pos)) # 3枚
        self.assertFalse(judge_preflop_range(["As", "Xh"], pos)) # 不正なランク
        self.assertFalse(judge_preflop_range(["As", "K!"], pos)) # 不正なスート
        self.assertFalse(judge_preflop_range(["11h", "9c"], pos)) # 不正なランク
        

        # ユーザーリクエストのケース (J2s)
        self.assertFalse(judge_preflop_range(["2♣", "J♣"], "UTG"))
        self.assertFalse(judge_preflop_range(["2♣", "J♣"], "MP"))
        self.assertFalse(judge_preflop_range(["2♣", "J♣"], "CO"))
        self.assertFalse(judge_preflop_range(["2♣", "J♣"], "BTN"))
        self.assertFalse(judge_preflop_range(["2♣", "J♣"], "SB"))

    def test_notation_variants(self):
        
        # '10' 表記 (リスト)
        self.assertTrue(judge_preflop_range(["10h", "9d"], "BTN")) # T9o
        self.assertTrue(judge_preflop_range(["10c", "10d"], "UTG")) # TT
        self.assertTrue(judge_preflop_range(["A♥", "10♥"], "UTG")) # ATs
        
        # Unicode (リスト)
        self.assertTrue(judge_preflop_range(["K♣", "Q♣"], "UTG")) # KQs
        self.assertTrue(judge_preflop_range(["A♠", "K♥"], "UTG")) # AKo


if __name__ == '__main__':
    # 実行方法:
    # 1. 上記の2つのコードブロックをそれぞれ
    #    'poker_range_analyzer.py' と 'test_poker_range_analyzer.py' として保存します。
    # 2. ターミナルで 'test_poker_range_analyzer.py' があるディレクトリに移動します。
    # 3. 'python -m unittest test_poker_range_analyzer.py' を実行します。
    unittest.main(argv=['first-arg-is-ignored'], exit=False)