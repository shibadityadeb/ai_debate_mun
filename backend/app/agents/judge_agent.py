"""Judge agent for scoring and adjudication."""
from app.agents.base_agent import BaseAgent


class JudgeAgent(BaseAgent):
    """Judge agent stub."""

    def act(self, context):
        return {'action': 'score'}
