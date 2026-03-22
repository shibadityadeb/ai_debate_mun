from app.agents.base_agent import BaseAgent


class JudgeAgent(BaseAgent):

    def __init__(self, llm_client, name: str = "Judge"):
        system_prompt = (
            "You are a strict, unbiased United Nations debate judge. "
            "Your task is to evaluate the debate transcript and score each country on four axes: "
            "logical strength, diplomatic tone, factual relevance, and strategic alignment. "
            "Be fair and do not hallucinate. Compare agents based on the transcript only. "
            "Output must be valid JSON in this exact structure:\n"
            "{\n"
            "  \"scores\": {\n"
            "    \"<Country>\": {\n"
            "      \"logic\": <0-10>,\n"
            "      \"diplomacy\": <0-10>,\n"
            "      \"facts\": <0-10>,\n"
            "      \"strategy\": <0-10>,\n"
            "      \"total\": <sum>\n"
            "    }, ...\n"
            "  },\n"
            "  \"winner\": \"<Country>\",\n"
            "  \"reasoning\": \"...\"\n"
            "}"
        )
        super().__init__(name=name, system_prompt=system_prompt, llm_client=llm_client)

    async def act(self, context: str) -> str:
        """Evaluate the debate and return strict JSON scoring."""

        if not isinstance(context, str) or not context.strip():
            raise ValueError("context must be a non-empty debate transcript")

        user_prompt = (
            "Use the following debate transcript to evaluate each participating country. "
            "Do not add extraneous fields; output only valid JSON.\n\n"
            "Debate Transcript:\n"
            f"{context}\n"
        )

        response = await self.llm_client.generate(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
        )

        return response

