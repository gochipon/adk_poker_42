"""
Team2 poker agent package entry point.

Expose the main `root_agent` so ADK can load it via `team2_agent.agent`.
"""

from .agent import root_agent

__all__ = ["root_agent"]
