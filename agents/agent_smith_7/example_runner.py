# example_runner.py
import json
from agents.llm_decision import build_input_for_llm, decide_action

USE_MOCK_LLM = True  # ADKがまだセットアップされていない場合はTrueにしてテスト

if USE_MOCK_LLM:
    # モック版：build_inputを作って、簡易ルールで返す
    def mock_decide_action(game_state):
        data = build_input_for_llm(game_state)
        stage = data["stage"]
        if stage == "preflop":
            if data.get("preflop_strength", 0) >= 0.85:
                return {"action": "raise", "amount": 3 * (game_state.get("call_amount", 0) or 10), "reasoning": "強いプリフロップハンドのため積極的にレイズ（モック）"}
            if data.get("preflop_strength", 0) >= 0.6:
                return {"action": "call", "amount": game_state.get("call_amount", 0), "reasoning": "ミドルハンドのためポジション次第でコール（モック）"}
            return {"action": "fold", "amount": 0, "reasoning": "弱いハンドのためフォールド（モック）"}
        else:
            ev = data.get("expected_value", -999)
            if ev > 100:
                return {"action": "raise", "amount": min(game_state.get("your_stack",9999), data["pot_size"] + 200), "reasoning": f"EV が高いため攻撃（EV={ev})"}
            if ev > 0:
                return {"action": "call", "amount": game_state.get("call_amount", 0), "reasoning": f"EV がわずかに正なので安全にコール（EV={ev})"}
            return {"action": "fold", "amount": 0, "reasoning": f"EV が負なのでフォールド（EV={ev})"}

    decision_fn = mock_decide_action
else:
    decision_fn = decide_action

# サンプルゲーム状態（ポストフロップ例）
game_state = {
    "stage": "flop",
    "hole_cards": ["Ah", "Kd"],
    "community_cards": ["Ad", "7c", "2h"],
    "pot_size": 600,
    "call_amount": 150,
    "seat_index": 3,
    "dealer_index": 0,
    "num_active_players": 5,
    "your_stack": 1500,
    "opponent_aggression": 0.6,
    "available_actions": ["fold", "call(150)", "raise(300-500)"]
}

decision = decision_fn(game_state)
print("LLM入力（整理済み）:")
print(json.dumps(build_input_for_llm(game_state), indent=2))
print("\n決定:")
print(json.dumps(decision, indent=2))
