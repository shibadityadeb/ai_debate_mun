"""Builds contextual system prompt for debate agents."""

from typing import List

from app.memory.state_store import DebateState, DebateMessage


def _format_message(message: DebateMessage) -> str:
    return f"* {message.agent} ({message.role}): {message.content}"


def _truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def build_context(
    state: DebateState,
    agent_name: str,
    phase: str,
    retrieved_context: str = "",
    history_limit: int = 6,
    max_length: int = 1200,
) -> str:
    """Generate agent prompt context from debate state.

    Args:
        state: Current debate state.
        agent_name: Agent receiving context.
        phase: Current debate phase (e.g., opening, rebuttal).
        retrieved_context: Real-world knowledge to inject into context.
        history_limit: Number of recent messages to include.
        max_length: Maximum total characters for the generated context.

    Returns:
        A formatted context string for the agent.
    """
    phase_label = phase.capitalize()

    # Exclude own previous messages for rebuttal phase, otherwise include all
    if phase_label.lower() == "rebuttal":
        messages = [m for m in state.history if m.agent != agent_name]
    else:
        messages = list(state.history)

    recent = messages[-history_limit:]

    history_lines: List[str] = ["Recent Discussion:"]
    if recent:
        for msg in recent:
            history_lines.append(_format_message(msg))
    else:
        history_lines.append("* No prior messages yet.")

    instructions = [
        "Instructions:",
        "- Stay in character as your assigned country delegate.",
        "- Be strategic and defend national interests.",
        "- Respond to others in the debate and build on their points.",
    ]

    sections = [
        f"Debate Topic: {state.topic}",
        f"Phase: {phase_label}",
        "",
    ]

    sections += history_lines

    if retrieved_context:
        sections += ["", "REAL-WORLD CONTEXT:", retrieved_context]

    sections += ["", *instructions]

    context = "\n".join(sections)
    return _truncate_text(context, max_length)

