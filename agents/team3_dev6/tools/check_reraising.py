from typing import Any, Dict, List

def check_reraising(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    リレイズ（再レイズ）が発生しているかを確認するツール。

    Args:
        game_state (dict): ゲーム状態のJSONデータ。
            例)
            {
                "your_id": 1,
                "phase": "preflop",
                "your_cards": ["7♣", "10♣"],
                "community": [],
                "your_chips": 2000,
                "your_bet_this_round": 0,
                "your_total_bet_this_hand": 0,
                "pot": 30,
                "to_call": 20,
                "dealer_button": 3,
                "current_turn": 1,
                "players": [
                    {"id": 0, "chips": 1980, "bet": 20, "status": "active"},
                    {"id": 2, "chips": 2000, "bet": 0, "status": "active"},
                    {"id": 3, "chips": 2000, "bet": 0, "status": "active"},
                    {"id": 4, "chips": 1990, "bet": 10, "status": "active"}
                ],
                "actions": ["fold", "call (20)", "raise (min 40)", "all-in (2000)"],
                "history": [
                    "Player 4 posted small blind 10",
                    "Player 0 posted big blind 20",
                    "Player 2 raised to 40",
                    "Player 3 reraised to 100"
                ]
            }

    Returns:
        dict: リレイズ確認結果
        {
            "is_reraising": bool (リレイズが発生しているか),
            "reraising_count": int (リレイズの回数),
            "reraising_players": list[dict] (リレイズを行ったプレイヤーの情報),
            "betting_sequence": list[dict] (ベッティングシーケンスの解析),
            "interpretation": str (状況の解釈と意味),
            "recommendation": str (推奨される対応)
        }
    """
    history = game_state.get("history", [])
    players = game_state.get("players", [])
    your_id = game_state.get("your_id", -1)
    your_bet_this_round = game_state.get("your_bet_this_round", 0)
    to_call = game_state.get("to_call", 0)
    phase = game_state.get("phase", "preflop")

    result = {
        "is_reraising": False,
        "reraising_count": 0,
        "reraising_players": [],
        "betting_sequence": [],
        "interpretation": "",
        "recommendation": ""
    }

    # ベッティングシーケンスを解析
    betting_actions = []
    initial_bet = 0  # 最初のベット額（ブラインド以外）

    # ブラインド情報を取得
    small_blind = 0
    big_blind = 0

    for action in history:
        action_lower = action.lower()
        if "small blind" in action_lower:
            # "Player 4 posted small blind 10" のような形式から抽出
            parts = action.split()
            for i, part in enumerate(parts):
                if part.isdigit():
                    small_blind = int(part)
                    break
        elif "big blind" in action_lower:
            parts = action.split()
            for i, part in enumerate(parts):
                if part.isdigit():
                    big_blind = int(part)
                    break
        elif "raised" in action_lower or "reraised" in action_lower:
            # "Player 2 raised to 40" や "Player 3 reraised to 100" を解析
            parts = action.split()
            player_id = None
            bet_amount = None
            is_reraising = "reraised" in action_lower

            # プレイヤーIDを抽出
            for part in parts:
                if part.startswith("Player") and len(parts) > parts.index(part) + 1:
                    try:
                        player_id = int(parts[parts.index(part) + 1])
                    except (ValueError, IndexError):
                        pass
                # ベット額を抽出 ("to 40" や "100" のような形式)
                if part == "to" and len(parts) > parts.index(part) + 1:
                    try:
                        bet_amount = int(parts[parts.index(part) + 1])
                    except (ValueError, IndexError):
                        pass
                elif part.isdigit() and "Player" not in action:
                    # "to"がない場合も数字があれば抽出
                    if bet_amount is None:
                        try:
                            bet_amount = int(part)
                        except ValueError:
                            pass

            if player_id is not None and bet_amount is not None:
                betting_actions.append({
                    "player_id": player_id,
                    "action_type": "reraise" if is_reraising else "raise",
                    "amount": bet_amount,
                    "raw_action": action
                })

                if is_reraising:
                    result["reraising_count"] += 1
                    # プレイヤー情報を取得
                    player_info = next((p for p in players if p.get("id") == player_id), None)
                    if player_info:
                        result["reraising_players"].append({
                            "id": player_id,
                            "chips": player_info.get("chips", 0),
                            "bet": player_info.get("bet", 0),
                            "status": player_info.get("status", "unknown")
                        })
        elif "called" in action_lower:
            # コールも記録（文脈を理解するため）
            parts = action.split()
            player_id = None
            for part in parts:
                if part.startswith("Player") and len(parts) > parts.index(part) + 1:
                    try:
                        player_id = int(parts[parts.index(part) + 1])
                    except (ValueError, IndexError):
                        pass

            if player_id is not None:
                betting_actions.append({
                    "player_id": player_id,
                    "action_type": "call",
                    "amount": None,  # コール額は履歴から直接取得できない場合がある
                    "raw_action": action
                })

    result["betting_sequence"] = betting_actions
    result["is_reraising"] = result["reraising_count"] > 0

    # 解釈と推奨事項を生成
    if result["is_reraising"]:
        result["interpretation"] = (
            f"リレイズが{result['reraising_count']}回発生しています。"
            f"これは通常、非常に強いハンドを示唆します。"
            f"リレイズしたプレイヤー: {[p['id'] for p in result['reraising_players']]}"
        )

        # リレイズの強さを評価
        if result["reraising_count"] >= 2:
            result["recommendation"] = (
                "複数回のリレイズが発生しているため、非常に強いハンドが対面している可能性が高い。"
                "ウィークハンドやミドルレンジの手ではフォールドを強く推奨。"
                "非常に強いハンド（トップペア以上、ストロングドロー）のみコール/レイズを検討。"
            )
        elif result["reraising_count"] == 1:
            result["recommendation"] = (
                "1回のリレイズが発生。ストロングハンドを示唆していますが、"
                "自分のハンドの強さとポットオッズを慎重に評価してください。"
                f"コールに必要な額: {to_call}チップ。"
                "ミドルレンジ以下の手ではフォールドを検討。"
            )
    else:
        # リレイズがないが、レイズはあるか
        raises = [a for a in betting_actions if a["action_type"] == "raise"]
        if raises:
            result["interpretation"] = (
                f"レイズは{len(raises)}回発生していますが、リレイズはありません。"
                "通常のレイズレンジの可能性があります。"
            )
            result["recommendation"] = (
                "リレイズがないため、レイズプレイヤーは標準的なレンジでプレイしている可能性が高い。"
                "自分のハンドの強さとポジションを考慮して判断してください。"
            )
        else:
            # レイズもリレイズもない（ブラインドのみ、または全員コール/チェック）
            result["interpretation"] = (
                "レイズやリレイズは発生していません。"
                "全員がコールまたはチェックしている状況です。"
            )
            result["recommendation"] = (
                "全体的にパッシブなアクションが多いため、"
                "タイトな状況または弱いハンドのプレイヤーが多い可能性があります。"
                "自分のハンドが強ければ積極的にベット/レイズを検討できます。"
            )

    # フェーズ別の補足情報
    if phase == "preflop":
        result["interpretation"] += " プレフロップでのリレイズは通常、プレミアムハンド（AA, KK, QQ, AK等）を示唆します。"
    elif phase in ["flop", "turn", "river"]:
        result["interpretation"] += f" {phase.upper()}でのリレイズは強いハンドまたは強いドローを示唆します。"

    return result

