# tools/postflop_ev_tool.py
import random

class PostflopEVTool:
    """
    フロップ・ターン・リバーの期待値計算
    Monte Carlo簡易版
    """
    def monte_carlo_win_rate(self, hole_cards, community_cards, num_opponents=1, trials=500):
        win, tie = 0, 0
        all_cards = [r+s for r in "23456789TJQKA" for s in "cdhs"]
        used_cards = set(hole_cards + community_cards)
        deck = [c for c in all_cards if c not in used_cards]

        for _ in range(trials):
            random.shuffle(deck)
            remaining_board = deck[:5-len(community_cards)]
            full_board = community_cards + remaining_board
            my_score = self.evaluate_hand(hole_cards, full_board)

            opponent_scores = []
            for _ in range(num_opponents):
                opp_hole = deck[5:7]
                opp_score = self.evaluate_hand(opp_hole, full_board)
                opponent_scores.append(opp_score)

            max_opp = max(opponent_scores)
            if my_score > max_opp:
                win += 1
            elif my_score == max_opp:
                tie += 1

        win_rate = win / trials
        tie_rate = tie / trials
        return round(win_rate,3), round(tie_rate,3)

    def expected_value(self, win_rate, pot, call_amount):
        return round(win_rate * pot - (1-win_rate)*call_amount,2)

    def evaluate_hand(self, hole_cards, board):
        ranks = [c[0] for c in hole_cards + board]
        score = 0
        for r in set(ranks):
            cnt = ranks.count(r)
            if cnt==2: score+=2
            elif cnt==3: score+=5
            elif cnt>=4: score+=10
        score += random.uniform(0,1)
        return score
