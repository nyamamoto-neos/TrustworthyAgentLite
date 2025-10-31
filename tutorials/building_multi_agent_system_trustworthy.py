"""Standalone script orchestrating the trustworthy multi-agent tutorial workflow."""

from __future__ import annotations

import argparse
import os
from typing import Dict, Tuple

from dotenv import load_dotenv

from agentlite.commons import TaskPackage
from agentlite.llm.LLMConfig import LLMConfig
from agentlite.llm.agent_llms import get_llm_backend

from trustworthy_workflow.agent_factories import (
    build_agents,
    build_manager,
    create_loggers,
    seed_manager,
    seed_plot_agent,
)
from trustworthy_workflow.TrustworthyAgentForWikipediaSearch import TrustworthyAgentForWikipediaSearch
from trustworthy_workflow.trust_analysis import (
    display_trust_score_report,
    extract_population,
    extract_population_values,
    load_trust_scores,
)
from trustworthy_workflow.action_drawFigure import DrawFigure


def build_llm(llm_name: str) -> Tuple[object, LLMConfig]:
    """Create the LLM backend defined by the environment."""
    config_dict = {"llm_name": llm_name, "temperature": 0.0}
    config = LLMConfig(config_dict)
    llm = get_llm_backend(config)
    return llm, config


def _load_env() -> None:
    """Load environment variables from .env file and print configuration summary."""
    load_dotenv(override=True)
    # Remove OpenAI API key to avoid conflicts with Cleanlab TLM
    os.environ.pop("OPENAI_API_KEY", None)

    # Print environment summary
    summary = {
        "LLM": os.environ.get("LLM", "Not set"),
        "CLEANLAB_TLM_API_KEY": "****" if os.environ.get("CLEANLAB_TLM_API_KEY") else "Not set",
        "OPENROUTER_API_KEY": "****" if os.environ.get("OPENROUTER_API_KEY") else "Not set",
    }
    for key, value in summary.items():
        print(f"{key}: {value}")


def _ensure_data_directory(path: str = "data") -> str:
    """Ensure the CSV output directory exists and return its path."""
    os.makedirs(path, exist_ok=True)
    return path


def _run_manager_task(manager, instruction: str) -> str:
    print("🔄 Starting multi-agent task...\n")
    task = TaskPackage(instruction=instruction, task_creator="User")
    response = manager(task)
    print("\n✅ Manager response:")
    print(response)
    return response


def _collect_population_data(search_agent: TrustworthyAgentForWikipediaSearch, csv_path: str) -> Tuple[int, int, float, float]:
    print("\n📊 TLM Trust Scores recorded:")
    trust_scores_map, _ = load_trust_scores(csv_path)
    print("\n📈 Extracting actual population values from search results...")
    california_pop, mexico_pop = extract_population_values(search_agent, extract_population)
    california_trust = trust_scores_map.get("{'query': 'Population of California'}", trust_scores_map.get("{'query': 'population of California'}", 0.5))
    mexico_trust = trust_scores_map.get("{'query': 'Population of Mexico'}", trust_scores_map.get("{'query': 'population of Mexico'}", 0.5))
    return california_pop, mexico_pop, california_trust, mexico_trust


def _render_final_chart(california_pop: int, mexico_pop: int, california_trust: float, mexico_trust: float) -> None:
    print("\n📊 Creating visualization with extracted values and trust scores...")
    draw_fig = DrawFigure()
    result = draw_fig(
        names=["California", "Mexico"],
        values=[california_pop, mexico_pop],
        trust_scores=[california_trust, mexico_trust],
    )
    print(f"\n✅ {result}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the trustworthy multi-agent population tutorial")
    parser.add_argument(
        "--manager-plot",
        action="store_true",
        help="Instruct the manager to drive the plot agent and skip the scripted fallback chart.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    _load_env()
    data_dir = _ensure_data_directory()
    trust_csv = os.path.join(data_dir, "trust_scores_demo.csv")
    agent_type = "react"  # available options: "react", "act", "zs" (alias for act), "zst" (alias for react)

    llm, _ = build_llm(os.environ.get("LLM", "gpt-4-32k"))
    tw_logger, agent_logger = create_loggers()
    search_agent, plot_agent = build_agents(
        llm,
        tw_logger,
        agent_logger,
        trust_score_file=trust_csv,
        agent_type=agent_type,
    )
    seed_plot_agent(plot_agent)
    manager = build_manager(llm, search_agent, plot_agent, tw_logger)
    seed_manager(manager, search_agent, plot_agent)

    print(f"🔧 Agent type configured as: {agent_type}")

    instruction = "Search Wikipedia for the population of California and Mexico. Report the numeric values you find."
    if args.manager_plot:
        instruction = (
            "Search Wikipedia for the population of California and Mexico. Report the numeric values you find, "
            "and plot a bar chart comparing the populations."
        )

    _run_manager_task(
        manager,
        instruction,
    )

    california_pop, mexico_pop, california_trust, mexico_trust = _collect_population_data(search_agent, trust_csv)
    if args.manager_plot:
        print("\nℹ️ Manager-driven plotting enabled; skipping fallback chart rendering.")
    else:
        _render_final_chart(california_pop, mexico_pop, california_trust, mexico_trust)
    display_trust_score_report(trust_csv)


if __name__ == "__main__":
    main()

