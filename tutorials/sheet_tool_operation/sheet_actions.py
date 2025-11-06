"""
Google Sheets Action Implementations
Direct gspread API wrappers - no environment, no rewards
"""

import os
import re
import gspread
from typing import Optional, List, Any
from agentlite.actions.BaseAction import BaseAction

# Global state to track current spreadsheet and worksheet
current_spreadsheet = None
current_worksheet = None


def get_gspread_client(credentials_file: str = None):
    """Initialize and return gspread client"""
    if credentials_file is None:
        credentials_file = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "credentials.json")

    if not os.path.exists(credentials_file):
        raise FileNotFoundError(
            f"Credentials file not found: {credentials_file}\n"
            "Please download your service account credentials and save as credentials.json"
        )

    return gspread.service_account(filename=credentials_file)


def validate_A1_notation(cell: str) -> bool:
    """Validate if string is in A1 notation (e.g., A1, B2, AA10)"""
    pattern = r"^[A-Z]+[0-9]+$"
    return bool(re.match(pattern, cell))


class OpenSpreadsheet(BaseAction):
    """Open a Google Spreadsheet by name or ID"""

    def __init__(self, gc=None) -> None:
        action_name = "open_spreadsheet"
        action_desc = "Open a Google Spreadsheet by name or ID"
        params_doc = {
            "spreadsheet_name_or_id": "string: Name or ID of the spreadsheet to open",
            "name_or_id": "string (optional alias): Deprecated name parameter, kept for backwards compatibility",
        }
        self.gc = gc
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, spreadsheet_name_or_id: str = None, name_or_id: str = None):
        global current_spreadsheet

        target_id = spreadsheet_name_or_id or name_or_id
        if not target_id:
            return "Error: Missing spreadsheet identifier. Provide 'spreadsheet_name_or_id'."

        if self.gc is None:
            return "Error: gspread client not initialized"

        try:
            # Try opening by ID first
            try:
                current_spreadsheet = self.gc.open_by_key(target_id)
            except Exception as e1:
                # If opening by ID fails, try by name
                try:
                    current_spreadsheet = self.gc.open(target_id)
                except Exception as e2:
                    return (
                        "Error opening spreadsheet: Could not find spreadsheet with name or ID "
                        f"'{target_id}'. Errors: By ID: {str(e1)}, By name: {str(e2)}"
                    )

            sheets = [ws.title for ws in current_spreadsheet.worksheets()]
            return f"Opened spreadsheet '{current_spreadsheet.title}'. Available sheets: {sheets}"
        except Exception as e:
            return f"Error opening spreadsheet: {str(e)}"


class OpenSheet(BaseAction):
    """Open a specific sheet (worksheet) within the current spreadsheet"""

    def __init__(self) -> None:
        action_name = "open_sheet"
        action_desc = "Open a specific sheet (worksheet) within the current spreadsheet"
        params_doc = {
            "sheet_name": "string: Name of the worksheet to open"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, sheet_name: str):
        global current_worksheet
        if not current_spreadsheet:
            return "Error: No spreadsheet is currently open. Use open_spreadsheet first."

        try:
            current_worksheet = current_spreadsheet.worksheet(sheet_name)
            row_count = current_worksheet.row_count
            col_count = current_worksheet.col_count
            return f"Opened sheet '{sheet_name}' ({row_count} rows × {col_count} columns)"
        except Exception as e:
            return f"Error opening sheet: {str(e)}"


class GetAllValues(BaseAction):
    """Get all values from the current sheet as a 2D list"""

    def __init__(self) -> None:
        action_name = "get_all_values"
        action_desc = "Get all values from the current sheet as a 2D list. No parameters required."
        params_doc = {"dummy": "string (optional): Not used - leave empty"}
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, dummy: str = None):
        if not current_worksheet:
            return "Error: No sheet is currently open. Use open_sheet first."

        try:
            values = current_worksheet.get_all_values()
            if not values:
                return "Sheet is empty"
            return values
        except Exception as e:
            return f"Error getting values: {str(e)}"


class GetCellValue(BaseAction):
    """Get the value of a specific cell"""

    def __init__(self) -> None:
        action_name = "get_cell_value"
        action_desc = "Get the value of a specific cell"
        params_doc = {
            "cell": "string: Cell address in A1 notation (e.g., 'A1', 'B2')"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, cell: str):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        if not validate_A1_notation(cell):
            return f"Error: '{cell}' is not valid A1 notation. Use format like 'A1', 'B5'"

        try:
            value = current_worksheet.acell(cell).value
            return value if value else "(empty)"
        except Exception as e:
            return f"Error getting cell value: {str(e)}"


