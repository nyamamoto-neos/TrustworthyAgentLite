"""Factories for agents, loggers, and examples used in the tutorial."""

from __future__ import annotations

from typing import Tuple

from agentlite.actions import ThinkAct, FinishAct
from agentlite.actions.InnerActions import INNER_ACT_KEY
from agentlite.agents import BaseAgent, ManagerAgent
from agentlite.agents.agent_utils import AGENT_CALL_ARG_KEY
from agentlite.commons import AgentAct, TaskPackage
from agentlite.llm.LLMConfig import LLMConfig
from agentlite.llm.agent_llms import get_llm_backend
from agentlite.logging.terminal_logger import AgentLogger, TrustworthyAgentLogger

from .TrustworthyAgentForWikipediaSearch import TrustworthyAgentForWikipediaSearch
from .action_drawFigure import DrawFigure
from .action_wikipediaSearch import WikipediaSearch


def build_llm(llm_name: str) -> Tuple[object, LLMConfig]:
    """Create the LLM backend defined by the environment."""
    config_dict = {"llm_name": llm_name, "temperature": 0.0}
    config = LLMConfig(config_dict)
    llm = get_llm_backend(config)
    return llm, config


def create_loggers() -> Tuple[TrustworthyAgentLogger, AgentLogger]:
    """Instantiate loggers for trustworthy and non-trustworthy agents."""
    tw_logger = TrustworthyAgentLogger(log_file_name="trustworthy_demo.log", FLAG_PRINT=True, PROMPT_DEBUG_FLAG=False)
    agent_logger = AgentLogger(log_file_name="plot_agent.log", FLAG_PRINT=True, PROMPT_DEBUG_FLAG=False)
    return tw_logger, agent_logger


def build_agents(
    llm,
    tw_logger,
    agent_logger,
    trust_score_file: str,
    agent_type: str = "react",
) -> Tuple[TrustworthyAgentForWikipediaSearch, BaseAgent]:
    """Create the search and plot agents used by the tutorial."""
    search_agent_info = {
        "name": "search_agent",
        "role": "you can search wikipedia to get the information. When reporting population data, provide the actual numeric values (e.g., 40000000 for 40 million).",
    }
    plot_agent_info = {
        "name": "plot_agent",
        "role": "you can plot a bar figure based on the input names and values.",
    }
    agent_arch = {
        "zs": "act",
        "zst": "react",
    }.get(agent_type, agent_type)

    search_agent = TrustworthyAgentForWikipediaSearch(
        name=search_agent_info["name"],
        role=search_agent_info["role"],
        llm=llm,
        actions=[WikipediaSearch()],
        trust_score_file=trust_score_file,
        agent_arch=agent_arch,
        logger=tw_logger,
        trust_threshold=0.6,
        max_retries=1,
        retry_strategy="skip",
    )
    plot_agent = BaseAgent(
        name=plot_agent_info["name"],
        role=plot_agent_info["role"],
        llm=llm,
        actions=[DrawFigure()],
        logger=agent_logger,
    )
    return search_agent, plot_agent


def seed_plot_agent(plot_agent: BaseAgent) -> None:
    """Provide an example sequence so the plot agent knows how to call DrawFigure."""
    example_task = TaskPackage(instruction="plot a population figure for CityA and CityB")
    think_act = AgentAct(
        name=ThinkAct.action_name,
        params={INNER_ACT_KEY: "I can call DrawFigure with the supplied city names and values."},
    )
    draw_act = AgentAct(
        name=DrawFigure().action_name,
        params={"names": ["CityA", "CityB"], "values": [112.3, 332.4]},
    )
    finish_act = AgentAct(name=FinishAct.action_name, params={INNER_ACT_KEY: "Done!"})
    chain = [
        (think_act, "OK"),
        (draw_act, "Successfully draw the bar figure!"),
        (finish_act, "Task Completed."),
    ]
    plot_agent.add_example(task=example_task, action_chain=chain)


def build_manager(llm, search_agent: TrustworthyAgentForWikipediaSearch, plot_agent: BaseAgent, tw_logger) -> ManagerAgent:
    """Create the manager agent coordinating search and visualization."""
    manager_role = "coordinate the search and plot agents to gather population data and produce a bar chart."
    team = [search_agent, plot_agent]
    return ManagerAgent(name="manager_agent", role=manager_role, llm=llm, TeamAgents=team, logger=tw_logger)


def seed_manager(manager: ManagerAgent, search_agent: BaseAgent, plot_agent: BaseAgent) -> None:
    """Provide a guided example for the manager to follow."""
    example_task = TaskPackage(instruction="plot the bar figure of CityA and CityB population.")
    think_start = AgentAct(
        name=ThinkAct.action_name,
        params={
            INNER_ACT_KEY: "I should ask search_agent for both populations, then send the values to plot_agent to draw the chart.",
        },
    )
    search_call = AgentAct(
        name=search_agent.name,
        params={AGENT_CALL_ARG_KEY: "Can you find the population of CityA and CityB?"},
    )
    think_delegate = AgentAct(
        name=ThinkAct.action_name,
        params={INNER_ACT_KEY: "With both populations collected, I should ask plot_agent to render the figure."},
    )
    plot_call = AgentAct(
        name=plot_agent.name,
        params={AGENT_CALL_ARG_KEY: "Draw a bar figure for CityA with 112.3 million people and CityB with 332.4 million people."},
    )
    finish_call = AgentAct(
        name=FinishAct.action_name,
        params={INNER_ACT_KEY: "I retrieved the populations and plotted the bar chart."},
    )
    chain = [
        (think_start, "OK"),
        (search_call, "The population of CityA is approximately 112.3 million and CityB is approximately 332.4 million."),
        (think_delegate, "OK"),
        (plot_call, "Done!"),
        (finish_call, "Task Completed."),
    ]
    manager.add_example(task=example_task, action_chain=chain)
