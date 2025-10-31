import unittest
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
        # 含まれる (True)
        self.assertTrue(judge_preflop_range("AA", "UTG"))
        self.assertTrue(judge_preflop_range("KK", "UTG"))
        self.assertTrue(judge_preflop_range("AKs", "UTG"))
        self.assertTrue(judge_preflop_range("AKo", "UTG"))
        self.assertTrue(judge_preflop_range("AQs", "UTG"))
        self.assertTrue(judge_preflop_range("AQo", "UTG"))
        self.assertTrue(judge_preflop_range("77", "UTG"))
        self.assertTrue(judge_preflop_range("76s", "UTG"))
        self.assertTrue(judge_preflop_range("A2s", "UTG"))
        # 含まれない (False)
        self.assertFalse(judge_preflop_range("66", "UTG"))
        self.assertFalse(judge_preflop_range("AJo", "UTG"))
        self.assertFalse(judge_preflop_range("KTo", "UTG"))
        self.assertFalse(judge_preflop_range("22", "UTG"))
        self.assertFalse(judge_preflop_range("75s", "UTG"))
        self.assertFalse(judge_preflop_range("A9o", "UTG"))

    def test_mp_range(self):
        # 含まれる (True)
        self.assertTrue(judge_preflop_range("AA", "MP"))
        self.assertTrue(judge_preflop_range("66", "MP")) # UTGではFalse
        self.assertTrue(judge_preflop_range("55", "MP")) # UTGではFalse
        self.assertTrue(judge_preflop_range("AJo", "MP")) # UTGではFalse
        self.assertTrue(judge_preflop_range("KQo", "MP")) # UTGではFalse
        self.assertTrue(judge_preflop_range("65s", "MP"))
        # 含まれない (False)
        self.assertFalse(judge_preflop_range("44", "MP"))
        self.assertFalse(judge_preflop_range("A9o", "MP"))
        self.assertFalse(judge_preflop_range("J8s", "MP"))

    def test_co_range(self):
        # 含まれる (True)
        self.assertTrue(judge_preflop_range("AA", "CO"))
        self.assertTrue(judge_preflop_range("22", "CO")) # MPではFalse
        self.assertTrue(judge_preflop_range("A5o", "CO")) # MPではFalse
        self.assertTrue(judge_preflop_range("KTo", "CO"))
        self.assertTrue(judge_preflop_range("JTo", "CO"))
        self.assertTrue(judge_preflop_range("54s", "CO"))
        # 含まれない (False)
        self.assertFalse(judge_preflop_range("A4o", "CO"))
        self.assertFalse(judge_preflop_range("K9o", "CO"))
        self.assertFalse(judge_preflop_range("J9o", "CO"))

    def test_btn_range(self):
        # 含まれる (True)
        self.assertTrue(judge_preflop_range("AA", "BTN"))
        self.assertTrue(judge_preflop_range("22", "BTN"))
        self.assertTrue(judge_preflop_range("A2o", "BTN")) # COではFalse
        self.assertTrue(judge_preflop_range("K9o", "BTN")) # COではFalse
        self.assertTrue(judge_preflop_range("Q9o", "BTN"))
        self.assertTrue(judge_preflop_range("J9o", "BTN"))
        self.assertTrue(judge_preflop_range("T9o", "BTN"))
        self.assertTrue(judge_preflop_range("K2s", "BTN"))
        self.assertTrue(judge_preflop_range("Q2s", "BTN"))
        self.assertTrue(judge_preflop_range("J4s", "BTN"))
        self.assertTrue(judge_preflop_range("54s", "BTN"))
        # 含まれない (False) - BTNは広いため除外されるハンドは少ない
        self.assertFalse(judge_preflop_range("K7o", "BTN"))
        self.assertFalse(judge_preflop_range("Q8o", "BTN"))
        self.assertFalse(judge_preflop_range("J8o", "BTN"))
        self.assertFalse(judge_preflop_range("T8o", "BTN"))
        self.assertFalse(judge_preflop_range("98o", "BTN"))

    def test_sb_range(self):
        # 含まれる (True)
        self.assertTrue(judge_preflop_range("AA", "SB"))
        self.assertTrue(judge_preflop_range("22", "SB"))
        self.assertTrue(judge_preflop_range("A5o", "SB"))
        self.assertTrue(judge_preflop_range("K9o", "SB"))
        self.assertTrue(judge_preflop_range("QTo", "SB"))
        self.assertTrue(judge_preflop_range("JTo", "SB"))
        self.assertTrue(judge_preflop_range("54s", "SB"))
        self.assertTrue(judge_preflop_range("64s", "SB")) # 重複削除後も存在確認
        # 含まれない (False) - BTNにはあるがSBにはないハンド
        self.assertFalse(judge_preflop_range("A4o", "SB"))
        self.assertFalse(judge_preflop_range("A3o", "SB"))
        self.assertFalse(judge_preflop_range("A2o", "SB"))
        self.assertFalse(judge_preflop_range("K8o", "SB"))
        self.assertFalse(judge_preflop_range("Q9o", "SB"))
        self.assertFalse(judge_preflop_range("J9o", "SB"))
        self.assertFalse(judge_preflop_range("T9o", "SB"))
        self.assertFalse(judge_preflop_range("K4s", "SB"))
        self.assertFalse(judge_preflop_range("Q3s", "SB"))
        self.assertFalse(judge_preflop_range("J5s", "SB"))

    def test_invalid_position(self):
        """レンジデータが存在しないポジションのテスト"""
        # "BB" はオープンレンジとしては定義されていないため False
        self.assertFalse(judge_preflop_range("AA", "BB"))
        # Literal型で制限されているが、万が一不正な文字列が来た場合
        self.assertFalse(judge_preflop_range("AA", "Dealer"))
        self.assertFalse(judge_preflop_range("AA", "UTG+1")) # MPのエイリアスだがデータキーが違う

    def test_invalid_hand_input(self):
        """ハンド正規化が失敗した場合、Falseが返ることを確認"""
        self.assertFalse(judge_preflop_range("AXs", "UTG"))
        self.assertFalse(judge_preflop_range("T", "CO"))
        self.assertFalse(judge_preflop_range("AsKdx", "BTN"))
        self.assertFalse(judge_preflop_range("", "SB"))

    def test_case_insensitivity_and_normalization(self):
        """大文字小文字、ランク順、4文字表記が正規化されて正しく判定されるか"""
        # UTG (True)
        self.assertTrue(judge_preflop_range("aa", "UTG"))
        self.assertTrue(judge_preflop_range("aks", "UTG"))
        self.assertTrue(judge_preflop_range("aqo", "UTG"))
        self.assertTrue(judge_preflop_range("askd", "UTG")) # -> AKo
        self.assertTrue(judge_preflop_range("asks", "UTG")) # -> AKs
        self.assertTrue(judge_preflop_range("ak", "UTG"))   # -> AKo
        self.assertTrue(judge_preflop_range("KAs", "UTG")) # -> AKs
        self.assertTrue(judge_preflop_range("KA", "UTG"))  # -> AKo
        self.assertTrue(judge_preflop_range("QKo", "MP"))  # -> KQo
        self.assertTrue(judge_preflop_range("67s", "UTG")) # -> 76s

        # UTG (False, 正規化はされるがレンジにない)
        self.assertFalse(judge_preflop_range("ajo", "UTG"))
        self.assertFalse(judge_preflop_range("aj", "UTG"))  # -> AJo
        self.assertFalse(judge_preflop_range("jA", "UTG"))  # -> AJo
        self.assertFalse(judge_preflop_range("AdJc", "UTG")) # -> AJo
        self.assertFalse(judge_preflop_range("65s", "UTG"))
        self.assertFalse(judge_preflop_range("56s", "UTG"))

if __name__ == '__main__':
    # 実行方法:
    # 1. 上記の2つのコードブロックをそれぞれ
    #    'poker_range_analyzer.py' と 'test_poker_range_analyzer.py' として保存します。
    # 2. ターミナルで 'test_poker_range_analyzer.py' があるディレクトリに移動します。
    # 3. 'python -m unittest test_poker_range_analyzer.py' を実行します。
    unittest.main(argv=['first-arg-is-ignored'], exit=False)