# tools/postflop_hand_strength_tool.py
import random
from treys import Evaluator, Card, Deck

class PostflopHandStrengthTool:
    def __init__(self):
        self.evaluator = Evaluator()

    def _to_treys_cards(self, cards):
        # 入力例 'Ah', 'Kd' -> treys Card.new('Ah') works
        return [Card.new(c) for c in cards]

    def monte_carlo_win_rate(self, hole_cards, community_cards, num_opponents=1, trials=800):
        """
        Monte Carloで残りカードをランダムサンプリングして勝率を推定します。
        - hole_cards: ['Ah', 'Kd']
        - community_cards: ['Ad', '7c', '2h'] （0〜5枚）
        - num_opponents: 敵人数（あなた以外のアクティブプレイヤー数）
        - trials: シミュレーション回数（パフォーマンスと精度のトレードオフ）
        戻り値: win_rate（0〜1）、tie_rate（0〜1）
        """
        # 簡単な入力検証
        assert len(hole_cards) == 2
        assert 0 <= len(community_cards) <= 5

        wins = 0
        ties = 0
        losses = 0

        # prepare current used cards
        used = set(hole_cards + community_cards)

        for _ in range(trials):
            deck = Deck()
            # remove used cards from deck
            # Deck.draw() will give random cards; to remove specific, we rebuild deck
            remaining = [c for c in deck.cards if Card.int_to_str(c) not in used]
            random.shuffle(remaining)

            # draw missing community cards
            needed = 5 - len(community_cards)
            community_drawn = []
            idx = 0
            while needed > 0:
                card_int = remaining[idx]
                community_drawn.append(Card.int_to_str(card_int))
                idx += 1
                needed -= 1

            full_community = community_cards + community_drawn

            # draw opponents' hole cards
            opp_hands = []
            for _ in range(num_opponents):
                c1 = remaining[idx]; idx += 1
                c2 = remaining[idx]; idx += 1
                opp_hands.append([Card.int_to_str(c1), Card.int_to_str(c2)])

            # evaluate scores (lower is better in treys)
            our_score = self.evaluator.evaluate(
                [Card.new(c) for c in full_community],
                [Card.new(c) for c in hole_cards]
            )
            best_opp_score = None
            tied = False
            for opp in opp_hands:
                opp_score = self.evaluator.evaluate(
                    [Card.new(c) for c in full_community],
                    [Card.new(c) for c in opp]
                )
                if best_opp_score is None or opp_score < best_opp_score:
                    best_opp_score = opp_score

            if our_score < best_opp_score:
                wins += 1
            elif our_score == best_opp_score:
                ties += 1
            else:
                losses += 1

        win_rate = wins / trials
        tie_rate = ties / trials
        return round(win_rate, 4), round(tie_rate, 4)
