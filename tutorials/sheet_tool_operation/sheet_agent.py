"""
Sheet Manager Agent
Intelligent agent for managing Google Sheets
"""

from typing import List
from agentlite.actions import BaseAction, ThinkAct, FinishAct, PlanAct
from agentlite.agents import BaseAgent
from agentlite.agents.TrustworthyAgent import TrustworthyAgent
from agentlite.llm.agent_llms import BaseLLM
from agentlite.logging.terminal_logger import AgentLogger, TrustworthyAgentLogger
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


class SheetManagerAgent(TrustworthyAgent):
    """Agent for managing Google Sheets with natural language"""

    def __init__(self, llm: BaseLLM, gspread_client, agent_arch: str = "react", PROMPT_DEBUG_FLAG: bool = False):
        name = "SheetManager"
        role = "Manage Google Sheets by opening spreadsheets, reading/writing data, updating cells, and organizing information."
        constraint = "Only use available sheet actions. Verify spreadsheet is open before performing operations."
        instruction = "You are an intelligent Google Sheets agent. Follow your [Role] and [Action_Doc] to take actions. Decompose tasks into executable actions. Finish when the task is complete. Take one action per generation. DO NOT repeat actions."

        self.agent_arch = agent_arch
        self.gspread_client = gspread_client

        # Determine reasoning type based on agent architecture
        if agent_arch in ["zs"]:
            reasoning_type = "act"
        elif agent_arch in ["zst"]:
            reasoning_type = "react"
        else:
            reasoning_type = agent_arch

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
            FindCell(),
            SortSheetByColumn(),
        ]

        super().__init__(
            name=name,
            role=role,
            llm=llm,
            actions=actions,
            reasoning_type=reasoning_type,
            constraint=constraint,
            instruction=instruction,
            logger=TrustworthyAgentLogger(PROMPT_DEBUG_FLAG=PROMPT_DEBUG_FLAG),
            agent_arch=agent_arch
        )

        # Build examples based on architecture
        self.__build_examples__()

    def __build_examples__(self):
        """Build examples based on agent architecture"""
        if self.agent_arch == "react":
            self.__build_react_examples__()
        elif self.agent_arch == "act":
            self.__build_act_examples__()
        elif self.agent_arch == "planact":
            self.__build_planact_examples__()
        elif self.agent_arch == "planreact":
            self.__build_planreact_examples__()

    def __build_react_examples__(self):
        """Construct ReAct examples with Think-Act pattern"""
        # Example: Open spreadsheet and get summary
        task = "Open the spreadsheet named 'Test Sheet' and give me a summary of Sheet1"
        task_pack = TaskPackage(instruction=task)

        # Step 1: Think about approach
        act_1 = AgentAct(
            name=ThinkAct.action_name,
            params={INNER_ACT_KEY: "I need to first open the spreadsheet 'Test Sheet', then open Sheet1, and get its summary."}
        )
        obs_1 = "OK"

        # Step 2: Open spreadsheet
        act_2 = AgentAct(
            name="open_spreadsheet",
            params={"spreadsheet_name_or_id": "Test Sheet"}
        )
        obs_2 = "Opened spreadsheet 'Test Sheet'. Available sheets: ['Sheet1', 'Sheet2', 'Summary']"

        # Step 3: Think about next action
        act_3 = AgentAct(
            name=ThinkAct.action_name,
            params={INNER_ACT_KEY: "I need to open Sheet1 to get its summary."}
        )
        obs_3 = "OK"

        # Step 4: Open sheet
        act_4 = AgentAct(
            name="open_sheet",
            params={"sheet_name": "Sheet1"}
        )
        obs_4 = "Opened sheet 'Sheet1' (100 rows × 10 columns)"

        # Step 5: Think before getting summary
        act_5 = AgentAct(
            name=ThinkAct.action_name,
            params={INNER_ACT_KEY: "Now I can get the summary of this sheet."}
        )
        obs_5 = "OK"

        # Step 6: Get summary
        act_6 = AgentAct(
            name="get_sheet_summary",
            params={"dummy": ""}
        )
        obs_6 = """Sheet: Sheet1
Dimensions: 100 rows × 10 columns

First 3 rows:
Row 1: ['Product', 'Sales', 'Price', 'Quantity']
Row 2: ['Apple', '1000', '2.5', '400']
Row 3: ['Orange', '800', '3.0', '267']"""

        # Step 7: Finish
        act_7 = AgentAct(
            name=FinishAct.action_name,
            params={INNER_ACT_KEY: "I successfully opened 'Test Sheet' and retrieved a summary of Sheet1. It has 100 rows and 10 columns with product sales data."}
        )
        obs_7 = "Task Completed."

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

        # Example 2: Read a single cell value (sheet already open)
        task2 = "What is the value in cell A1?"
        task_pack2 = TaskPackage(instruction=task2)

        # Step 1: Think about approach
        act2_1 = AgentAct(
            name=ThinkAct.action_name,
            params={INNER_ACT_KEY: "A sheet is already open. I just need to read cell A1 and report the value."}
        )
        obs2_1 = "OK"

        # Step 2: Get cell value
        act2_2 = AgentAct(
            name="get_cell_value",
            params={"cell": "A1"}
        )
        obs2_2 = "Product"

        # Step 3: Think about finishing
        act2_3 = AgentAct(
            name=ThinkAct.action_name,
            params={INNER_ACT_KEY: "I successfully retrieved the value. Cell A1 contains 'Product'. I should finish now."}
        )
        obs2_3 = "OK"

        # Step 4: Finish
        act2_4 = AgentAct(
            name=FinishAct.action_name,
            params={INNER_ACT_KEY: "The value in cell A1 is 'Product'."}
        )
        obs2_4 = "Task Completed."

        act_obs2 = [
            (act2_1, obs2_1),
            (act2_2, obs2_2),
            (act2_3, obs2_3),
            (act2_4, obs2_4),
        ]
        self.add_example(task=task_pack2, action_chain=act_obs2)

    def __build_act_examples__(self):
        """Construct Act examples without explicit Think steps"""
        # Example: Open spreadsheet and get summary
        task = "Open the spreadsheet named 'Test Sheet' and give me a summary of Sheet1"
        task_pack = TaskPackage(instruction=task)

        # Step 1: Open spreadsheet
        act_1 = AgentAct(
            name="open_spreadsheet",
            params={"spreadsheet_name_or_id": "Test Sheet"}
        )
        obs_1 = "Opened spreadsheet 'Test Sheet'. Available sheets: ['Sheet1', 'Sheet2', 'Summary']"

        # Step 2: Open sheet
        act_2 = AgentAct(
            name="open_sheet",
            params={"sheet_name": "Sheet1"}
        )
        obs_2 = "Opened sheet 'Sheet1' (100 rows × 10 columns)"

        # Step 3: Get summary
        act_3 = AgentAct(
            name="get_sheet_summary",
            params={"dummy": ""}
        )
        obs_3 = """Sheet: Sheet1
Dimensions: 100 rows × 10 columns

First 3 rows:
Row 1: ['Product', 'Sales', 'Price', 'Quantity']
Row 2: ['Apple', '1000', '2.5', '400']
Row 3: ['Orange', '800', '3.0', '267']"""

        # Step 4: Finish
        act_4 = AgentAct(
            name=FinishAct.action_name,
            params={INNER_ACT_KEY: "I successfully opened 'Test Sheet' and retrieved a summary of Sheet1. It has 100 rows and 10 columns with product sales data."}
        )
        obs_4 = "Task Completed."

        act_obs = [
            (act_1, obs_1),
            (act_2, obs_2),
            (act_3, obs_3),
            (act_4, obs_4),
        ]
        self.add_example(task=task_pack, action_chain=act_obs)

        # Example 2: Read a single cell value (sheet already open)
        task2 = "What is the value in cell A1?"
        task_pack2 = TaskPackage(instruction=task2)

        # Step 1: Get cell value
        act2_1 = AgentAct(
            name="get_cell_value",
            params={"cell": "A1"}
        )
        obs2_1 = "Product"

        # Step 2: Finish
        act2_2 = AgentAct(
            name=FinishAct.action_name,
            params={INNER_ACT_KEY: "The value in cell A1 is 'Product'."}
        )
        obs2_2 = "Task Completed."

        act_obs2 = [
            (act2_1, obs2_1),
            (act2_2, obs2_2),
        ]
        self.add_example(task=task_pack2, action_chain=act_obs2)

    def __build_planact_examples__(self):
        """Construct Plan-Act examples"""
        # Example: Open spreadsheet and get summary
        task = "Open the spreadsheet named 'Test Sheet' and give me a summary of Sheet1"
        task_pack = TaskPackage(instruction=task)

        # Step 1: Plan
        act_1 = AgentAct(
            name=PlanAct.action_name,
            params={INNER_ACT_KEY: "I will open the spreadsheet 'Test Sheet', then open Sheet1, and finally get its summary."}
        )
        obs_1 = "OK"

        # Step 2: Open spreadsheet
        act_2 = AgentAct(
            name="open_spreadsheet",
            params={"spreadsheet_name_or_id": "Test Sheet"}
        )
        obs_2 = "Opened spreadsheet 'Test Sheet'. Available sheets: ['Sheet1', 'Sheet2', 'Summary']"

        # Step 3: Open sheet
        act_3 = AgentAct(
            name="open_sheet",
            params={"sheet_name": "Sheet1"}
        )
        obs_3 = "Opened sheet 'Sheet1' (100 rows × 10 columns)"

        # Step 4: Get summary
        act_4 = AgentAct(
            name="get_sheet_summary",
            params={"dummy": ""}
        )
        obs_4 = """Sheet: Sheet1
Dimensions: 100 rows × 10 columns

First 3 rows:
Row 1: ['Product', 'Sales', 'Price', 'Quantity']
Row 2: ['Apple', '1000', '2.5', '400']
Row 3: ['Orange', '800', '3.0', '267']"""

        # Step 5: Finish
        act_5 = AgentAct(
            name=FinishAct.action_name,
            params={INNER_ACT_KEY: "I successfully opened 'Test Sheet' and retrieved a summary of Sheet1. It has 100 rows and 10 columns with product sales data."}
        )
        obs_5 = "Task Completed."

        act_obs = [
            (act_1, obs_1),
            (act_2, obs_2),
            (act_3, obs_3),
            (act_4, obs_4),
            (act_5, obs_5),
        ]
        self.add_example(task=task_pack, action_chain=act_obs)

    def __build_planreact_examples__(self):
        """Construct Plan-ReAct examples"""
        # Example: Open spreadsheet and get summary
        task = "Open the spreadsheet named 'Test Sheet' and give me a summary of Sheet1"
        task_pack = TaskPackage(instruction=task)

        # Step 1: Plan
        act_1 = AgentAct(
            name=PlanAct.action_name,
            params={INNER_ACT_KEY: "I will open the spreadsheet 'Test Sheet', then open Sheet1, and finally get its summary."}
        )
        obs_1 = "OK"

        # Step 2: Open spreadsheet
        act_2 = AgentAct(
            name="open_spreadsheet",
            params={"spreadsheet_name_or_id": "Test Sheet"}
        )
        obs_2 = "Opened spreadsheet 'Test Sheet'. Available sheets: ['Sheet1', 'Sheet2', 'Summary']"

        # Step 3: Think about next action
        act_3 = AgentAct(
            name=ThinkAct.action_name,
            params={INNER_ACT_KEY: "I need to open Sheet1 to get its summary."}
        )
        obs_3 = "OK"

        # Step 4: Open sheet
        act_4 = AgentAct(
            name="open_sheet",
            params={"sheet_name": "Sheet1"}
        )
        obs_4 = "Opened sheet 'Sheet1' (100 rows × 10 columns)"

        # Step 5: Think before getting summary
        act_5 = AgentAct(
            name=ThinkAct.action_name,
            params={INNER_ACT_KEY: "Now I can get the summary of this sheet."}
        )
        obs_5 = "OK"

        # Step 6: Get summary
        act_6 = AgentAct(
            name="get_sheet_summary",
            params={"dummy": ""}
        )
        obs_6 = """Sheet: Sheet1
Dimensions: 100 rows × 10 columns

First 3 rows:
Row 1: ['Product', 'Sales', 'Price', 'Quantity']
Row 2: ['Apple', '1000', '2.5', '400']
Row 3: ['Orange', '800', '3.0', '267']"""

        # Step 7: Finish
        act_7 = AgentAct(
            name=FinishAct.action_name,
            params={INNER_ACT_KEY: "I successfully opened 'Test Sheet' and retrieved a summary of Sheet1. It has 100 rows and 10 columns with product sales data."}
        )
        obs_7 = "Task Completed."

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