class GetRangeValues(BaseAction):
    """Get values from a cell range"""

    def __init__(self) -> None:
        action_name = "get_range_values"
        action_desc = "Get values from a cell range"
        params_doc = {
            "range_notation": "string: Range in A1 notation (e.g., 'A1:B10')"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, range_notation: str):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        try:
            values = current_worksheet.get(range_notation)
            return values if values else "Range is empty"
        except Exception as e:
            return f"Error getting range: {str(e)}"


class UpdateCell(BaseAction):
    """Update a single cell with a value"""

    def __init__(self) -> None:
        action_name = "update_cell"
        action_desc = "Update a single cell with a value"
        params_doc = {
            "cell": "string: Cell address in A1 notation (e.g., 'A1')",
            "value": "string or number: Value to write to the cell"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, cell: str, value: str):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        if not validate_A1_notation(cell):
            return f"Error: '{cell}' is not valid A1 notation."

        try:
            current_worksheet.update_acell(cell, value)
            return f"Cell {cell} updated to '{value}'"
        except Exception as e:
            return f"Error updating cell: {str(e)}"


class UpdateRange(BaseAction):
    """Update a range of cells with values"""

    def __init__(self) -> None:
        action_name = "update_range"
        action_desc = "Update a range of cells with values"
        params_doc = {
            "range_notation": "string: Range in A1 notation (e.g., 'A1:B2')",
            "values": "list of lists: 2D array of values to write"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, range_notation: str, values: List[List[Any]]):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        try:
            current_worksheet.update(range_notation, values)
            return f"Range {range_notation} updated successfully"
        except Exception as e:
            return f"Error updating range: {str(e)}"


class InsertRows(BaseAction):
    """Insert new rows with data"""

    def __init__(self) -> None:
        action_name = "insert_rows"
        action_desc = "Insert new rows with data"
        params_doc = {
            "values": "list of lists: Rows to insert, each row is a list of values",
            "row_index": "integer: Position to insert rows (1-indexed)"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, values: List[List[Any]], row_index: int):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        try:
            current_worksheet.insert_rows(values, row_index)
            return f"Inserted {len(values)} row(s) at row {row_index}"
        except Exception as e:
            return f"Error inserting rows: {str(e)}"


class FindCell(BaseAction):
    """Find a cell containing a specific value"""

    def __init__(self) -> None:
        action_name = "find_cell"
        action_desc = "Find a cell containing a specific value"
        params_doc = {
            "query": "string: Text to search for in the sheet"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, query: str):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        try:
            cell = current_worksheet.find(query)
            if cell:
                return f"Found '{query}' at {cell.address} (row {cell.row}, col {cell.col})"
            else:
                return f"Value '{query}' not found in sheet"
        except Exception as e:
            return f"Error finding cell: {str(e)}"


class SortSheetByColumn(BaseAction):
    """Sort the entire sheet by a specific column"""

    def __init__(self) -> None:
        action_name = "sort_sheet_by_column"
        action_desc = "Sort the entire sheet by a specific column"
        params_doc = {
            "column_index": "integer: Column number to sort by (1-indexed)",
            "order": "string (optional): Sort order 'asc' or 'desc', default is 'asc'"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, column_index: int, order: str = "asc"):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        if order not in ["asc", "desc"]:
            return "Error: Order must be 'asc' or 'desc'"

        try:
            current_worksheet.sort((column_index, order))
            return f"Sheet sorted by column {column_index} in {order}ending order"
        except Exception as e:
            return f"Error sorting sheet: {str(e)}"


class GetSheetSummary(BaseAction):
    """Get a summary of the current sheet (dimensions, first few rows)"""

    def __init__(self) -> None:
        action_name = "get_sheet_summary"
        action_desc = "Get a summary of the current sheet (dimensions, first few rows). No parameters required."
        params_doc = {"dummy": "string (optional): Not used - leave empty"}
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, dummy: str = None):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        try:
            row_count = current_worksheet.row_count
            col_count = current_worksheet.col_count
            values = current_worksheet.get_all_values()

            summary = f"Sheet: {current_worksheet.title}\n"
            summary += f"Dimensions: {row_count} rows × {col_count} columns\n"

            if values:
                summary += f"\nFirst 3 rows:\n"
                for i, row in enumerate(values[:3], 1):
                    summary += f"Row {i}: {row}\n"
            else:
                summary += "Sheet is empty"

            return summary
        except Exception as e:
            return f"Error getting summary: {str(e)}"


