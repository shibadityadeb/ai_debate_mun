import asyncio
import random
from typing import Dict, List, Optional

from app.agents.country_agent import CountryAgent
from app.agents.judge_agent import JudgeAgent
from app.agents.moderator_agent import ModeratorAgent
from app.mcp.retriever import Retriever
from app.memory.context_builder import build_context
from app.memory.state_store import DebateMessage, DebateState


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

    async def _generate_agent_message(self, agent: CountryAgent, phase: str, retrieved_context: str = "") -> None:
        """Generate and store a single agent message sequentially."""
        print(f"{agent.name} generating response...")
        context = build_context(
            self.state,
            agent.name,
            phase,
            retrieved_context=retrieved_context,
        )
        response = await self._ask_agent(agent, context)
        text = self._normalize_response(response)
        self.state.history.append(DebateMessage(agent=agent.name, role=phase, content=text))
        print(f"  -> {agent.name} ({phase}): {text[:80]}...")

    async def run_opening_round(self) -> None:
        """Run opening statements sequentially."""
        self.state.current_round = "opening"
        retrieved_context = self.retriever.get_context(self.state.topic)

        for agent in self.agents:
            await self._generate_agent_message(agent, "opening", retrieved_context)

    async def run_rebuttal_round(self, rounds: int = 1) -> None:
        """Run rebuttal rounds sequentially so each agent sees prior responses."""
        retrieved_context = self.retriever.get_context(self.state.topic) if self.retriever else ""

        for round_index in range(rounds):
            phase = f"rebuttal-{round_index + 1}"
            self.state.current_round = phase
            print(f"🔁 Starting {phase}...")

            for agent in self.agents:
                await self._generate_agent_message(agent, phase, retrieved_context)

    async def run_resolution_phase(self) -> None:
        """Generate final resolution from moderator."""
        self.state.current_round = "resolution"
        print("Moderator generating response...")
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
        print(f"  -> Moderator (resolution): {text[:80]}...")

    async def run_voting_phase(self) -> None:
        """Each agent votes yes/no/abstain on the resolution."""
        self.state.current_round = "voting"
        voted: Dict[str, str] = {}

        for agent in self.agents:
            choice = random.choice(["yes", "no", "abstain"])
            voted[agent.name] = choice
            self.state.history.append(DebateMessage(agent=agent.name, role="vote", content=choice))
            print(f"  -> {agent.name} (vote): {choice}")

        self.state.votes = voted

    async def run_judging_phase(self) -> Dict[str, str]:
        """Judge evaluates the debate and returns score and reasoning."""
        self.state.current_round = "judging"
        print("Judge generating response...")
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
        print(f"  -> Judge (judging): {text[:80]}...")
        return decision

    async def run_full_debate(self) -> DebateState:
        """Run full debate sequence and return final state."""
        print(f"🎭 [ORCHESTRATOR] Starting full debate on topic: {self.state.topic}")

        try:
            await self.retriever.fetch_and_store(self.state.topic)
        except Exception as error:
            print(f"⚠️  Context retrieval failed: {error}, continuing with debate")

        print("📝 [PHASE 1] Running Opening Round...")
        await self.run_opening_round()
        print(f"✅ Opening Round Complete. Messages: {len(self.state.history)}")

        print("💬 [PHASE 2] Running Rebuttal Rounds...")
        await self.run_rebuttal_round(rounds=2)
        print(f"✅ Rebuttal Complete. Total Messages: {len(self.state.history)}")

        print("🤝 [PHASE 3] Running Resolution Phase...")
        await self.run_resolution_phase()
        print(f"✅ Resolution Complete. Total Messages: {len(self.state.history)}")

        print("🗳️  [PHASE 4] Running Voting Phase...")
        await self.run_voting_phase()
        print(f"✅ Voting Complete. Votes: {self.state.votes}")

        print("⚖️  [PHASE 5] Running Judging Phase...")
        await self.run_judging_phase()
        print(f"✅ Judging Complete. Total Messages: {len(self.state.history)}")

        print("🎉 [ORCHESTRATOR] Full debate completed!")
        return self.state
