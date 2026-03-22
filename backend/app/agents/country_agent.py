"""Country agent representing a UN member state."""

from typing import Dict, List

from app.agents.base_agent import BaseAgent
from app.llm.llm_client import LLMClient


class CountryAgent(BaseAgent):
    """Country participant agent with identity-based prompts."""

    def __init__(self, country_profile: Dict[str, object], llm_client: LLMClient):
        """Initialize CountryAgent with profile and LLM client."""
        self.country_profile = country_profile

        self.aggression_level = self._normalize_level(country_profile.get("aggression_level", 0.5))
        self.cooperation_level = self._normalize_level(country_profile.get("cooperation_level", 0.5))

        system_prompt = self._build_system_prompt(country_profile)

        super().__init__(
            name=country_profile.get("name", "Unknown Country"),
            system_prompt=system_prompt,
            llm_client=llm_client,
        )

    @staticmethod
    def _normalize_level(value: object) -> float:
        try:
            level = float(value)
        except (TypeError, ValueError):
            level = 0.5
        return min(max(level, 0.0), 1.0)


    @staticmethod
    def _format_goals(goals: List[str]) -> str:
        return "\n".join(f"- {goal}" for goal in goals)

    @classmethod
    def _build_system_prompt(cls, profile: Dict[str, object]) -> str:
        name = profile.get("name", "Unknown")
        stance = profile.get("stance", "Neutral stance")
        tone = profile.get("tone", "Diplomatic")
        goals = profile.get("goals", [])

        if not isinstance(goals, list):
            goals = [str(goals)]

        goal_block = cls._format_goals(goals)

        aggression_level = profile.get("aggression_level", 0.5)
        cooperation_level = profile.get("cooperation_level", 0.5)

        return (
            f"You are the official delegate of {name} in a United Nations debate. "
            f"Your role is to represent your country’s interests with clarity and strategy.\n\n"
            f"Country identity: {name}\n"
            f"Political stance: {stance}\n"
            f"Tone: {tone}\n"
            f"Aggression level: {aggression_level}\n"
            f"Cooperation level: {cooperation_level}\n"
            f"Strategic goals:\n{goal_block}\n\n"
            "Follow these guidelines:\n"
            "- Speak diplomatically and respectfully.\n"
            "- Defend national interests strongly.\n"
            "- Avoid repeating the same arguments.\n"
            "- You may challenge opposing countries directly.\n"
            "- You may form alliances with cooperative partners.\n"
            "- You must protect national interests above all.\n"
            "- Be strategic, not generic.\n"
            "- Maintain character and do not break role.\n"
            "- Use opponent and ally arguments provided in context to guide responses.\n"
        )

    async def act(self, context: str) -> str:
        """Generate a response for given context using inherited BaseAgent behavior."""
        return await super().act(context)