class DeleteSheet(BaseAction):
    """Delete a sheet (worksheet) from the spreadsheet"""

    def __init__(self) -> None:
        action_name = "del_sheet"
        action_desc = "Delete a sheet"
        params_doc = {
            "name": "string: The name of the sheet to delete"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, name: str):
        global current_spreadsheet
        if not current_spreadsheet:
            return "Error: No spreadsheet is currently open."

        try:
            worksheet = current_spreadsheet.worksheet(name)
            current_spreadsheet.del_worksheet(worksheet)
            return f"Sheet '{name}' deleted successfully"
        except Exception as e:
            return f"Error deleting sheet: {str(e)}"


class FreezeData(BaseAction):
    """Freeze rows or columns in a sheet"""

    def __init__(self) -> None:
        action_name = "freeze_data"
        action_desc = "Freeze data in a sheet"
        params_doc = {
            "dimension": "string: The dimension to freeze data in (row or column)",
            "num": "integer: The number of rows or columns to freeze"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, dimension: str, num: int):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        try:
            if dimension.lower() == "row":
                current_worksheet.freeze(rows=num)
                return f"Froze {num} row(s)"
            elif dimension.lower() == "column":
                current_worksheet.freeze(cols=num)
                return f"Froze {num} column(s)"
            else:
                return "Error: Dimension must be 'row' or 'column'"
        except Exception as e:
            return f"Error freezing data: {str(e)}"


class GetA1Annotation(BaseAction):
    """Get the A1 notation for a given row and column"""

    def __init__(self) -> None:
        action_name = "get_A1_annotation"
        action_desc = "Get the annotation at A1"
        params_doc = {
            "row": "integer: The row of the annotation",
            "col": "integer: The column of the annotation"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, row: int, col: int):
        try:
            # Convert row and column to A1 notation
            import gspread.utils
            cell_address = gspread.utils.rowcol_to_a1(row, col)
            return f"A1 notation for row {row}, col {col}: {cell_address}"
        except Exception as e:
            return f"Error getting A1 notation: {str(e)}"


class InsertColumns(BaseAction):
    """Insert columns into a sheet"""

    def __init__(self) -> None:
        action_name = "insert_cols"
        action_desc = "Insert columns into a sheet"
        params_doc = {
            "values_list": "list: The list of values to insert",
            "col_idx": "integer: The index of the column to insert the values into"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, values_list: List[Any], col_idx: int):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        try:
            current_worksheet.insert_cols(values_list, col_idx)
            return f"Inserted column at index {col_idx}"
        except Exception as e:
            return f"Error inserting columns: {str(e)}"


class DeleteBatchData(BaseAction):
    """Delete batch data from a sheet (rows or columns)"""

    def __init__(self) -> None:
        action_name = "delete_batch_data"
        action_desc = "Delete batch data from a sheet"
        params_doc = {
            "dimension": "string: The dimension to delete data from (row or column)",
            "index_list": "list: The list of indices to delete data from"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, dimension: str, index_list: List[int]):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        try:
            if dimension.lower() == "row":
                # Delete rows in reverse order to avoid index shifting
                for idx in sorted(index_list, reverse=True):
                    current_worksheet.delete_rows(idx)
                return f"Deleted {len(index_list)} row(s)"
            elif dimension.lower() == "column":
                for idx in sorted(index_list, reverse=True):
                    current_worksheet.delete_columns(idx)
                return f"Deleted {len(index_list)} column(s)"
            else:
                return "Error: Dimension must be 'row' or 'column'"
        except Exception as e:
            return f"Error deleting batch data: {str(e)}"


class UpdateCellByFormula(BaseAction):
    """Update a cell using a formula"""

    def __init__(self) -> None:
        action_name = "update_cell_by_formula"
        action_desc = "Update a cell by formula in a sheet"
        params_doc = {
            "start_position": "string: The start position of the range to update",
            "end_position": "string: The end position of the range to update",
            "position_list": "list: The list of positions to update by formula",
            "operator": "string: The operator to use in the formula",
            "result_position": "string: The position to store the result of the formula"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, start_position: str = None, end_position: str = None,
                 position_list: List[str] = None, operator: str = None,
                 result_position: str = None):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        try:
            # Build formula based on inputs
            if position_list and operator and result_position:
                formula = f"={operator}({','.join(position_list)})"
            elif start_position and end_position and operator and result_position:
                formula = f"={operator}({start_position}:{end_position})"
            else:
                return "Error: Invalid formula parameters"

            current_worksheet.update_acell(result_position, formula)
            return f"Formula '{formula}' applied to {result_position}"
        except Exception as e:
            return f"Error updating cell by formula: {str(e)}"


