from itertools import combinations
from math import comb
from typing import Any, Dict, List, Optional, Set

from .hand_score import (
    Card,
    HandResult,
    SimpleHandEvaluator,
    Suit,
    _parse_cards,
    _score_from_rank_value,
)

def _build_full_deck() -> List[Card]:
    """Generate a standard 52-card deck."""
    return [Card(rank, suit) for suit in Suit for rank in range(2, 15)]


# ハンドレンジ判定関数群
def _is_premium_hand(card1: Card, card2: Card) -> bool:
    """
    プレミアムハンドかどうかを判定
    AA, KK, QQ, AK (suited/offsuit)
    """
    ranks = sorted([card1.rank, card2.rank], reverse=True)
    # AA, KK, QQ
    if ranks[0] == ranks[1] and ranks[0] >= 12:
        return True
    # AK
    if ranks == [14, 13]:
        return True
    return False


def _is_broadway_hand(card1: Card, card2: Card) -> bool:
    """
    ブロードウェイハンド（10以上のハイカード）かどうかを判定
    A-K, A-Q, A-J, A-10, K-Q, K-J, K-10, Q-J, Q-10, J-10
    """
    ranks = sorted([card1.rank, card2.rank], reverse=True)
    # 両方のカードが10以上で、ペアではない
    return ranks[0] >= 10 and ranks[1] >= 10 and ranks[0] != ranks[1]


def _is_pocket_pair(card1: Card, card2: Card) -> bool:
    """ポケットペアかどうかを判定"""
    return card1.rank == card2.rank


def _is_suited_connector(card1: Card, card2: Card) -> bool:
    """
    スートコネクター（同じスートで数値が連続）かどうかを判定
    例: 8♠7♠, J♥10♥
    """
    if card1.suit != card2.suit:
        return False
    rank_diff = abs(card1.rank - card2.rank)
    # 連続している、またはA-5のホイール
    return rank_diff == 1 or (rank_diff == 12 and min(card1.rank, card2.rank) == 2)


def _is_high_sum_hand(card1: Card, card2: Card, threshold: int = 20) -> bool:
    """
    カードの数値合計が指定値以上かどうかを判定
    デフォルトは20以上（例: A-7, K-8, Q-9, J-10など）
    """
    return card1.rank + card2.rank >= threshold


def _filter_hand_by_range(
    card1: Card, card2: Card, range_filters: Set[str]
) -> bool:
    """
    指定されたレンジフィルターに基づいてハンドを判定

    Args:
        card1, card2: 評価するカード2枚
        range_filters: 適用するフィルター名のセット
            - "premium": プレミアムハンド
            - "broadway": ブロードウェイハンド
            - "pocket_pair": ポケットペア
            - "suited_connector": スートコネクター
            - "high_sum": 合計20以上
            - "all": 全てのハンド（フィルターなし）

    Returns:
        フィルターに合致すればTrue
    """
    if not range_filters or "all" in range_filters:
        return True

    if "premium" in range_filters and _is_premium_hand(card1, card2):
        return True
    if "broadway" in range_filters and _is_broadway_hand(card1, card2):
        return True
    if "pocket_pair" in range_filters and _is_pocket_pair(card1, card2):
        return True
    if "suited_connector" in range_filters and _is_suited_connector(card1, card2):
        return True
    if "high_sum" in range_filters and _is_high_sum_hand(card1, card2):
        return True

    return False


def _remove_known_cards(deck: List[Card], known_cards: List[Card]) -> None:
    """Mutate deck by removing cards that are already visible."""
    for card in known_cards:
        try:
            deck.remove(card)
        except ValueError as exc:
            raise ValueError(f"Card {card} is not available in the deck") from exc


async def hand_rank_tool(
    your_cards: List[str],
    community: Optional[List[str]] = None,
    opponent_range: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    指定されたホールカードとコミュニティカードからハンド強度を評価し、
    同じボードを共有する相手のホールカードの組み合わせのうち、
    自分のハンドより強いものの総数を算出します。

    Args:
        your_cards: プレイヤーのホールカード（例: ["A♥", "K♠"]）
        community: 既に公開されているコミュニティカード（0-5枚）
        opponent_range: 相手のハンドレンジフィルター（未指定の場合は全てのハンドを評価）
            - "premium": プレミアムハンド（AA, KK, QQ, AK）
            - "broadway": ブロードウェイハンド（10以上の組み合わせ）
            - "pocket_pair": ポケットペア
            - "suited_connector": スートコネクター
            - "high_sum": カード合計20以上
            - "all": 全てのハンド（デフォルト）

    Returns:
        dict: {
            "hand": {...},  # 自分のハンド情報
            "stronger_hands": int,  # 相手のホールカード組み合わせのうち自分より強い総数
            "tied_hands": int,  # 引き分けになる組み合わせ数
            "weaker_hands": int,  # 自分より弱い組み合わせ数
            "total_opponent_combinations": int,  # 評価した相手ハンドの総数
            "filtered_combinations": int,  # レンジフィルター適用後の組み合わせ数
            "applied_filters": List[str],  # 適用されたフィルター
        }
    """
    community = community or []
    opponent_range = opponent_range or ["all"]

    hero_hole = _parse_cards(your_cards)
    board = _parse_cards(community)

    if len(hero_hole) != 2:
        raise ValueError("your_cards must contain exactly two cards")
    if len(board) > 5:
        raise ValueError("community cannot contain more than five cards")

    hero_result: HandResult = SimpleHandEvaluator.evaluate_hand(hero_hole, board)

    deck = _build_full_deck()
    _remove_known_cards(deck, hero_hole + board)

    remaining_cards = len(deck)
    total_opponent_combinations = comb(remaining_cards, 2) if remaining_cards >= 2 else 0

    # ハンドレンジフィルターをセットに変換
    range_filters = set(opponent_range)

    stronger = 0
    ties = 0
    filtered_count = 0

    for opponent_hole in combinations(deck, 2):
        # ハンドレンジフィルターを適用
        if not _filter_hand_by_range(opponent_hole[0], opponent_hole[1], range_filters):
            continue

        filtered_count += 1
        opponent_result = SimpleHandEvaluator.evaluate_hand(list(opponent_hole), board)
        if hero_result < opponent_result:
            stronger += 1
        elif hero_result == opponent_result:
            ties += 1

    weaker = filtered_count - stronger - ties

    hand_summary = {
        "rank": hero_result.rank.name,
        "rank_value": hero_result.rank.value,
        "strength_score": round(_score_from_rank_value(hero_result.rank.value), 4),
        "description": SimpleHandEvaluator.get_hand_strength_description(hero_result),
        "best_five_cards": [str(card) for card in hero_result.cards],
        "kickers": hero_result.kickers,
        "normalized_input": {
            "your_cards": [str(card) for card in hero_hole],
            "community_cards": [str(card) for card in board],
        },
    }

    return {
        "hand": hand_summary,
        "stronger_hands": stronger,
        "tied_hands": ties,
        "weaker_hands": weaker,
        "total_opponent_combinations": total_opponent_combinations,
        "filtered_combinations": filtered_count,
        "applied_filters": list(range_filters),
    }
