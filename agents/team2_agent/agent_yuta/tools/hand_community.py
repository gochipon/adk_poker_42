"""
Hand Community Tool - ハンドの貢献度を評価するツール

自分のハンドカードがコミュニティカードと組み合わせた時にどれだけ強さに貢献しているかを
0-10のスコアで評価します。

スコアの意味:
- 10: 自分のハンドが最大限に貢献している（例: ポケットペアでセット完成）
- 5-9: 中程度の貢献（例: ペアができた、フラッシュドロー）
- 1-4: 小さな貢献（例: ハイカードが少し改善）
- 0: 全く貢献していない（コミュニティカードのみで役ができている）
"""

from typing import List, Optional, Dict, Any
from .hand_score import (
    Card,
    HandResult,
    SimpleHandEvaluator,
    _parse_cards,
)


def _calculate_contribution_score(
    hand_with_hole: HandResult,
    hand_community_only: Optional[HandResult],
    community_count: int,
) -> float:
    """
    ハンドの貢献度を0-10のスケールで計算

    Args:
        hand_with_hole: ホールカード+コミュニティカードのハンド評価
        hand_community_only: コミュニティカードのみのハンド評価（5枚未満の場合はNone）
        community_count: コミュニティカードの枚数

    Returns:
        0-10のスコア（float）
    """
    # コミュニティカードが5枚未満の場合
    # ホールカードがないと役が作れないため、ハンドの強さに応じてスコアを返す
    if community_count < 5 or hand_community_only is None:
        # ハンドの強さに応じてスコアを調整
        # 強い役ほど高いスコア
        base_score = hand_with_hole.rank.value  # 1-10
        return float(base_score)

    # コミュニティカードが5枚の場合の貢献度計算
    rank_diff = hand_with_hole.rank.value - hand_community_only.rank.value

    # ランクの差が大きいほど貢献度が高い
    if rank_diff > 0:
        # 役が改善された場合
        # スリーカード以上なら高スコア
        if hand_with_hole.rank.value >= 4:  # THREE_OF_A_KIND以上
            score = min(10.0, 6.0 + rank_diff * 2.0)
        else:
            # ワンペア、ツーペアの場合は中程度
            score = min(10.0, 5.0 + rank_diff * 1.5)
        return score
    elif rank_diff == 0:
        # 同じ役の場合、キッカーで比較
        # キッカーが改善されていれば中程度のスコア
        kicker_improvement = False
        for my_kicker, board_kicker in zip(
            hand_with_hole.kickers, hand_community_only.kickers
        ):
            if my_kicker > board_kicker:
                kicker_improvement = True
                break

        if kicker_improvement:
            # キッカーの改善があれば4-6点
            return 5.0
        else:
            # 改善がなければ低スコア
            return 2.0
    else:
        # コミュニティカードのみの方が強い
        # ボードの方が強いが、自分のハンドの強さも考慮
        # ハイカードなら0点、役があれば少しスコアを与える
        if hand_with_hole.rank.value <= 1:  # HIGH_CARD
            return 0.0
        else:
            return 1.0


async def hand_community_tool(
    your_cards: List[str],
    community_cards: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    自分のハンドがコミュニティカードとの組み合わせでどれだけ強いかを評価するツール

    このツールは以下を計算します:
    1. ホールカード + コミュニティカードの最強ハンド
    2. コミュニティカードのみの最強ハンド（5枚の場合）
    3. 両者の差分から、ホールカードの貢献度を0-10でスコア化

    スコアの解釈:
    - 10点満点: ホールカードが最大限に役立っている（強い役を作っている）
    - 5-9点: 中程度の貢献（役の改善やキッカーの向上）
    - 1-4点: わずかな貢献（ハイカードの改善程度）
    - 0点: 全く貢献していない（ボードだけで完成している役）

    Args:
        your_cards: プレイヤーのホールカード（2枚）
                   例: ["A♥", "K♠"] または ["As", "Kh"]
        community_cards: コミュニティカード（0-5枚）
                        例: ["Q♥", "J♦", "10♣", "9♠", "8♥"]

    Returns:
        dict: {
            "contribution_score": float,  # 0-10の貢献度スコア
            "hand_with_hole": dict,       # ホールカード込みのハンド情報
            "hand_community_only": dict,  # コミュニティのみのハンド情報（5枚の場合）
            "evaluation": str,            # スコアの評価コメント
        }

    Examples:
        >>> # ポケットペアでセット完成
        >>> await hand_community_tool(["A♥", "A♠"], ["A♦", "K♥", "Q♣", "J♠", "10♦"])
        {"contribution_score": 10.0, "evaluation": "excellent", ...}

        >>> # ボードでストレート完成（ホールカードは不要）
        >>> await hand_community_tool(["2♥", "3♠"], ["A♦", "K♥", "Q♣", "J♠", "10♦"])
        {"contribution_score": 2.0, "evaluation": "minimal", ...}
    """
    community_cards = community_cards or []

    # カードのパース
    hole = _parse_cards(your_cards)
    board = _parse_cards(community_cards)

    # バリデーション
    if len(hole) != 2:
        raise ValueError("your_cards must contain exactly 2 cards")
    if len(board) > 5:
        raise ValueError("community_cards cannot contain more than 5 cards")

    # 1. ホールカード + コミュニティカードで評価
    hand_with_hole = SimpleHandEvaluator.evaluate_hand(hole, board)

    # 2. コミュニティカードのみで評価（5枚の場合のみ）
    hand_community_only = None
    if len(board) == 5:
        hand_community_only = SimpleHandEvaluator.evaluate_hand([], board)

    # 3. 貢献度スコアを計算
    contribution_score = _calculate_contribution_score(
        hand_with_hole, hand_community_only, len(board)
    )

    # 4. 評価コメント生成
    if contribution_score >= 9.0:
        evaluation = "excellent"  # 素晴らしい！ハンドが非常に強い
        comment = "あなたのホールカードはこのボードで最大限に活躍しています！"
    elif contribution_score >= 7.0:
        evaluation = "strong"  # 強い貢献
        comment = "ホールカードが役の強化に大きく貢献しています。"
    elif contribution_score >= 5.0:
        evaluation = "moderate"  # 中程度
        comment = "ホールカードは中程度の貢献をしています。"
    elif contribution_score >= 3.0:
        evaluation = "weak"  # 弱い貢献
        comment = "ホールカードの貢献は限定的です。"
    else:
        evaluation = "minimal"  # ほぼ貢献なし
        comment = "ホールカードはほとんど役に立っていません。"

    # 結果の構築
    result = {
        "contribution_score": round(contribution_score, 2),
        "evaluation": evaluation,
        "comment": comment,
        "hand_with_hole": {
            "rank": hand_with_hole.rank.name,
            "rank_value": hand_with_hole.rank.value,
            "description": SimpleHandEvaluator.get_hand_strength_description(hand_with_hole),
            "best_five_cards": [str(card) for card in hand_with_hole.cards],
            "kickers": hand_with_hole.kickers,
        },
        "normalized_input": {
            "your_cards": [str(card) for card in hole],
            "community_cards": [str(card) for card in board],
        },
    }

    # コミュニティカードのみの評価結果も追加（5枚の場合）
    if hand_community_only:
        result["hand_community_only"] = {
            "rank": hand_community_only.rank.name,
            "rank_value": hand_community_only.rank.value,
            "description": SimpleHandEvaluator.get_hand_strength_description(hand_community_only),
            "best_five_cards": [str(card) for card in hand_community_only.cards],
            "kickers": hand_community_only.kickers,
        }
    else:
        result["hand_community_only"] = None

    return result
