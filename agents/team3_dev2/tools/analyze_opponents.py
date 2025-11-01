"""
相手プレイヤー分析ツール - JSONヒストリーから相手プレイヤーの傾向を分析
"""

import json
import re
from typing import Optional, List, Dict, Any
from collections import defaultdict


def _parse_history_entry(history_entry: str) -> Optional[Dict[str, Any]]:
    """
    ヒストリー文字列からアクション情報を抽出

    Args:
        history_entry: ヒストリー文字列（例: "Player 1 bet 20", "Preflop: All players called 30"）

    Returns:
        パースされたアクション情報、またはNone
    """
    if not history_entry:
        return None

    # Player ID, アクションタイプ, 金額を抽出
    patterns = [
        # "Player X action [amount]"
        r"Player\s+(\d+)\s+(folded|fold|checked|check|called|call|bet|raised|raise|all[- ]?in|all-in)\s*(?:\((\d+)\))?\s*(?:(\d+))?",
        # "Player X posted small blind X" or "big blind X"
        r"Player\s+(\d+)\s+posted\s+(small_blind|big_blind)\s+(\d+)",
        # "All players called X"
        r"All\s+players\s+(called|folded|checked)\s*(?:(\d+))?",
        # Phase info: "Preflop: ...", "Flop: ...", etc.
        r"(Preflop|Flop|Turn|River):\s*(.+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, history_entry, re.IGNORECASE)
        if match:
            groups = match.groups()

            # Phase情報
            if len(groups) == 2 and groups[0] in ["Preflop", "Flop", "Turn", "River"]:
                phase = groups[0].lower()
                # 再帰的に残りの部分をパース
                rest = groups[1]
                action_info = _parse_history_entry(rest)
                if action_info:
                    action_info["phase"] = phase
                return action_info

            # Player action
            if len(groups) >= 2:
                player_id = int(groups[0])
                action_str = groups[1].lower()

                # アクションタイプの正規化
                action_type_map = {
                    "fold": "fold",
                    "folded": "fold",
                    "check": "check",
                    "checked": "check",
                    "call": "call",
                    "called": "call",
                    "bet": "raise",
                    "raise": "raise",
                    "raised": "raise",
                    "all-in": "all_in",
                    "all in": "all_in",
                    "small_blind": "small_blind",
                    "big_blind": "big_blind",
                }

                action_type = action_type_map.get(action_str, action_str)

                # 金額の抽出
                amount = 0
                if len(groups) >= 3 and groups[2]:
                    amount = int(groups[2])
                elif len(groups) >= 4 and groups[3]:
                    amount = int(groups[3])
                elif len(groups) >= 3 and groups[2] and groups[2].isdigit():
                    amount = int(groups[2])

                return {
                    "player_id": player_id,
                    "action_type": action_type,
                    "amount": amount,
                }

    return None


def _extract_actions_from_history(history: List[str], my_id: int) -> Dict[int, List[Dict[str, Any]]]:
    """
    ヒストリーから各プレイヤーのアクションを抽出

    Args:
        history: ヒストリー文字列のリスト
        my_id: 自分のプレイヤーID（除外する）

    Returns:
        プレイヤーID -> アクションリストの辞書
    """
    player_actions = defaultdict(list)
    current_phase = "preflop"

    for entry in history:
        # フェーズ情報を更新
        phase_match = re.search(r"(Preflop|Flop|Turn|River):", entry, re.IGNORECASE)
        if phase_match:
            current_phase = phase_match.group(1).lower()

        # アクションをパース
        action_info = _parse_history_entry(entry)
        if action_info and "player_id" in action_info:
            player_id = action_info["player_id"]

            # 自分のアクションは除外
            if player_id == my_id:
                continue

            # フェーズ情報を追加
            if "phase" not in action_info:
                action_info["phase"] = current_phase

            player_actions[player_id].append(action_info)

    return dict(player_actions)


def _calculate_playing_style(stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    プレイスタイルを計算

    Args:
        stats: プレイヤーの統計情報

    Returns:
        プレイスタイル分析結果
    """
    action_counts = stats.get("action_counts", {})
    hands_played = stats.get("hands_played", 1)

    # 各アクションの頻度
    folds = action_counts.get("fold", 0)
    checks = action_counts.get("check", 0)
    calls = action_counts.get("call", 0) + action_counts.get("small_blind", 0) + action_counts.get("big_blind", 0)
    raises = action_counts.get("raise", 0)
    all_ins = action_counts.get("all_in", 0)

    total_actions = folds + checks + calls + raises + all_ins
    if total_actions == 0:
        return {
            "style": "unknown",
            "tightness": 0.5,
            "aggressiveness": 0.5,
            "vpip": 0.0,
            "pfr": 0.0,
            "afq": 0.0,
        }

    # VPIP (Voluntarily Put chips In Pot) - 任意でチップを投入した割合
    # call, raise, all_in が該当（small_blind/big_blind除く）
    voluntary_actions = calls + raises + all_ins - action_counts.get("small_blind", 0) - action_counts.get("big_blind", 0)
    vpip = voluntary_actions / hands_played if hands_played > 0 else 0.0

    # PFR (Pre-Flop Raise) - プリフロップでレイズした割合（概算）
    preflop_raises = stats.get("preflop_raises", 0)
    pfr = preflop_raises / hands_played if hands_played > 0 else 0.0

    # AFQ (Aggression Frequency) - アグレッション頻度
    # (レイズ + オールイン) / (コール + チェック + レイズ + オールイン)
    aggressive_actions = raises + all_ins
    passive_actions = calls + checks - action_counts.get("small_blind", 0) - action_counts.get("big_blind", 0)
    afq = aggressive_actions / (aggressive_actions + passive_actions) if (aggressive_actions + passive_actions) > 0 else 0.0

    # タイトネス（タイト/ルーズ）
    # VPIPが低いほどタイト
    if vpip < 0.15:
        tightness = 0.9  # 非常にタイト
    elif vpip < 0.25:
        tightness = 0.7  # タイト
    elif vpip < 0.40:
        tightness = 0.5  # バランス
    elif vpip < 0.60:
        tightness = 0.3  # ルーズ
    else:
        tightness = 0.1  # 非常にルーズ

    # アグレッシブネス（アグレッシブ/パッシブ）
    aggressiveness = afq

    # スタイル分類
    if tightness >= 0.7 and aggressiveness >= 0.5:
        style = "TAG (Tight Aggressive)"
    elif tightness >= 0.7 and aggressiveness < 0.5:
        style = "Tight Passive"
    elif tightness < 0.4 and aggressiveness >= 0.5:
        style = "LAG (Loose Aggressive)"
    elif tightness < 0.4 and aggressiveness < 0.5:
        style = "Loose Passive"
    elif aggressiveness >= 0.6:
        style = "Aggressive"
    elif aggressiveness <= 0.3:
        style = "Passive"
    else:
        style = "Balanced"

    return {
        "style": style,
        "tightness": round(tightness, 3),
        "aggressiveness": round(aggressiveness, 3),
        "vpip": round(vpip, 3),
        "pfr": round(pfr, 3),
        "afq": round(afq, 3),
    }


def _calculate_player_stats(actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    プレイヤーのアクションリストから統計を計算

    Args:
        actions: プレイヤーのアクションリスト

    Returns:
        統計情報の辞書
    """
    action_counts = defaultdict(int)
    bet_amounts = []
    preflop_raises = 0
    hands_played = 0
    showdowns = 0
    wins = 0
    total_winnings = 0

    # ハンド数を推定（フォールド、ショーダウン到達などから）
    folded_hands = sum(1 for a in actions if a.get("action_type") == "fold")
    # 簡単な推定: フォールドした回数 + 参加した回数（正確な計算は難しいため概算）
    hands_played = folded_hands + 1  # 最低1ハンドはプレイ

    for action in actions:
        action_type = action.get("action_type", "")
        amount = action.get("amount", 0)
        phase = action.get("phase", "")

        action_counts[action_type] += 1

        if amount > 0:
            bet_amounts.append(amount)

        if phase == "preflop" and action_type in ["raise", "all_in"]:
            preflop_raises += 1

    # 平均ベットサイズ
    avg_bet = sum(bet_amounts) / len(bet_amounts) if bet_amounts else 0

    return {
        "action_counts": dict(action_counts),
        "hands_played": hands_played,
        "average_bet_size": round(avg_bet, 2),
        "preflop_raises": preflop_raises,
        "showdowns": showdowns,
        "showdown_wins": wins,
        "total_winnings": total_winnings,
    }


def _analyze_betting_patterns(actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    ベッティングパターンを分析

    Args:
        actions: 最近のアクション履歴

    Returns:
        ベッティングパターン分析結果
    """
    if not actions:
        return {
            "average_bet_size": 0,
            "raise_frequency": 0.0,
            "recent_actions_count": 0,
        }

    bet_amounts = []
    raises_count = 0
    total_actions = len(actions)

    for action in actions:
        amount = action.get("amount", 0)
        action_type = action.get("action_type", "")

        if amount > 0:
            bet_amounts.append(amount)

        if action_type == "raise":
            raises_count += 1

    avg_bet = sum(bet_amounts) / len(bet_amounts) if bet_amounts else 0
    raise_frequency = raises_count / total_actions if total_actions > 0 else 0.0

    return {
        "average_bet_size": round(avg_bet, 2),
        "raise_frequency": round(raise_frequency, 3),
        "recent_actions_count": total_actions,
    }


def analyze_opponents(
    history_json: str,
    my_id: Optional[int] = None,
    opponent_ids: Optional[List[int]] = None,
) -> str:
    """
    JSONヒストリーから相手プレイヤーの分析を行う

    指定されたJSONヒストリーから相手プレイヤーの統計情報を抽出し、以下の分析を行います:
    - プレイスタイル（タイト/ルーズ、アグレッシブ/パッシブ）
    - VPIP, PFR, AFQなどの統計指標
    - ベッティングパターン
    - アクション分布

    Args:
        history_json: JSON形式のヒストリー（文字列または辞書形式）
        my_id: 自分のプレイヤーID（Noneの場合はhistory_jsonからyour_idを取得）
        opponent_ids: 分析対象のプレイヤーIDリスト（Noneの場合は全相手プレイヤー）

    Returns:
        分析結果をJSON形式の文字列で返します

    Example:
        >>> history_json = '{"your_id": 0, "history": ["Player 1 bet 20", ...]}'
        >>> analyze_opponents(history_json)
        '{"opponents": [{"player_id": 1, "style": "TAG", ...}, ...]}'
    """
    try:
        # JSON文字列をパース
        if isinstance(history_json, str):
            history_data = json.loads(history_json)
        else:
            history_data = history_json

        # 自分のIDを取得
        if my_id is None:
            my_id = history_data.get("your_id")

        if my_id is None:
            return json.dumps({
                "error": "プレイヤーIDが指定されていません",
                "message": "my_idまたはhistory_jsonにyour_idを指定してください"
            }, ensure_ascii=False, indent=2)

        # ヒストリーを取得
        history = history_data.get("history", [])
        if not history:
            return json.dumps({
                "error": "ヒストリーが空です",
                "message": "history_jsonにhistoryフィールドが含まれていないか、空です"
            }, ensure_ascii=False, indent=2)

        # プレイヤー情報から相手プレイヤーIDを取得
        players = history_data.get("players", [])
        all_player_ids = {p.get("id") for p in players if p.get("id") != my_id}

        # ヒストリーからアクションを抽出
        player_actions = _extract_actions_from_history(history, my_id)

        # ヒストリーから抽出されたプレイヤーIDとプレイヤー情報から取得したIDをマージ
        all_opponent_ids = set(player_actions.keys()) | all_player_ids

        # opponent_idsが指定されている場合はフィルタリング
        if opponent_ids is not None:
            all_opponent_ids = all_opponent_ids & set(opponent_ids)

        if not all_opponent_ids:
            return json.dumps({
                "error": "分析対象のプレイヤーが見つかりません",
                "message": "指定されたプレイヤーIDが存在しないか、履歴がありません"
            }, ensure_ascii=False, indent=2)

        # 各プレイヤーの統計を取得して分析
        opponents_analysis = []

        for player_id in sorted(all_opponent_ids):
            actions = player_actions.get(player_id, [])

            # 統計情報を計算
            stats = _calculate_player_stats(actions)

            # プレイスタイルを計算
            style_analysis = _calculate_playing_style(stats)

            # ベッティングパターンを分析（最近のアクション）
            recent_actions = actions[-20:] if len(actions) > 20 else actions
            betting_patterns = _analyze_betting_patterns(recent_actions)

            # ショーダウン統計（ヒストリーからは正確に取得できないため、デフォルト値）
            showdown_stats = {
                "showdowns": stats.get("showdowns", 0),
                "wins": stats.get("showdown_wins", 0),
                "win_rate": 0.0,
                "total_winnings": stats.get("total_winnings", 0),
            }

            # アクション分布
            action_distribution = {
                action_type: round(count / stats.get("hands_played", 1), 3)
                for action_type, count in stats.get("action_counts", {}).items()
            }

            # 結果をまとめる
            player_analysis = {
                "player_id": player_id,
                "hands_played": stats.get("hands_played", 0),
                "playing_style": style_analysis,
                "betting_patterns": betting_patterns,
                "showdown_stats": showdown_stats,
                "action_distribution": action_distribution,
                "total_actions": len(actions),
            }

            opponents_analysis.append(player_analysis)

        # 結果を整形
        result = {
            "analysis_summary": {
                "total_opponents": len(opponents_analysis),
                "my_player_id": my_id,
            },
            "opponents": opponents_analysis,
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except json.JSONDecodeError as e:
        return json.dumps({
            "error": f"JSON解析エラー: {str(e)}",
            "message": "history_jsonが有効なJSON形式ではありません"
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        import traceback
        return json.dumps({
            "error": str(e),
            "traceback": traceback.format_exc(),
            "message": "相手プレイヤーの分析中にエラーが発生しました"
        }, ensure_ascii=False, indent=2)
