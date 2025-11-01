from typing import Optional, List, Tuple


def _score_from_rank_value(rank_value: int) -> float:
	"""
	HandRank(10=Royal Flush .. 1=High Card) を 0..1 のスコアに正規化。
	強いほど 1.0 に近づく単調増加スコア。
	"""
	max_v = 10.0
	min_v = 1.0
	return (rank_value - min_v) / (max_v - min_v)


def _to_treys_str(card_str: str) -> str:
	"""
	"A♠" / "Ah" / "AS" / "10d" / "Td" などを treys 形式 (e.g. "As") に正規化。
	"""
	s = card_str.strip()
	# ランク抽出
	rank_map = {
		"A": "A",
		"K": "K",
		"Q": "Q",
		"J": "J",
		"T": "T",
		"10": "T",
		"9": "9",
		"8": "8",
		"7": "7",
		"6": "6",
		"5": "5",
		"4": "4",
		"3": "3",
		"2": "2",
	}
	# スート抽出
	suit_map = {
		"♠": "s",
		"S": "s",
		"s": "s",
		"♣": "c",
		"C": "c",
		"c": "c",
		"♦": "d",
		"D": "d",
		"d": "d",
		"♥": "h",
		"❤": "h",
		"H": "h",
		"h": "h",
	}

	# 2文字 or 3文字想定（10を含む場合あり）
	# まずランク候補を長い順に試す
	for rk in ("10", "A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"):
		if s.upper().startswith(rk):
			r = rank_map[rk]
			suit_part = s[len(rk):]
			if not suit_part:
				raise ValueError(f"Invalid card: {card_str}")
			# スートは末尾1文字を優先（絵文字のときはそのまま）
			ch = suit_part[-1]
			if ch not in suit_map:
				# もしかすると絵文字 1 文字のみが入っているケース
				ch = suit_part[0]
			if ch not in suit_map:
				raise ValueError(f"Invalid suit in card: {card_str}")
			return f"{r}{suit_map[ch]}"

	# 末尾側から判定（例: A♠ のように 1+絵文字）
	if len(s) >= 2:
		r = s[0].upper()
		sym = s[1]
		if r in rank_map and sym in suit_map:
			return f"{rank_map[r]}{suit_map[sym]}"

	raise ValueError(f"Unrecognized card format: {card_str}")


def _make_remaining_deck(exclude_treys: List[int]) -> List[int]:
	from treys import Card
	all_ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
	all_suits = ["s", "h", "d", "c"]
	deck: List[int] = []
	for r in all_ranks:
		for su in all_suits:
			c = Card.new(f"{r}{su}")
			deck.append(c)
	return [c for c in deck if c not in set(exclude_treys)]


