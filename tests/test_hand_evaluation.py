from math import comb


def test_flop_totals_and_keys():
    from agents.team3_agent.tools.hand_evaluation import hand_evaluation
    # フロップでの基本検証
    res = hand_evaluation(["A♠", "K♥"], ["2♣", "7♦", "9♠"])
	# 必須キー
    for k in [
    	"rank",
		"rank_value",
		"strength_score",
		"best_five_cards",
		"kickers",
		"stronger_hands",
		"tied_hands",
		"weaker_hands",
		"total_opponent_combinations",
	]:
        assert k in res
    # 合計件数（残り 47 枚から 2 枚）
    assert res["total_opponent_combinations"] == comb(52 - 2 - 3, 2)
    assert res["stronger_hands"] + res["tied_hands"] + res["weaker_hands"] == res[
		"total_opponent_combinations"
	]
	# スコア範囲
    assert 0.0 <= res["strength_score"] <= 1.0


def test_flop_known_straight_rank_value():
	from agents.team3_agent.tools.hand_evaluation import hand_evaluation
	# ボード Ah Kd Jc, ハンド Qs Th -> ストレート
	res = hand_evaluation(["Q♠", "T♥"], ["A♥", "K♦", "J♣"])
	# 合計件数（残り 47 枚から 2 枚）
	assert res["total_opponent_combinations"] == comb(52 - 2 - 3, 2)
	# 役値はストレート (=5)
	assert res["rank_value"] == 5


def test_turn_totals():
	from agents.team3_agent.tools.hand_evaluation import hand_evaluation
	res = hand_evaluation(["A♠", "A♥"], ["2♣", "7♦", "9♠", "K♣"])
	# 合計件数（残り 46 枚から 2 枚）
	assert res["total_opponent_combinations"] == comb(52 - 2 - 4, 2)
	assert res["stronger_hands"] + res["tied_hands"] + res["weaker_hands"] == res[
		"total_opponent_combinations"
	]


def test_river_royal_flush_rank_value():
	from agents.team3_agent.tools.hand_evaluation import hand_evaluation
	# ロイヤルフラッシュ（スペード）
	res = hand_evaluation(["A♠", "K♠"], ["Q♠", "J♠", "T♠", "2♦", "3♦"])
	# 合計件数（残り 45 枚から 2 枚）
	assert res["total_opponent_combinations"] == comb(52 - 2 - 5, 2)
	# 役値はロイヤルフラッシュ (=10)
	assert res["rank_value"] == 10
	# スコア上限近辺
	assert 0.9 <= res["strength_score"] <= 1.0


