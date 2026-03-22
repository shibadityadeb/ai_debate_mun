
from collections import defaultdict
from typing import Dict, List


class RoundManager:

    def __init__(self):
        pass

    @staticmethod
    def analyze_relationships(history: List[Dict[str, str]]) -> Dict[str, Dict[str, List[str]]]:
        """Analyzes debate history to infer alliances and conflicts.

        Args:
            history: A list of messages, each with keys like 'agent', 'role', 'content'.

        Returns:
            A dict with 'alliances' and 'conflicts' mapping agents to counterparties.
        """
        # Simple keywords for support and attack
        support_keywords = ["agree", "support", "concur", "ally", "cooperate"]
        conflict_keywords = ["disagree", "oppose", "counter", "criticize", "attack", "challenge"]

        alliances = defaultdict(set)
        conflicts = defaultdict(set)

        # If an entry explicitly mentions another country with positive/negative words, infer relationship.
        for entry in history:
            agent = entry.get("agent", "")
            content = entry.get("content", "").lower()

            # extract potential mentioned countries from content by uppercase words or names in text
            tokens = content.replace(".", "").replace(",", "").split()
            potential_targets = [t.strip("()[]\"')") for t in tokens if t.capitalize() == t and t.isalpha()]

            # fallback: check in 2-word sequences for common country names (lower-cased)
            # Without heavy NLP, we assume agent names appear plainly
            if not potential_targets:
                words = content.split()
                for i in range(len(words) - 1):
                    candidate = f"{words[i]} {words[i+1]}".strip()
                    if candidate.istitle():
                        potential_targets.append(candidate)

            for target in potential_targets:
                if target == agent or not target:
                    continue
                if any(kw in content for kw in support_keywords):
                    alliances[agent].add(target)
                    alliances[target].add(agent)
                if any(kw in content for kw in conflict_keywords):
                    conflicts[agent].add(target)
                    conflicts[target].add(agent)

        # Convert sets to sorted lists for stable output
        alliances_out = {k: sorted(list(v)) for k, v in alliances.items()}
        conflicts_out = {k: sorted(list(v)) for k, v in conflicts.items()}

        return {
            "alliances": alliances_out,
            "conflicts": conflicts_out,
        }

