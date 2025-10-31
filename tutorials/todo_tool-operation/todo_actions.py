"""
Todoist Action Implementations
Direct API wrappers for Todoist operations - no environment, no rewards
"""

import os
import requests
from datetime import datetime
from agentlite.actions.BaseAction import BaseAction

# Todoist API configuration
TODOIST_BASE_URL = "https://api.todoist.com/rest/v2"


def get_headers():
    """Get authorization headers for Todoist API"""
    api_key = os.getenv('TODO_KEY')
    if not api_key:
        raise ValueError("TODO_KEY not found in environment variables")
    return {"Authorization": f"Bearer {api_key}"}


class GetCurrentDate(BaseAction):
    """Get today's date in YYYY-MM-DD format"""

    def __init__(self) -> None:
        action_name = "get_user_current_date"
        action_desc = "Get the current date of the user"
        params_doc = {}
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self):
        return datetime.now().strftime("%Y-%m-%d")


class GetUserCurrentLocation(BaseAction):
    """Get the current location of the user (simulated)"""

    def __init__(self) -> None:
        action_name = "get_user_current_location"
        action_desc = "Get the current location of the user"
        params_doc = {}
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self):
        # In a real implementation, this would use geolocation API
        # For now, return a default location
        return "Current Location: Not available (requires geolocation API)"


class GetProjects(BaseAction):
    """Get all projects with their IDs and names"""

    def __init__(self) -> None:
        action_name = "get_projects"
        action_desc = "Get all projects with their IDs and names"
        params_doc = {}
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self):
        try:
            response = requests.get(f"{TODOIST_BASE_URL}/projects", headers=get_headers())
            response.raise_for_status()
            projects = response.json()
            # Return simplified project info
            return [{"id": p["id"], "name": p["name"], "is_favorite": p.get("is_favorite", False)}
                    for p in projects]
        except Exception as e:
            return f"Error getting projects: {str(e)}"


class UpdateProject(BaseAction):
    """Update project details (favorite status)"""

    def __init__(self) -> None:
        action_name = "update_project"
        action_desc = "Update the project details"
        params_doc = {
            "project_id": "(Type: string) The ID of the project to update",
            "is_favorite": "(Type: boolean) The favorite status of the project"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, project_id: str, is_favorite: bool):
        try:
            response = requests.post(
                f"{TODOIST_BASE_URL}/projects/{project_id}",
                headers=get_headers(),
                json={"is_favorite": is_favorite}
            )
            response.raise_for_status()
            return f"Project {project_id} updated successfully (is_favorite: {is_favorite})"
        except Exception as e:
            return f"Error updating project: {str(e)}"


class GetTasks(BaseAction):
    """Get all tasks for a specific project"""

    def __init__(self) -> None:
        action_name = "get_tasks"
        action_desc = "Get all tasks for a specific project"
        params_doc = {
            "project_id": "(Type: string) The ID of the project"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, project_id: str):
        try:
            response = requests.get(
                f"{TODOIST_BASE_URL}/tasks",
                params={"project_id": project_id},
                headers=get_headers()
            )
            response.raise_for_status()
            tasks = response.json()
            # Return simplified task info
            return [{"id": t["id"], "content": t["content"],
                    "due_date": t.get("due", {}).get("date", "No due date")}
                    for t in tasks]
        except Exception as e:
            return f"Error getting tasks: {str(e)}"


class GetTaskDescription(BaseAction):
    """Get the description of a specific task"""

    def __init__(self) -> None:
        action_name = "get_task_description"
        action_desc = "Get the description of a specific task"
        params_doc = {
            "task_id": "(Type: string) The ID of the task"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, task_id: str):
        try:
            response = requests.get(
                f"{TODOIST_BASE_URL}/tasks/{task_id}",
                headers=get_headers()
            )
            response.raise_for_status()
            task = response.json()
            return task.get("description", "No description available")
        except Exception as e:
            return f"Error getting task description: {str(e)}"


class GetTaskDuration(BaseAction):
    """Get the estimated duration of a task"""

    def __init__(self) -> None:
        action_name = "get_task_duration"
        action_desc = "Get the duration of a task"
        params_doc = {
            "task_id": "(Type: string) The ID of the task to get duration for"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, task_id: str):
        try:
            response = requests.get(f"{TODOIST_BASE_URL}/tasks/{task_id}", headers=get_headers())
            response.raise_for_status()
            task = response.json()
            # Duration is stored in the 'duration' field (in minutes)
            duration = task.get("duration")
            if duration:
                return f"Task {task_id} duration: {duration.get('amount')} {duration.get('unit')}"
            else:
                return f"Task {task_id} has no duration set"
        except Exception as e:
            return f"Error getting task duration: {str(e)}"


class CompleteTask(BaseAction):
    """Mark a task as completed"""

    def __init__(self) -> None:
        action_name = "complete_task"
        action_desc = "Mark a task as completed"
        params_doc = {
            "task_id": "(Type: string) The ID of the task to complete"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, task_id: str):
        try:
            response = requests.post(
                f"{TODOIST_BASE_URL}/tasks/{task_id}/close",
                headers=get_headers()
            )
            response.raise_for_status()
            return f"Task {task_id} completed successfully"
        except Exception as e:
            return f"Error completing task: {str(e)}"


class UpdateTaskDueDate(BaseAction):
    """Update the due date of a task"""

    def __init__(self) -> None:
        action_name = "update_task"
        action_desc = "Update the due date of a task"
        params_doc = {
            "task_id": "(Type: string) The ID of the task to update",
            "due_date": "(Type: string) The new due date for the task (YYYY-MM-DD)"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, task_id: str, due_date: str):
        try:
            response = requests.post(
                f"{TODOIST_BASE_URL}/tasks/{task_id}",
                json={"due_date": due_date},
                headers=get_headers()
            )
            response.raise_for_status()
            return f"Task {task_id} due date updated to {due_date}"
        except Exception as e:
            return f"Error updating task: {str(e)}"


class DeleteTask(BaseAction):
    """Delete a task permanently"""

    def __init__(self) -> None:
        action_name = "delete_task"
        action_desc = "Delete a task permanently"
        params_doc = {
            "task_id": "(Type: string) The ID of the task to delete"
        }
        super().__init__(action_name, action_desc, params_doc)

    def __call__(self, task_id: str):
        try:
            response = requests.delete(
                f"{TODOIST_BASE_URL}/tasks/{task_id}",
                headers=get_headers()
            )
            response.raise_for_status()
            return f"Task {task_id} deleted successfully"
        except Exception as e:
            return f"Error deleting task: {str(e)}"
