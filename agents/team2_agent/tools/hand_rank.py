from itertools import combinations
from math import comb
from typing import Any, Dict, List, Optional

from .hand_score import (
    Card,
    HandResult,
    SimpleHandEvaluator,
    Suit,
    _parse_cards,
    _score_from_rank_value,
)
from .preflop_scorer import evaluate_preflop_hand, filter_hand_by_range

def _build_full_deck() -> List[Card]:
    """Generate a standard 52-card deck."""
    return [Card(rank, suit) for suit in Suit for rank in range(2, 15)]

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
            "preflop_rank": {  # プリフロップレンジ評価
                "combo": str,
                "score": float,
                "tier": str,
                "category": str,
            },
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
    preflop_rank = evaluate_preflop_hand(hero_hole)

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
        if not filter_hand_by_range(opponent_hole[0], opponent_hole[1], range_filters):
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
        "preflop_rank": preflop_rank,
        "stronger_hands": stronger,
        "tied_hands": ties,
        "weaker_hands": weaker,
        "total_opponent_combinations": total_opponent_combinations,
        "filtered_combinations": filtered_count,
        "applied_filters": list(range_filters),
    }
