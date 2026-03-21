"""Base agent interface for all agents."""


class BaseAgent:
    """Abstract agent contract."""

    def act(self, context):
        raise NotImplementedError
