"""Wikipedia search action and helper utilities for population extraction."""

from __future__ import annotations

import re
from typing import Optional, Tuple

from agentlite.actions.BaseAction import BaseAction
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper


class WikipediaSearch(BaseAction):
    """Wrapper for WikipediaQueryRun action."""

    def __init__(self) -> None:
        action_name = "Wikipedia_Search"
        action_desc = "Using this API to search Wiki content."
        params_doc = {"query": "the search string. be simple."}
        self.search = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
        super().__init__(action_name=action_name, action_desc=action_desc, params_doc=params_doc)

    def __call__(self, query: str) -> str:
        return self.search.run(query)


def extract_population(text: str) -> Optional[int]:
    """Extract a population number from plain text."""
    if not text:
        return None
    patterns = [
        r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*million",
        r"(\d{9,})",
        r"(\d{1,3}(?:,\d{3})+)",
    ]
    lowered = text.lower()
    for pattern in patterns:
        match = re.search(pattern, lowered)
        if not match:
            continue
        num_str = match.group(1).replace(",", "")
        try:
            number = float(num_str)
        except ValueError:
            continue
        if "million" in lowered[match.start(): match.end() + 10]:
            number *= 1e6
        return int(number)
    return None


def print_population_debug(label: str, value: Optional[int]) -> None:
    if value:
        print(f"  ✅ {label}: extracted {value}")
    else:
        print(f"  ⚠️ {label}: extraction failed")


def extract_population_values(
    agent,
    extractor,
    default_ca: int = 10_000_000,
    default_mx: int = 100_000_000,
) -> Tuple[int, int]:
    """Pull California and Mexico populations from an agent's memory."""
    california_pop = None
    mexico_pop = None
    print("  Debug: Checking search_agent memory...")
    if hasattr(agent, "short_term_memory") and hasattr(agent.short_term_memory, "memory"):
        memory = agent.short_term_memory.memory
        print(f"  Debug: Memory exists with {len(memory)} tasks")
        for task_id, task_data in memory.items():
            print(f"  Debug: Task {task_id}, keys: {list(task_data.keys())}")
            action_chain = task_data.get("act_obs", [])
            print(f"  Debug: Found {len(action_chain)} action-observation pairs")
            for action, observation in action_chain:
                if action.name != "Wikipedia_Search":
                    continue
                query = action.params.get("query", "").lower()
                print(f"  Debug: Wikipedia search query: {query}")
                print(f"  Debug: Observation snippet: {observation[:200]}...")
                if "california" in query and california_pop is None:
                    california_pop = extractor(observation)
                    print_population_debug("California", california_pop)
                if "mexico" in query and mexico_pop is None:
                    mexico_pop = extractor(observation)
                    print_population_debug("Mexico", mexico_pop)
    else:
        print("  ⚠️ Debug: No memory found in search_agent")
    if california_pop is None:
        california_pop = default_ca
        print(f"  ⚠️ California: using default value {california_pop}")
    if mexico_pop is None:
        mexico_pop = default_mx
        print(f"  ⚠️ Mexico: using default value {mexico_pop}")
    return california_pop, mexico_pop
