# tools/preflop_ev_tool.py
class PreflopEVTool:
    """
    プリフロップの期待値計算ツール
    """
    base_strength_table = {
        ("A","A"):0.95, ("K","K"):0.9, ("Q","Q"):0.85, ("J","J"):0.8,
        ("T","T"):0.75, ("9","9"):0.7, ("8","8"):0.65,
        ("A","K"):0.82, ("A","Q"):0.8, ("K","Q"):0.78, ("J","T"):0.72,
    }

    position_factors = {"UTG":0.8, "MP":0.9, "CO":1.0, "BTN":1.1, "SB":0.95}

    def evaluate(self, hole_cards, position="CO", stack=1000, call_amount=10, num_active=5, opponent_aggression=0.5):
        ranks = tuple(sorted([c[0] for c in hole_cards], reverse=True))
        base = self.base_strength_table.get(ranks, 0.5)

        pos_factor = self.position_factors.get(position,1.0)
        stack_factor = min(stack / (call_amount * 20), 2.0)
        opponent_factor = 1.0 - (opponent_aggression * 0.2)

        ev = base * pos_factor * stack_factor * opponent_factor
        return round(ev,2)
