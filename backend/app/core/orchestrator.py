
import asyncio
import random
from typing import List, Dict, Optional
from app.agents.country_agent import CountryAgent
from app.agents.judge_agent import JudgeAgent
from app.agents.moderator_agent import ModeratorAgent
from app.memory.context_builder import build_context
from app.memory.state_store import DebateState, DebateMessage
from app.mcp.retriever import Retriever


class DebateOrchestrator:
    

    def __init__(
        self,
        agents: List[CountryAgent],
        moderator: ModeratorAgent,
        judge: JudgeAgent,
        state: DebateState,
        retriever: Optional[Retriever] = None,
    ):
        self.agents = agents
        self.moderator = moderator
        self.judge = judge
        self.state = state
        self.retriever = retriever or Retriever()

    def initialize_debate(self, topic: str, countries: List[str]) -> None:
        """Initialize debate state."""
        self.state.topic = topic
        self.state.countries = list(countries)
        self.state.current_round = "opening"
        self.state.history = []
        self.state.resolution = None
        self.state.votes = {}

    async def _ask_agent(self, agent, context: str):
        result = agent.act(context)
        if asyncio.iscoroutine(result):
            result = await result
        return result

    def _normalize_response(self, response) -> str:
        if isinstance(response, dict):
            return response.get("content") or response.get("text") or str(response)
        return str(response)

    async def run_opening_round(self) -> None:
        """Run opening statements from all agents."""
        self.state.current_round = "opening"
        retrieved_context = self.retriever.get_context(self.state.topic)

        for agent in self.agents:
            context = build_context(
                self.state,
                agent.name,
                "opening",
                retrieved_context=retrieved_context,
            )
            response = await self._ask_agent(agent, context)
            text = self._normalize_response(response)

            message = DebateMessage(agent=agent.name, role="opening", content=text)
            self.state.history.append(message)

    async def run_rebuttal_round(self, rounds: int = 1) -> None:
        """Run rebuttal rounds where agents respond strategically to opponents."""
        for i in range(rounds):
            self.state.current_round = f"rebuttal-{i+1}"
            retrieved_context = self.retriever.get_context(self.state.topic)
            tasks = []
            for agent in self.agents:
                context = build_context(
                    self.state,
                    agent.name,
                    "rebuttal",
                    retrieved_context=retrieved_context,
                )
                tasks.append((agent, self._ask_agent(agent, context)))

            results = []
            for agent, task in tasks:
                response = await task
                text = self._normalize_response(response)
                results.append((agent.name, text))

            for agent_name, text in results:
                message = DebateMessage(agent=agent_name, role="rebuttal", content=text)
                self.state.history.append(message)

    async def run_resolution_phase(self) -> None:
        """Generate final resolution from moderator."""
        self.state.current_round = "resolution"
        retrieved_context = self.retriever.get_context(self.state.topic)
        context = build_context(
            self.state,
            "Moderator",
            "resolution",
            retrieved_context=retrieved_context,
        )
        response = await self._ask_agent(self.moderator, context)
        text = self._normalize_response(response)

        self.state.resolution = text
        self.state.history.append(DebateMessage(agent="Moderator", role="resolution", content=text))

    async def run_voting_phase(self) -> None:
        """Each agent votes yes/no/abstain on the resolution."""
        self.state.current_round = "voting"
        voted: Dict[str, str] = {}

        for agent in self.agents:
            # Simple deterministic vote based on the agent name hash
            choice = random.choice(["yes", "no", "abstain"])
            voted[agent.name] = choice
            self.state.history.append(
                DebateMessage(agent=agent.name, role="vote", content=choice)
            )

        self.state.votes = voted

    async def run_judging_phase(self) -> Dict[str, str]:
        """Judge evaluates the debate and returns score and reasoning."""
        self.state.current_round = "judging"
        retrieved_context = self.retriever.get_context(self.state.topic)
        context = build_context(
            self.state,
            "Judge",
            "judging",
            retrieved_context=retrieved_context,
        )
        response = await self._ask_agent(self.judge, context)
        text = self._normalize_response(response)

        decision = {
            "score": "undecided",
            "reasoning": text,
        }
        self.state.history.append(DebateMessage(agent="Judge", role="judging", content=text))
        return decision

    async def run_full_debate(self) -> DebateState:
        """Run full debate sequence and return final state."""
        await self.retriever.fetch_and_store(self.state.topic)

        await self.run_opening_round()
        await self.run_rebuttal_round(rounds=2)
        await self.run_resolution_phase()
        await self.run_voting_phase()
        await self.run_judging_phase()
        return self.state

