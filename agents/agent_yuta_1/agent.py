from google.adk.agents import SequentialAgent
from .sub_agent.hand_strenght import root_agent as hand_strength_agent
from .sub_agent.board_texture import root_agent as board_texture_agent
from .sub_agent.bet_size import root_agent as bet_size_agent
from .sub_agent.format import root_agent as format_agent
from .sub_agent.action import root_agent as action_agent
from .sub_agent.forecast import root_agent as forecast_agent

root_agent = SequentialAgent(
    name="poker_action_orchestrator",
    description="戦略的な意思決定を行うテキサスホールデム・ポーカープレイヤー",
    sub_agents=[
        hand_strength_agent,
        board_texture_agent,
        forecast_agent,
        action_agent,
        bet_size_agent,
        format_agent
    ]
)
