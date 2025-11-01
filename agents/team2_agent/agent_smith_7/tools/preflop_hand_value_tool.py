# tools/preflop_hand_value_tool.py
class PreflopHandValueTool:
    def __init__(self):
        # 簡易プリフロップ強度テーブル（代表例）
        # 拡張して独自の確率表を入れてください
        self.hand_strengths = {
            "AA": 1.00, "KK": 0.97, "QQ": 0.95, "JJ": 0.92, "TT": 0.89,
            "AKs": 0.88, "AQs": 0.86, "AJs": 0.84, "KQs": 0.82,
            "AK": 0.85, "AQ": 0.82, "AJ": 0.79, "KQ": 0.77,
            # ペア下位（例）
            "99": 0.74, "88": 0.71, "77": 0.68, "66": 0.65, "55": 0.62,
        }

    def canonical_form(self, cards):
        # cards: ['Ah', 'Kd'] or ['10h', 'Kd']
        ranks = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7,
                 '8':8, '9':9, 'T':10, '10':10, 'J':11, 'Q':12, 'K':13, 'A':14}
        c1, c2 = cards

        # Handle both '10' and 'T' formats
        if c1.startswith('10'):
            r1, s1 = 'T', c1[2]
        else:
            r1, s1 = c1[0], c1[1]

        if c2.startswith('10'):
            r2, s2 = 'T', c2[2]
        else:
            r2, s2 = c2[0], c2[1]

        suited = 's' if s1 == s2 else ''
        # 降順に並べる（例: AKs, not KAs）
        if ranks[r1] < ranks[r2]:
            r1, r2 = r2, r1
        return f"{r1}{r2}{suited}"

    def evaluate(self, cards):
        key = self.canonical_form(cards)
        return round(self.hand_strengths.get(key, 0.5), 3)
