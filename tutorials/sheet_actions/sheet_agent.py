"""
Sheet Manager Agent
Intelligent agent for managing Google Sheets
"""

from typing import List
from agentlite.actions import BaseAction, ThinkAct, FinishAct
from agentlite.agents import BaseAgent
from agentlite.llm.agent_llms import BaseLLM
from agentlite.logging.terminal_logger import AgentLogger
from agentlite.commons import AgentAct, TaskPackage
from agentlite.actions.InnerActions import INNER_ACT_KEY

from .sheet_actions import (
    OpenSpreadsheet,
    OpenSheet,
    GetAllValues,
    GetCellValue,
    GetRangeValues,
    UpdateCell,
    UpdateRange,
    InsertRows,
    FindCell,
    SortSheetByColumn,
    GetSheetSummary,
    DeleteSheet,
    FreezeData,
    GetA1Annotation,
    InsertColumns,
    DeleteBatchData,
    UpdateCellByFormula,
    SortSheetByCol,
    MergeCells,
    UpdateNote,
    GetValueByFormula,
    FilterCells,
    GetNote,
)


class SheetManagerAgent(BaseAgent):
    """Agent for managing Google Sheets with natural language"""

    def __init__(self, llm: BaseLLM, gspread_client, prompt_debug: bool = False):
        name = "SheetManager"
        role = """You are a Google Sheets management assistant that helps users work with spreadsheets.
        You can open spreadsheets, read data, update cells, insert rows, search for values, and sort data.
        Always think step-by-step and use the available actions to complete tasks efficiently."""

        # Setup logger
        agent_logger = AgentLogger(PROMPT_DEBUG_FLAG=prompt_debug)

        # Define available actions (pass gspread client to OpenSpreadsheet)
        actions = [
            OpenSpreadsheet(gspread_client),
            OpenSheet(),
            DeleteSheet(),
            FreezeData(),
            GetA1Annotation(),
            InsertColumns(),
            InsertRows(),
            DeleteBatchData(),
            UpdateCell(),
            UpdateCellByFormula(),
            UpdateRange(),
            SortSheetByCol(),
            MergeCells(),
            UpdateNote(),
            GetAllValues(),
            GetRangeValues(),
            GetCellValue(),
            GetValueByFormula(),
            FilterCells(),
            GetNote(),
            GetSheetSummary(),
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
        """Add an example workflow for updating spreadsheet data"""
        # Example: Find and update a value in a spreadsheet
        task = "In the Sales Data spreadsheet, find the cell containing 'Q1 Revenue' and update the adjacent cell to 100000"
        task_pack = TaskPackage(instruction=task)

        # Step 1: Think about the approach
        act_1 = AgentAct(
            name=ThinkAct.action_name,
            params={INNER_ACT_KEY: "I need to first open the Sales Data spreadsheet, then find the Q1 Revenue cell, and update the adjacent cell."}
        )
        obs_1 = "OK"

        # Step 2: Open spreadsheet
        act_2 = AgentAct(
            name="open_spreadsheet",
            params={"name_or_id": "Sales Data"}
        )
        obs_2 = "Opened spreadsheet 'Sales Data'. Available sheets: ['Sheet1', 'Summary']"

        # Step 3: Think about which sheet to use
        act_3 = AgentAct(
            name=ThinkAct.action_name,
            params={INNER_ACT_KEY: "I'll open Sheet1 to search for the Q1 Revenue cell."}
        )
        obs_3 = "OK"

        # Step 4: Open sheet
        act_4 = AgentAct(
            name="open_sheet",
            params={"sheet_name": "Sheet1"}
        )
        obs_4 = "Opened sheet 'Sheet1' (100 rows × 26 columns)"

        # Step 5: Find the cell
        act_5 = AgentAct(
            name="find_cell",
            params={"query": "Q1 Revenue"}
        )
        obs_5 = "Found 'Q1 Revenue' at A5 (row 5, col 1)"

        # Step 6: Think about updating adjacent cell
        act_6 = AgentAct(
            name=ThinkAct.action_name,
            params={INNER_ACT_KEY: "Q1 Revenue is at A5, so the adjacent cell is B5. I'll update B5 to 100000."}
        )
        obs_6 = "OK"

        # Step 7: Update the cell
        act_7 = AgentAct(
            name="update_cell",
            params={"cell": "B5", "value": "100000"}
        )
        obs_7 = "Cell B5 updated to '100000'"

        # Step 8: Finish
        act_8 = AgentAct(
            name=FinishAct.action_name,
            params={INNER_ACT_KEY: "I successfully found 'Q1 Revenue' at cell A5 and updated the adjacent cell B5 to 100000."}
        )
        obs_8 = "Task Completed."

        # Add the example to the agent
        act_obs = [
            (act_1, obs_1),
            (act_2, obs_2),
            (act_3, obs_3),
            (act_4, obs_4),
            (act_5, obs_5),
            (act_6, obs_6),
            (act_7, obs_7),
            (act_8, obs_8),
        ]
        self.add_example(task=task_pack, action_chain=act_obs)