def hand_evaluation(your_cards: list[str], community_cards: Optional[list[str]] = None,) -> dict[str, any]:
	"""
	指定されたカードとコミュニティカードからハンド強度を評価。
	同じボードを共有する全ての相手 2 枚組み合わせを列挙し、
	自分のハンドより 強い/同等/弱い 組み合わせ数を算出します。

	Args:
		your_cards: プレイヤーのカード（例: ["A♥", "K♠"]）
		community_cards: 既に公開されているコミュニティカード（0-5枚）

	Returns:
		dict: {
			"rank": str,  # 自分の役（日本語表現）
			"rank_value": int,  # 自分の役のランク値（10..1）
			"strength_score": float,  # 0..1 正規化スコア（高いほど強い）
			"best_five_cards": list[str],  # 最強 5 枚の表記
			"kickers": list[int],
			"stronger_hands": int,
			"tied_hands": int,
			"weaker_hands": int,
			"total_opponent_combinations": int,
		}
	"""
	from itertools import combinations
	from treys import Card as TCard, Evaluator as TEvaluator
	from .hand_evaluator_utils import HandEvaluator as LocalEvaluator, HandResult as LocalHandResult, HandRank as LocalHandRank, Card as LocalCard, Suit as LocalSuit

	community_cards = community_cards or []

	if len(community_cards) < 3:
		return {
			"error": "プリフロップではhand_evaluationは使用できません",
			"message": "コミュニティカードが3枚以上必要です（flop以降で使用してください）"
		}

	# 入力を treys 形式へ
	try:
		treys_hero = [TCard.new(_to_treys_str(c)) for c in your_cards]
		treys_board = [TCard.new(_to_treys_str(c)) for c in community_cards]
	except Exception as e:
		raise ValueError(f"Card parse error: {e}")

	# treys で自身のスコア算出（小さいほど強い）
	eval_t = TEvaluator()
	hero_score = eval_t.evaluate(treys_hero, treys_board)

	# 相手全組み合わせ列挙（自分とボードを除外）
	remaining = _make_remaining_deck(exclude_treys=treys_hero + treys_board)
	stronger = 0
	ties = 0
	weaker = 0
	for opp_hole in combinations(remaining, 2):
		opp_score = eval_t.evaluate(list(opp_hole), treys_board)
		if opp_score < hero_score:
			stronger += 1
		elif opp_score == hero_score:
			ties += 1
		else:
			weaker += 1

	# 最強 5 枚とキッカーはローカル Evaluator を利用（表示用の詳細を取得）
	def _parse_local_card(s: str) -> LocalCard:
		text = s.strip()
		# ランク
		if text.upper().startswith("10"):
			rank = 10
			suit_part = text[2:]
		else:
			r_map = {"A":14, "K":13, "Q":12, "J":11, "T":10,
					  "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
			ch = text[0].upper()
			if ch not in r_map:
				raise ValueError(f"Invalid rank in card: {s}")
			rank = r_map[ch]
			suit_part = text[1:]
		# スート
		s_map = {
			"♠": LocalSuit.SPADES,
			"♣": LocalSuit.CLUBS,
			"♦": LocalSuit.DIAMONDS,
			"♥": LocalSuit.HEARTS,
			"❤": LocalSuit.HEARTS,
			"S": LocalSuit.SPADES,
			"C": LocalSuit.CLUBS,
			"D": LocalSuit.DIAMONDS,
			"H": LocalSuit.HEARTS,
			"s": LocalSuit.SPADES,
			"c": LocalSuit.CLUBS,
			"d": LocalSuit.DIAMONDS,
			"h": LocalSuit.HEARTS,
		}
		if not suit_part:
			raise ValueError(f"Invalid suit in card: {s}")
		sym = suit_part[-1]
		if sym not in s_map:
			# 先頭側で記号が来るケースにも対応（例: A♠）
			sym = suit_part[0]
		if sym not in s_map:
			raise ValueError(f"Invalid suit in card: {s}")
		return LocalCard(rank, s_map[sym])

	try:
		local_hole = [_parse_local_card(c) for c in your_cards]
		local_board = [_parse_local_card(c) for c in community_cards]
		local_result: LocalHandResult = LocalEvaluator.evaluate_hand(local_hole, local_board)
	except Exception:
		# フォールバック：最強 5 枚やキッカーが取得できない場合は空にする
		local_result = None

	if local_result:
		rank_jp = local_result.description if local_result.description else ""
		rank_value = local_result.rank.value
		best_five_cards = [str(c) for c in local_result.cards]
		kickers = list(local_result.kickers)
	else:
		# treys のクラス名を英語で返すフォールバック
		rank_class = eval_t.get_rank_class(hero_score)
		rank_jp = TEvaluator.class_to_string(rank_class)
		# rank_value は大きいほど強いように見せるため、役クラスを 1..9 から 1..10 にスケール
		rank_value = int(rank_class)
		best_five_cards = []
		kickers = []

	result = {
		"rank": rank_jp,
		"rank_value": rank_value,
		"strength_score": round(_score_from_rank_value(rank_value), 4),
		"best_five_cards": best_five_cards,
		"kickers": kickers,
		"stronger_hands": stronger,
		"tied_hands": ties,
		"weaker_hands": weaker,
		"total_opponent_combinations": stronger + ties + weaker,
	}
	return result