class SortSheetByCol(BaseAction):
    """Sort a sheet by column (alias for compatibility)"""

    def __init__(self) -> None:
        action_name = "sort_sheet_by_col"
        action_desc = "Sort a sheet by column"
        params_doc = {
            "col_num": "integer: The number of the column to sort by",
            "order": "string: The order to sort by (ascending or descending)"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, col_num: int, order: str = "ascending"):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        # Convert order to asc/desc format
        order_map = {"ascending": "asc", "descending": "desc"}
        order_key = order_map.get(order.lower(), "asc")

        try:
            current_worksheet.sort((col_num, order_key))
            return f"Sheet sorted by column {col_num} in {order} order"
        except Exception as e:
            return f"Error sorting sheet: {str(e)}"


class MergeCells(BaseAction):
    """Merge cells in a sheet"""

    def __init__(self) -> None:
        action_name = "merge_cells"
        action_desc = "Merge cells in a sheet"
        params_doc = {
            "start_position": "string: The start position of the range to merge",
            "end_position": "string: The end position of the range to merge"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, start_position: str, end_position: str):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        try:
            merge_range = f"{start_position}:{end_position}"
            current_worksheet.merge_cells(merge_range)
            return f"Cells {merge_range} merged successfully"
        except Exception as e:
            return f"Error merging cells: {str(e)}"


class UpdateNote(BaseAction):
    """Update a note (comment) in a cell"""

    def __init__(self) -> None:
        action_name = "update_note"
        action_desc = "Update a note in a sheet"
        params_doc = {
            "position": "string: The position of the cell to update the note for",
            "content": "string: The content of the note to update"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, position: str, content: str):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        try:
            current_worksheet.update_note(position, content)
            return f"Note added to cell {position}"
        except Exception as e:
            return f"Error updating note: {str(e)}"


class GetValueByFormula(BaseAction):
    """Get the value calculated by a formula"""

    def __init__(self) -> None:
        action_name = "get_value_by_formula"
        action_desc = "Get the value of a cell by formula in a sheet"
        params_doc = {
            "start_position": "string: The start position of the range to get values by formula",
            "end_position": "string: The end position of the range to get values by formula",
            "position_list": "list: The list of positions to get values by formula",
            "operator": "string: The operator to use in the formula"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, start_position: str = None, end_position: str = None,
                 position_list: List[str] = None, operator: str = None):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        try:
            # Build formula
            if position_list and operator:
                formula = f"={operator}({','.join(position_list)})"
            elif start_position and end_position and operator:
                formula = f"={operator}({start_position}:{end_position})"
            else:
                return "Error: Invalid formula parameters"

            # Note: This is a simplified implementation
            # In practice, you'd need to evaluate the formula
            return f"Formula would be: {formula}"
        except Exception as e:
            return f"Error getting value by formula: {str(e)}"


class FilterCells(BaseAction):
    """Filter cells in a sheet"""

    def __init__(self) -> None:
        action_name = "filter_cells"
        action_desc = "Filter cells in a sheet"
        params_doc = {
            "query": "string: The query to filter cells by",
            "in_row": "boolean: Whether to filter cells in the row",
            "in_column": "boolean: Whether to filter cells in the column"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, query: str, in_row: bool = True, in_column: bool = True):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        try:
            # Find all cells matching the query
            cell_list = current_worksheet.findall(query)

            if not cell_list:
                return f"No cells found matching '{query}'"

            results = []
            for cell in cell_list:
                results.append(f"{cell.address} (row {cell.row}, col {cell.col}): {cell.value}")

            return f"Found {len(cell_list)} matching cells:\n" + "\n".join(results[:10])
        except Exception as e:
            return f"Error filtering cells: {str(e)}"


class GetNote(BaseAction):
    """Get the note (comment) of a cell"""

    def __init__(self) -> None:
        action_name = "get_note"
        action_desc = "Get the note of a cell in a sheet"
        params_doc = {
            "position": "string: The position of the cell to get the note for"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, position: str):
        if not current_worksheet:
            return "Error: No sheet is currently open."

        try:
            cell = current_worksheet.acell(position, value_render_option='FORMULA')
            note = current_worksheet.get_note(position)
            if note:
                return f"Note at {position}: {note}"
            else:
                return f"No note found at {position}"
        except Exception as e:
            return f"Error getting note: {str(e)}"

