from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from ..tools.porker_rank import rank_of_any_card
from typing import List, Dict, Any

def hand_rank_evaluator_tool(cards: List[str])->Dict[str, Any]:
    """
    ポーカーの役判定ツール。
    Args:
        cards (List[str]): 例 ['AS', 'KD', 'QS', 'JH', 'TC']
    Returns:
        dict: {"role": 役名, "cards": [使った5枚], "score": int}
    """
    hand, role, score = rank_of_any_card(cards)
    return {
        "role": role,
        "cards": list(hand),
        "score": score
    }
hand_rank_evaluator_tool.__name__ = "hand_rank_evaluator_tool"

hand_rank_evaluator_agent = Agent(
    name="hand_rank_evaluator_agent",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    description="入力されたカード配列から最強役を判定しJSON回答する専用エージェント",
    instruction="""
あなたはテキサスホールデム・ポーカーの役判定専用AIです。必ず以下のJSON形式で答えてください:
{
  "role": "役名の英語",
  "cards": [役判定に使われた5枚],
  "score": 整数スコア
}
役判定には hand_rank_evaluator_tool を必ず使って下さい。
入力例: ["AS", "KS", "QS", "JS", "TS", "2D", "3C"]
""",
    tools=[hand_rank_evaluator_tool],
    output_key = "hand_rank",
)
