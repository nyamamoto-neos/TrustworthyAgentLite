#!/usr/bin/env python
"""
Google Sheets Manager Agent Tutorial
=====================================

This script demonstrates how to build a practical agent that manages Google Sheets
using the Google Sheets API and AgentLite framework.

Prerequisites:
1. Create a Google Cloud Project
2. Enable Google Sheets API
3. Create a Service Account and download credentials JSON
4. Set GOOGLE_SHEETS_CREDENTIALS environment variable
5. Share your test spreadsheet with the service account email

See: https://docs.gspread.org/en/latest/oauth2.html#for-bots-using-service-account

Usage:
    conda activate TLM
    cd /Users/ymmtny/Documents/GitHub/AgentLiteTLM/tutorials
    python sheet_manager.py
"""

import os
import sys

from dotenv import load_dotenv

from agentlite.commons import TaskPackage
from agentlite.llm.LLMConfig import LLMConfig
from agentlite.llm.agent_llms import get_llm_backend
from sheet_tool_operation import get_gspread_client
from sheet_tool_operation.sheet_agent import SheetManagerAgent


def verify_environment():
    """Verify that we're running in the correct conda environment."""
    conda_env = os.environ.get("CONDA_DEFAULT_ENV", "")
    if conda_env != "TLM":
        print(f"⚠️  Warning: Not running in TLM conda environment (current: {conda_env or 'none'})")
        print("   To activate: conda activate TLM")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        print(f"✅ Running in conda environment: {conda_env}")


def setup_environment():
    """Load environment variables and return credentials file path."""
    # Load environment variables from parent directory (override=True forces reload)
    load_dotenv(dotenv_path="../.env", override=True)

    # Print environment summary
    print("\n📋 Environment Configuration:")
    summary = {
        "LLM": os.environ.get("LLM", "Not set"),
        "OPENROUTER_API_KEY": "****" if os.environ.get("OPENROUTER_API_KEY") else "Not set",
        "GOOGLE_SHEETS_CREDENTIALS": os.environ.get("GOOGLE_SHEETS_CREDENTIALS", "Not set (using default)"),
    }
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # Remove OpenAI API key to avoid conflicts
    os.environ.pop("OPENAI_API_KEY", None)

    # Path to your service account credentials
    credentials_file = os.path.expanduser(
        os.getenv(
            "GOOGLE_SHEETS_CREDENTIALS",
            "~/Documents/GitHub/nha-sys-sandbox/key/nha-proto-spredsheet-bd3cf7f6603e.json"
        )
    )

    # Check if credentials file exists
    if not os.path.exists(credentials_file):
        print("\n⚠️  Warning: credentials.json not found")
        print(f"Path checked: {credentials_file}")
        print("Please download your service account credentials from Google Cloud Console")
        raise FileNotFoundError(f"Credentials file not found: {credentials_file}")

    print(f"\n✅ Google Sheets credentials found: {credentials_file}")
    return credentials_file


def initialize_gspread(credentials_file):
    """Initialize and return gspread client."""
    try:
        gc = get_gspread_client(credentials_file)
        print("✅ Successfully connected to Google Sheets API")
        print("\nSheet actions available (used by agent):")
        print("  - OpenSpreadsheet: Open a spreadsheet by name/ID")
        print("  - OpenSheet: Switch to a specific worksheet")
        print("  - GetAllValues: Read entire sheet")
        print("  - GetCellValue: Read single cell")
        print("  - UpdateCell: Update single cell")
        print("  - InsertRows: Add new rows")
        print("  - FindCell: Search for values")
        print("  - SortSheetByColumn: Sort data")
        print("  - GetSheetSummary: Get sheet overview")
        return gc
    except Exception as e:
        print(f"❌ Error connecting to Google Sheets: {e}")
        raise


def initialize_llm():
    """Create LLM using configuration from .env file."""
    llm_name = os.getenv("LLM", "openai/gpt-3.5-turbo")
    config_dict = {"llm_name": llm_name, "temperature": 0.0}
    config = LLMConfig(config_dict)
    llm = get_llm_backend(config)

    print(f"✅ LLM initialized: {llm_name}")
    print(f"   Using OPENROUTER_API_KEY from .env file")

    return llm


def create_agent(llm, gspread_client):
    """Create and return SheetManagerAgent instance."""
    return SheetManagerAgent(llm=llm, gspread_client=gspread_client)


def test_open_spreadsheet(agent, spreadsheet_name="Test Sheet"):
    """Test 1: Open a spreadsheet and get summary."""
    print("=" * 60)
    print("TEST 1: Open spreadsheet and get summary")
    print("=" * 60)

    task = f"Open the spreadsheet named '{spreadsheet_name}' and give me a summary of Sheet1"
    task_pack = TaskPackage(instruction=task)
    response = agent(task_pack)

    print(f"\n📊 Response: {response}\n")
    return response


def test_read_cell(agent):
    """Test 2: Read specific cell values."""
    print("=" * 60)
    print("TEST 2: Read cell values")
    print("=" * 60)

    task = "What is the value in cell B1 of the current sheet?"
    task_pack = TaskPackage(instruction=task)
    response = agent(task_pack)

    print(f"\n📋 Response: {response}\n")
    return response


def test_update_cell(agent):
    """Test 3: Update a cell."""
    print("=" * 60)
    print("TEST 3: Update a cell value")
    print("=" * 60)

    task = "Update cell B2 to contain the text 'Updated by Agent'"
    task_pack = TaskPackage(instruction=task)
    response = agent(task_pack)

    print(f"\n✏️  Response: {response}\n")
    return response


def test_find_cell(agent):
    """Test 4: Find a value."""
    print("=" * 60)
    print("TEST 4: Find a cell containing specific text")
    print("=" * 60)

    task = "Find the cell that contains 'Total' and tell me its location"
    task_pack = TaskPackage(instruction=task)
    response = agent(task_pack)

    print(f"\n🔍 Response: {response}\n")
    return response


def test_complex_workflow(agent):
    """Test 5: Complex workflow - Data Analysis."""
    print("=" * 60)
    print("COMPLEX WORKFLOW: Analyze and update data")
    print("=" * 60)

    task = """In the current sheet, find all cells in column A that contain 'Product',
then read the values in column B next to them, and give me a summary."""

    task_pack = TaskPackage(instruction=task)
    response = agent(task_pack)

    print(f"\n📊 Response: {response}\n")
    return response


def main():
    """Main execution function."""
    print("=" * 70)
    print("🚀 Google Sheets Manager Agent Tutorial")
    print("=" * 70)

    # Verify conda environment
    verify_environment()

    # Setup
    credentials_file = setup_environment()
    gc = initialize_gspread(credentials_file)
    llm = initialize_llm()
    agent = create_agent(llm, gc)

    print("\n" + "=" * 60)
    print("🎯 Agent initialized and ready!")
    print("=" * 60 + "\n")

    # Run tests
    try:
        # Using the converted Google Sheets document
        # https://docs.google.com/spreadsheets/d/1h-F1tMEYXKpm5efWuh0HduXGHsiz9W1alJcMEODvPIY/edit
        spreadsheet_id = "1h-F1tMEYXKpm5efWuh0HduXGHsiz9W1alJcMEODvPIY"

        test_open_spreadsheet(agent, spreadsheet_id)
        test_read_cell(agent)
        # test_update_cell(agent)
        # test_find_cell(agent)
        # test_complex_workflow(agent)

        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
