"""TrustworthyAgent specialised for Wikipedia searches with trust score handling."""

from __future__ import annotations

import csv
import os
from typing import Dict, Optional

from agentlite.agents.TrustworthyAgent import TrustworthyAgent
from agentlite.commons import AgentAct, TaskPackage
from agentlite.llm.agent_llms import BaseLLM


class TrustworthyAgentForWikipediaSearch(TrustworthyAgent):
    """TrustworthyAgent variant that manages low-trust Wikipedia search results."""

    def __init__(
        self,
        name: str,
        role: str,
        llm: BaseLLM,
        actions,
        trust_score_file: str,
        agent_arch: str = "react",
        logger=None,
        trust_threshold: float = 0.5,
        max_retries: int = 2,
        retry_strategy: str = "warn",
        **kwargs,
    ) -> None:
        super().__init__(
            name=name,
            role=role,
            llm=llm,
            actions=actions,
            trust_score_file=trust_score_file,
            agent_arch=agent_arch,
            logger=logger,
            **kwargs,
        )
        self.trust_threshold = trust_threshold
        self.max_retries = max_retries
        self.retry_strategy = retry_strategy
        self.retry_count: Dict[str, int] = {}
        print("🎯 TrsutWorthyAgentForWikipediaSearch initialized:")
        print(f"   - Trust threshold: {trust_threshold}")
        print(f"   - Retry strategy: {retry_strategy}")
        print(f"   - Max retries: {max_retries}")

    def forward(self, task: TaskPackage, agent_act: AgentAct) -> str:
        observation = super().forward(task, agent_act)
        if agent_act.name == "Wikipedia_Search":
            trust_score = self._get_latest_trust_score()
            if trust_score is None:
                return observation
            if trust_score >= self.trust_threshold:
                print(f"✅ Trust score OK: {trust_score:.4f} >= {self.trust_threshold}")
                return observation
            return self._handle_low_trust(task, agent_act, trust_score, observation)
        return observation

    def _handle_low_trust(
        self,
        task: TaskPackage,
        agent_act: AgentAct,
        trust_score: float,
        observation: str,
    ) -> str:
        action_key = f"{agent_act.name}_{agent_act.params}"
        self.retry_count.setdefault(action_key, 0)
        if self.retry_strategy == "warn":
            self._log_warning(agent_act, trust_score)
            return observation
        if self.retry_strategy == "skip":
            self._log_skip(agent_act, trust_score)
            return "No reliable information found (trust score too low)."
        if self.retry_strategy == "retry" and self.retry_count[action_key] < self.max_retries:
            self.retry_count[action_key] += 1
            self._log_retry(agent_act, trust_score)
            return self.forward(task, agent_act)
        if self.retry_strategy == "retry":
            self._log_max_retry(agent_act, trust_score)
        return observation

    def _log_warning(self, agent_act: AgentAct, trust_score: float) -> None:
        print("\n⚠️ LOW TRUST SCORE DETECTED!")
        print(f"   Action: {agent_act.name}")
        print(f"   Params: {agent_act.params}")
        print(f"   Score: {trust_score:.4f} (threshold: {self.trust_threshold})")
        print("   Continuing with low-trust result...\n")

    def _log_skip(self, agent_act: AgentAct, trust_score: float) -> None:
        print("\n🚫 SKIPPING LOW TRUST RESULT!")
        print(f"   Action: {agent_act.name}")
        print(f"   Params: {agent_act.params}")
        print(f"   Score: {trust_score:.4f} (threshold: {self.trust_threshold})")
        print("   Returning empty observation...\n")

    def _log_retry(self, agent_act: AgentAct, trust_score: float) -> None:
        current_retry = self.retry_count[f"{agent_act.name}_{agent_act.params}"]
        print("\n🔄 RETRYING LOW TRUST ACTION!")
        print(f"   Action: {agent_act.name}")
        print(f"   Params: {agent_act.params}")
        print(f"   Score: {trust_score:.4f} (threshold: {self.trust_threshold})")
        print(f"   Retry {current_retry}/{self.max_retries}...\n")

    def _log_max_retry(self, agent_act: AgentAct, trust_score: float) -> None:
        print("\n❌ MAX RETRIES EXCEEDED!")
        print(f"   Action: {agent_act.name}")
        print(f"   Params: {agent_act.params}")
        print(f"   Score: {trust_score:.4f} (threshold: {self.trust_threshold})")
        print("   Using last result despite low trust...\n")

    def _get_latest_trust_score(self) -> Optional[float]:
        if not os.path.exists(self.trust_score_file):
            return None
        try:
            with open(self.trust_score_file, "r", newline="") as csv_file:
                rows = list(csv.DictReader(csv_file))
        except Exception as error:  # pragma: no cover - defensive file handling
            print(f"⚠️ Error reading trust score: {error}")
            return None
        if not rows:
            return None
        value = rows[-1].get("trust_score", "")
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
