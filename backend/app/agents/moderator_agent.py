"""Moderator agent for debate moderation."""
from app.agents.base_agent import BaseAgent


class ModeratorAgent(BaseAgent):
    """Moderation logic stub."""

    def act(self, context):
        return {'action': 'moderate'}
