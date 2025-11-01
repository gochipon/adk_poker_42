# tools/postflop_ev_tool.py
import random
from treys import Card, Evaluator

class PostflopEVTool:
    """
    フロップ・ターン・リバーの期待値計算
    Monte Carlo簡易版 (treysライブラリ使用)
    """
    def __init__(self):
        self.evaluator = Evaluator()

    def string_to_treys_card(self, card_str):
        """ "As" や "Td" のような文字列を treys の Card オブジェクトに変換 """
        return Card.new(card_str)

    def evaluate_hand(self, hole_cards_str, board_cards_str):
        """
        7枚のカードから役のスコアを計算する。
        treysライブラリでは「スコアが小さいほど強い」
        """
        # 文字列のリストをCardオブジェクトのリストに変換
        hand = [self.string_to_treys_card(c) for c in hole_cards_str]
        board = [self.string_to_treys_card(c) for c in board_cards_str]
        
        # 役を評価
        return self.evaluator.evaluate(board, hand)

    def monte_carlo_win_rate(self, hole_cards, community_cards, num_opponents=1, trials=500):
        win, tie = 0, 0
        
        # treysが認識できる全カードの文字列リスト ("As", "Kc", ...)
        all_cards_str = [r+s for r in "23456789TJQKA" for s in "cdhs"]
        
        used_cards_set = set(hole_cards + community_cards)
        deck_str = [c for c in all_cards_str if c not in used_cards_set]

        for _ in range(trials):
            random.shuffle(deck_str)
            
            # ボードの残り
            remaining_board_count = 5 - len(community_cards)
            remaining_board_str = deck_str[:remaining_board_count]
            full_board_str = community_cards + remaining_board_str
            
            # 自分のスコア (スコアが低いほど強い)
            my_score = self.evaluate_hand(hole_cards, full_board_str)

            opponent_scores = []
            
            # デッキから相手のカードを配る
            opp_deck_start = remaining_board_count
            
            for i in range(num_opponents):
                opp_hole_start = opp_deck_start + (i * 2)
                opp_hole_str = deck_str[opp_hole_start : opp_hole_start + 2]
                
                opp_score = self.evaluate_hand(opp_hole_str, full_board_str)
                opponent_scores.append(opp_score)

            if not opponent_scores: # 相手がいない場合
                win = 1
                break

            min_opp_score = min(opponent_scores)
            
            # treys はスコアが「低い」ほど強い
            if my_score < min_opp_score:
                win += 1
            elif my_score == min_opp_score:
                # 引き分けの考慮 (厳密にはタイの相手の数で割るべきだが簡易的に)
                tie_opponents = opponent_scores.count(my_score)
                tie += (1 / (tie_opponents + 1)) # 自分 + タイの相手

        win_rate = win / trials
        # タイを勝率に按分（簡易計算）
        tie_as_win_rate = (tie / trials) * 0.5 
        
        return round(win_rate + tie_as_win_rate, 3), round(tie_as_win_rate, 3) # (win_rate, tie_rate)

    def expected_value(self, win_rate, pot, call_amount):
        # postflop_ev_tool.py の元の計算式
        return round(win_rate * pot - (1-win_rate)*call_amount, 2)