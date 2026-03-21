"""Country agent representing a UN member state."""
from app.agents.base_agent import BaseAgent


class CountryAgent(BaseAgent):
    """Country participant agent."""

    def act(self, context):
        return {'action': 'country_statement'}
