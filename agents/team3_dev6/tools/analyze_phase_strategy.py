from typing import Any, Dict

def analyze_phase_strategy(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    現在のフェーズに基づいて、そのフェーズで取るべき戦略を分析するツール。

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
                "history": ["Player 4 posted small blind 10", "Player 0 posted big blind 20"]
            }

    Returns:
        dict: フェーズ別戦略分析結果
        {
            "phase": str (現在のフェーズ),
            "strategy": str (フェーズ別の一般的な戦略方針),
            "considerations": list[str] (このフェーズで考慮すべき要素のリスト),
            "recommended_approach": str (推奨されるアプローチ),
            "betting_tendency": str (ベッティングの傾向: "tight", "moderate", "aggressive", "very_aggressive")
        }
    """
    phase = game_state.get("phase", "preflop").lower()
    your_cards = game_state.get("your_cards", [])
    community = game_state.get("community", [])
    pot = game_state.get("pot", 0)
    to_call = game_state.get("to_call", 0)
    your_chips = game_state.get("your_chips", 0)
    players = game_state.get("players", [])
    active_players = [p for p in players if p.get("status") == "active"]
    num_active_players = len(active_players)

    result = {
        "phase": phase,
        "strategy": "",
        "considerations": [],
        "recommended_approach": "",
        "betting_tendency": "moderate"
    }

    if phase == "preflop":
        result["strategy"] = "プレフロップでは手札の強さとポジションが重要。タイトなレンジでプレイし、ポジションを活用する。"
        result["considerations"] = [
            "手札の強さ（ペア、高カード、スーツ）",
            "テーブルポジション（早いポジションではタイト、後ろのポジションではレンジを広げられる）",
            "アクティブプレイヤー数（多ければタイトに、少なければ積極的に）",
            "ブラインドとの関係（BBならコールしやすい状況も）",
            "レイズサイズとレイズ頻度"
        ]
        result["recommended_approach"] = (
            "強い手（プレミアムハンド、ポケットペア高）では積極的にレイズ。"
            "ミドルレンジの手ではポジションを考慮してコールまたはフォールド。"
            f"現在{num_active_players}人のアクティブプレイヤーがいるため、"
            f"{'タイトな' if num_active_players >= 4 else 'やや広めの'}レンジでプレイすることを推奨。"
        )
        result["betting_tendency"] = "tight" if num_active_players >= 4 else "moderate"

    elif phase == "flop":
        result["strategy"] = "フロップではボードテクスチャーとハンドの強さの関係を評価。ポットコントロールとバリューベットを意識。"
        result["considerations"] = [
            "フロップとの相性（ペア、ストレートドロー、フラッシュドロー、トップペア等）",
            "ボードテクスチャー（ウェット/ドライ、ペア、ストレート/フラッシュの可能性）",
            "ベット履歴（誰がベット/レイズしたか）",
            "アウツの数（ドローがある場合）",
            "ポットオッズとインプライドオッズ"
        ]
        result["recommended_approach"] = (
            "強い手やドローがある場合は積極的にベット/レイズ。"
            "ミドルペア以下は状況に応じてチェック/コールまたはフォールド。"
            f"コミュニティカード: {', '.join(community) if community else 'なし'}。"
            "ボードがウェット（ストレート/フラッシュの可能性がある）場合は慎重に。"
        )
        result["betting_tendency"] = "moderate"

    elif phase == "turn":
        result["strategy"] = "ターンではハンドの価値がより明確になる。ストロングハンドはバリューベット、ドローは慎重に。"
        result["considerations"] = [
            "ターンカードが手の強さに与える影響",
            "ドローの完了/未完了（ストレート、フラッシュ）",
            "ポットサイズとベットサイズのバランス",
            "相手のレンジとアクション（アグレッシブさ）",
            "リバーでのポジション"
        ]
        result["recommended_approach"] = (
            "完成した強い手（ツーペア以上）では積極的にバリューベット。"
            "アウツが減ったドローは慎重に評価（ポットオッズを確認）。"
            f"現在のポット: {pot}チップ。"
            "ターンでの大きなベットは通常ストロングハンドを示唆。"
        )
        result["betting_tendency"] = "moderate"

    elif phase == "river":
        result["strategy"] = "リバーでは最終的なハンドの価値が確定。バリューベットとブラッフのバランスが重要。"
        result["considerations"] = [
            "完成したハンドの最終的な強さ",
            "ボード全体のテクスチャー（ストレート/フラッシュの可能性）",
            "相手のレンジとの関係（自分のハンドが相手のレンジを上回っているか）",
            "ポットサイズに対するベットサイズ（バリュー最大化 vs ブラッフ）",
            "ベット履歴からの読み（相手がどのようなハンドを持っているか）"
        ]
        result["recommended_approach"] = (
            "ストロングハンドでは最大限のバリューを狙う（ポットの50-75%ベット）。"
            "ミドルレンジの手では状況に応じてチェック/コールまたはベット。"
            "ウィークハンドではチェック/フォールドを基本とするが、ブラッフを検討する場面も。"
            f"コールに必要な額: {to_call}チップ。"
        )
        result["betting_tendency"] = "tight" if to_call > pot * 0.5 else "moderate"

    else:
        result["strategy"] = f"フェーズ '{phase}' は分析対象外です。"
        result["considerations"] = []
        result["recommended_approach"] = "フェーズ情報を確認してください。"

    # 追加のコンテキスト情報
    if to_call > 0:
        pot_odds = to_call / (pot + to_call) if (pot + to_call) > 0 else 0
        result["considerations"].append(
            f"ポットオッズ: {pot_odds:.1%} (コール{to_call} / ポット{pot + to_call})"
        )

    return result

