from typing import List, Dict, Any
import csv
import json
import os
from agentlite.utils import f1_score
from datetime import datetime
from dotenv import load_dotenv
from .BaseAgent import BaseAgent
from agentlite.commons import TaskPackage, AgentAct
from agentlite.actions import FinishAct
from agentlite.commons.AgentAct import ActObsChainType

# ----- Minimal TLM Setup -----------------
from cleanlab_tlm import TLM
# -----------------------------------------

load_dotenv()

class TrustworthyAgent(BaseAgent):
    """A TrustworthyAgent that tracks and scores LLM interactions for trustworthiness.

    This agent extends BaseAgent to add trustworthiness scoring functionality.
    It tracks all LLM interactions (prompts and responses) and saves them to CSV.

    Additional parameters:
        trust_score_file: str, optional
            Path to save trustworthiness scores.
        score_last_only: bool, optional
            Whether to only score the last Finish act.
    """

    def __init__(
        self,
        name: str,
        role: str,
        llm: Any,
        actions: List[Any] = [],
        trust_score_file: str = None,
        score_last_only: bool = False,
        skip_trust_actions: List[str] = None,
        tlm_quality: str = "base",
        **kwargs
    ):
        # ---------------- Logger Setup (Optional) ----------------
        from agentlite.logging.terminal_logger import TrustworthyAgentLogger
        llm_model_name = getattr(llm, "llm_name", "unk")
        agent_arch = kwargs.get("agent_arch", "unk")
        logger = kwargs.pop('logger', None)
        if logger is None:
            log_file_name = f"trustworthy_{agent_arch}_{llm_model_name}.log"
            logger = TrustworthyAgentLogger(
                log_file_name=log_file_name,
                FLAG_PRINT=True
            )
        kwargs['logger'] = logger
        # ---------------------------------------------------

        # ---------------- BaseAgent ----------------
        super().__init__(name=name, role=role, llm=llm, actions=actions, **kwargs)
        self.max_exec_steps = 20 # Set max steps for agent (increased from 10 to allow completing complex tasks)
        # ---------------------------------------------------

        self.score_last_only = score_last_only         # Optional: Whether to score only final Finish act

        # Actions for which we should NOT call TLM (e.g., local plotting actions)
        if skip_trust_actions is None:
            skip_trust_actions = ["DrawFigure"]
        self.skip_trust_actions = set(skip_trust_actions)

        # ---------------- Minimal TLM Setup ----------------
        self.tlm = TLM()
        # ---------------------------------------------------

        # ---------------- Load TLM Pricing Configuration ----------------
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'tlm_pricing.json')
        try:
            with open(config_path, 'r') as f:
                self.pricing_config = json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"TLM pricing config not found at {config_path}, using default base pricing")
            self.pricing_config = {
                "pricing": {
                    "base": {"input_per_1m_tokens": 0.50, "output_per_1m_tokens": 1.70}
                },
                "default_quality": "base"
            }

        self.tlm_quality = tlm_quality
        if tlm_quality not in self.pricing_config.get("pricing", {}):
            self.logger.warning(f"Unknown TLM quality preset '{tlm_quality}', falling back to 'base'")
            self.tlm_quality = self.pricing_config.get("default_quality", "base")

        self.pricing_info = self.pricing_config["pricing"][self.tlm_quality]
        self.logger.info(f"Using TLM quality preset: {self.tlm_quality} "
                        f"(Input: ${self.pricing_info['input_per_1m_tokens']}/1M, "
                        f"Output: ${self.pricing_info['output_per_1m_tokens']}/1M)")

        # Initialize token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        # ---------------------------------------------------

        # ---------------- Save to CSV (Optional) ----------------
        if trust_score_file is None:
            trust_score_file = f"data/trustworthy_{agent_arch}_{llm_model_name}.csv"
        self.trust_score_file = trust_score_file
        try:
            with open(self.trust_score_file, 'x', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'task_id',
                    'step',
                    'question',
                    'answer',
                    'prompt',
                    'raw_action',
                    'finish_response',
                    'trust_score',
                    'f1',
                    'action_name',
                    'action_params',
                    'input_tokens',
                    'output_tokens',
                    'cost_usd'
                ])
        except FileExistsError:
            pass  # File already exists
        # ---------------------------------------------------

    def __next_act__(self, task: TaskPackage, action_chain: ActObsChainType) -> AgentAct:
        """Override __next_act__ to track and score LLM interactions.

        Args:
            task: The current task being executed
            action_chain: History of actions and observations

        Returns:
            AgentAct: The next action to take
        """
        # ---------------- BaseAgent ----------------
        action_prompt = self.prompt_gen.action_prompt(
            task=task,
            actions=self.actions,
            action_chain=action_chain,
        )
        self.logger.get_prompt(action_prompt)
        raw_action = self.llm_layer(action_prompt)
        if raw_action.startswith('Action: '):
            raw_action = raw_action[8:]
        self.logger.get_llm_output(raw_action)
        agent_act = self.__action_parser__(raw_action)
        # ---------------------------------------------------

        # ---------------- Minimal TLM Setup ----------------
        trust_score = None
        input_tokens = 0
        output_tokens = 0
        cost = 0.0

        # Skip TLM scoring for specified local actions (e.g., DrawFigure).
        # Be tolerant: skip when the action name contains the skip token (covers cases
        # where parsing failed and agent_act.name equals the full raw_action string),
        # and when the raw_action contains the action call pattern.
        should_skip = False
        for a in self.skip_trust_actions:
            try:
                if a in (agent_act.name or ""):
                    should_skip = True
                    break
                if isinstance(raw_action, str) and (f"{a}[" in raw_action or raw_action.strip().startswith(a)):
                    should_skip = True
                    break
            except Exception:
                # be defensive; if any unexpected types occur, avoid scoring
                should_skip = True
                break

        if should_skip:
            trust_score = None
        else:
            if not self.score_last_only or agent_act.name == FinishAct.action_name:
                # Get trustworthiness score and token usage from TLM
                tlm_response = self.tlm.get_trustworthiness_score(action_prompt, raw_action)
                trust_score = tlm_response["trustworthiness_score"]

                # Estimate token counts (TLM may provide these in the response)
                # If not provided by API, estimate: ~4 chars per token
                if "input_tokens" in tlm_response:
                    input_tokens = tlm_response["input_tokens"]
                else:
                    input_tokens = len(action_prompt) // 4

                if "output_tokens" in tlm_response:
                    output_tokens = tlm_response["output_tokens"]
                else:
                    output_tokens = len(str(raw_action)) // 4

                # Calculate cost
                cost = (
                    (input_tokens / 1_000_000) * self.pricing_info['input_per_1m_tokens'] +
                    (output_tokens / 1_000_000) * self.pricing_info['output_per_1m_tokens']
                )

                # Update cumulative tracking
                self.total_input_tokens += input_tokens
                self.total_output_tokens += output_tokens
                self.total_cost += cost

                # Log token usage
                self.logger.info(
                    f"TLM Token Usage - Input: {input_tokens:,}, Output: {output_tokens:,}, "
                    f"Cost: ${cost:.6f} (Total: ${self.total_cost:.6f})"
                )
        # ---------------------------------------------------

        # ---------------- Get F1 score & Response (Optional) ----------------
        f1 = None
        response = None
        if agent_act.name == FinishAct.action_name:
            response = FinishAct(**agent_act.params)
            f1, _, _ = f1_score(response, task.ground_truth)

        # ---------------- Logging & Saving (Optional) ----------------
        if trust_score is not None:
            self.logger.log_action_trust(
                action=agent_act,
                trust_score=trust_score,
                agent_name=self.name,
                step_idx=len(action_chain)
            )

            self.__record_interaction__(
                task_id=task.task_id,
                step=len(action_chain),
                question=task.instruction,
                answer=task.ground_truth,
                prompt=action_prompt,
                raw_action=raw_action,
                finish_response=response,
                trust_score=trust_score,
                f1=f1,
                action_name=agent_act.name,
                action_params=agent_act.params,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost
            )
        # ---------------------------------------------------
        return agent_act

    # ---------------- Save to CSV (Optional) ----------------
    def __record_interaction__(self, **kwargs):
        """Record an LLM interaction to the trust score CSV file.

        Args:
            **kwargs: Interaction details to record
        """
        try:
            with open(self.trust_score_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    kwargs.get('task_id', ''),
                    kwargs.get('step', 0),
                    kwargs.get('question', ''),
                    kwargs.get('answer', ''),
                    kwargs.get('prompt', ''),
                    kwargs.get('raw_action', ''),
                    kwargs.get('finish_response', None),
                    kwargs.get('trust_score', None),
                    kwargs.get('f1', None),
                    kwargs.get('action_name', ''),
                    str(kwargs.get('action_params', {})),
                    kwargs.get('input_tokens', 0),
                    kwargs.get('output_tokens', 0),
                    kwargs.get('cost_usd', 0.0)
                ])
        except Exception as e:
            self.logger.error(f"Failed to record trust score: {str(e)}")

    def get_token_usage_summary(self) -> Dict[str, Any]:
        """Get summary of token usage and costs for this agent.

        Returns:
            Dict containing total input/output tokens and cost
        """
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost_usd": self.total_cost,
            "quality_preset": self.tlm_quality,
            "pricing": self.pricing_info
        }