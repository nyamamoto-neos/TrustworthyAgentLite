"""
Todo Manager Agent
Intelligent agent for managing Todoist tasks
"""

from typing import List
from agentlite.actions import BaseAction, ThinkAct, FinishAct
from agentlite.agents import BaseAgent
from agentlite.llm.agent_llms import BaseLLM
from agentlite.logging.terminal_logger import AgentLogger
from agentlite.commons import AgentAct, TaskPackage
from agentlite.actions.InnerActions import INNER_ACT_KEY

from .todo_actions import (
    GetCurrentDate,
    GetUserCurrentLocation,
    GetProjects,
    UpdateProject,
    GetTasks,
    GetTaskDescription,
    GetTaskDuration,
    CompleteTask,
    UpdateTaskDueDate,
    DeleteTask,
)


class TodoManagerAgent(BaseAgent):
    """Agent for managing Todoist tasks with natural language"""

    def __init__(self, llm: BaseLLM, prompt_debug: bool = False):
        name = "TodoManager"
        role = """You are a task management assistant that helps users manage their Todoist tasks.
        You can list projects, view tasks, complete tasks, update due dates, and delete tasks.
        Always think step-by-step and use the available actions to help users."""

        # Setup logger
        agent_logger = AgentLogger(PROMPT_DEBUG_FLAG=prompt_debug)

        # Define available actions
        actions = [
            GetCurrentDate(),
            GetUserCurrentLocation(),
            GetProjects(),
            UpdateProject(),
            GetTasks(),
            GetTaskDescription(),
            GetTaskDuration(),
            CompleteTask(),
            UpdateTaskDueDate(),
            DeleteTask(),
            ThinkAct,
        ]

        super().__init__(
            name=name,
            role=role,
            llm=llm,
            actions=actions,
            logger=agent_logger,
        )

        # Add example to guide the agent
        self._build_example()

    def _build_example(self):
        """Add an example task completion flow"""
        # Example: Complete a task in a project
        task = "Complete the first task in the Work project"
        task_pack = TaskPackage(instruction=task)

        # Step 1: Think about what to do
        act_1 = AgentAct(
            name=ThinkAct.action_name,
            params={INNER_ACT_KEY: "I need to first get all projects to find the Work project ID"}
        )
        obs_1 = "OK"

        # Step 2: Get projects
        act_2 = AgentAct(
            name="get_projects",
            params={}
        )
        obs_2 = '[{"id": "123456", "name": "Work", "is_favorite": true}]'

        # Step 3: Think about next step
        act_3 = AgentAct(
            name=ThinkAct.action_name,
            params={INNER_ACT_KEY: "Found Work project with ID 123456. Now I need to get tasks in this project."}
        )
        obs_3 = "OK"

        # Step 4: Get tasks
        act_4 = AgentAct(
            name="get_tasks",
            params={"project_id": "123456"}
        )
        obs_4 = '[{"id": "789012", "content": "Prepare presentation", "due_date": "2024-01-15"}]'

        # Step 5: Think about completing the task
        act_5 = AgentAct(
            name=ThinkAct.action_name,
            params={INNER_ACT_KEY: "Found task 'Prepare presentation' with ID 789012. I'll complete it."}
        )
        obs_5 = "OK"

        # Step 6: Complete the task
        act_6 = AgentAct(
            name="complete_task",
            params={"task_id": "789012"}
        )
        obs_6 = "Task 789012 completed successfully"

        # Step 7: Finish
        act_7 = AgentAct(
            name=FinishAct.action_name,
            params={INNER_ACT_KEY: "I have successfully completed the first task 'Prepare presentation' in the Work project."}
        )
        obs_7 = "Task Completed."

        # Add the example to the agent
        act_obs = [
            (act_1, obs_1),
            (act_2, obs_2),
            (act_3, obs_3),
            (act_4, obs_4),
            (act_5, obs_5),
            (act_6, obs_6),
            (act_7, obs_7),
        ]
        self.add_example(task=task_pack, action_chain=act_obs)
