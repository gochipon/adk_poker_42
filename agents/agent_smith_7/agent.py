from tools.preflop_ev_tool import PreflopEVTool

preflop_ev_tool = PreflopEVTool()

def decide_action(game_state):
    if game_state["stage"] == "preflop":
        ev = preflop_ev_tool.evaluate(
            game_state["hole_cards"],
            position=game_state.get("position","CO"),
            stack=game_state.get("your_stack",1000),
            call_amount=game_state.get("call_amount",10),
            num_active=game_state.get("num_active_players",5),
            opponent_aggression=game_state.get("opponent_aggression",0.5)
        )
        reasoning = f"プリフロップ期待値: {ev}"

        call_amt = game_state.get("call_amount",10)
        if ev >= 1.0:
            return {"action":"raise", "amount":3*call_amt, "reasoning":reasoning + " → 3倍レイズ"}
        elif ev >= 0.7:
            return {"action":"call", "amount":call_amt, "reasoning":reasoning + " → コール"}
        else:
            return {"action":"fold", "amount":0, "reasoning":reasoning + " → フォールド"}
