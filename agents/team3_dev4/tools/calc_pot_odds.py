"""
ポットオッズ計算ツール
"""

import json
from typing import Union, Dict, Any, Optional


def calc_pot_odds(
    pot: float,
    to_call: float,
    format_type: str = "ratio"
) -> Dict[str, Any]:
    """
    ポットオッズを計算する。

    Args:
        pot (float): 現在のポット額
        to_call (float): コールに必要な額
        format_type (str): 出力形式。'ratio'（比率）、'percentage'（パーセンテージ）、'all'（全て）のいずれか

    Returns:
        Dict[str, Any]: ポットオッズ計算結果
            - pot_odds_ratio: ポットオッズ比（例: "5:1"）
            - pot_odds_percentage: ポットオッズパーセンテージ（例: 16.67）
            - break_even_equity: 損益分岐点の勝率（0.0-1.0）
            - pot_after_call: コール後のポットサイズ
            - pot_to_call_ratio: ポットとコール額の比
    """
    if pot < 0 or to_call < 0:
        raise ValueError("potとto_callは0以上である必要があります")

    if to_call == 0:
        # コールが不要な場合（チェック可能）
        return {
            "pot_odds_ratio": "∞:0",
            "pot_odds_percentage": 0.0,
            "break_even_equity": 0.0,
            "pot_after_call": pot,
            "pot_to_call_ratio": float('inf') if pot > 0 else 0.0,
            "message": "コールが不要です（チェック可能）"
        }

    # コール後のポットサイズ
    pot_after_call = pot + to_call

    # 損益分岐点の勝率（Break-even equity）
    # これは、コールする価値があるかどうかを判断する基準
    break_even_equity = to_call / pot_after_call

    # ポットオッズ比（pot:to_call の形式）
    pot_to_call_ratio = pot / to_call

    # ポットオッズ比を文字列形式に変換（例: "5:1"）
    def _format_ratio(ratio: float) -> str:
        """比率を読みやすい形式に変換"""
        if ratio >= 1:
            return f"{ratio:.2f}:1"
        else:
            return f"1:{1/ratio:.2f}"

    pot_odds_ratio_str = _format_ratio(pot_to_call_ratio)

    # ポットオッズパーセンテージ（コール額がポット全体に占める割合）
    pot_odds_percentage = (to_call / pot_after_call) * 100

    result = {
        "pot_odds_ratio": pot_odds_ratio_str,
        "pot_odds_percentage": round(pot_odds_percentage, 2),
        "break_even_equity": round(break_even_equity, 4),
        "pot_after_call": round(pot_after_call, 2),
        "pot_to_call_ratio": round(pot_to_call_ratio, 4),
    }

    # 推奨アクションの判断基準を追加
    if break_even_equity < 0.2:
        result["recommendation"] = "コールは非常に有利（低い勝率で利益が出る）"
    elif break_even_equity < 0.33:
        result["recommendation"] = "コールは有利"
    elif break_even_equity < 0.5:
        result["recommendation"] = "コールは中立的（ハンドの強さ次第）"
    else:
        result["recommendation"] = "コールは不利（高い勝率が必要）"

    return result


def calc_pot_odds_from_game_state(
    game_state: str,
    to_call_override: float = 0
) -> Dict[str, Any]:
    """
    ゲーム状態（JSON）からポットオッズを計算する。

    Args:
        game_state (Union[str, Dict[str, Any]]): ゲーム状態のJSON文字列または辞書
            - pot: 現在のポット額
            - to_call: コールに必要な額
        to_call_override (Optional[float]): to_callの値を上書きする場合に指定

    Returns:
        Dict[str, Any]: ポットオッズ計算結果
    """

    # JSON文字列をパース
    try:
        state = json.loads(game_state)
    except json.JSONDecodeError as e:
        raise ValueError(f"無効なJSON形式: {e}")

    # 必要な情報を抽出
    pot = float(state.get("pot", 0))
    to_call = float(to_call_override if to_call_override != 0 else state.get("to_call", 0))

    # ポットオッズを計算
    result = calc_pot_odds(pot, to_call, format_type="all")

    # ゲーム状態情報も追加
    result["game_state_info"] = {
        "pot": pot,
        "to_call": to_call,
        "phase": state.get("phase", "unknown"),
    }

    return result


def analyze_pot_odds_decision(
    pot: float,
    to_call: float,
    estimated_equity: float
) -> Dict[str, Any]:
    """
    ポットオッズと推定勝率から、コールすべきかどうかを分析する。

    Args:
        pot (float): 現在のポット額
        to_call (float): コールに必要な額
        estimated_equity (float): 推定勝率（0.0-1.0）

    Returns:
        Dict[str, Any]: 分析結果
            - should_call: コールすべきかどうか（True/False）
            - break_even_equity: 損益分岐点の勝率
            - estimated_equity: 推定勝率
            - equity_edge: 推定勝率と損益分岐点の差
            - expected_value: 期待値（簡易版）
    """
    if not (0 <= estimated_equity <= 1):
        raise ValueError("estimated_equityは0.0から1.0の間である必要があります")

    # ポットオッズを計算
    pot_odds = calc_pot_odds(pot, to_call)
    break_even_equity = pot_odds["break_even_equity"]
    pot_after_call = pot_odds["pot_after_call"]

    # 勝率の差（エッジ）
    equity_edge = estimated_equity - break_even_equity

    # コールすべきかどうか
    should_call = estimated_equity > break_even_equity

    # 期待値（簡易版）
    # EV = (勝率 × ポット獲得額) - (負率 × コール額)
    expected_value = (estimated_equity * pot_after_call) - ((1 - estimated_equity) * to_call)

    result = {
        "should_call": should_call,
        "break_even_equity": break_even_equity,
        "estimated_equity": estimated_equity,
        "equity_edge": round(equity_edge, 4),
        "expected_value": round(expected_value, 2),
        "decision_reasoning": "",
    }

    # 判断理由を追加
    if should_call:
        if equity_edge > 0.1:
            result["decision_reasoning"] = f"強くコールを推奨。推定勝率({estimated_equity:.1%})が損益分岐点({break_even_equity:.1%})を{equity_edge:.1%}ポイント上回っています。"
        else:
            result["decision_reasoning"] = f"コールを推奨。推定勝率({estimated_equity:.1%})が損益分岐点({break_even_equity:.1%})を上回っています。"
    else:
        if equity_edge < -0.1:
            result["decision_reasoning"] = f"コールは非推奨。推定勝率({estimated_equity:.1%})が損益分岐点({break_even_equity:.1%})を{abs(equity_edge):.1%}ポイント下回っています。"
        else:
            result["decision_reasoning"] = f"コールは慎重に判断。推定勝率({estimated_equity:.1%})が損益分岐点({break_even_equity:.1%})を下回っていますが、僅差の場合は他の要因（ポジション、相手の傾向など）も考慮してください。"

    return result

