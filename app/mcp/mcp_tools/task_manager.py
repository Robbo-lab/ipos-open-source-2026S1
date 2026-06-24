from datetime import datetime
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.task_handler import TaskHandler
from app.data.pydantic_objects import PLTask
from app.services.database import get_session_api
from app.utils.get_principal import Principal
from app.utils.permissions import (
    enforce_task_read_permissions,
    enforce_task_write_permissions,
)


class TaskInput(BaseModel):
    """Input schema for task manager tools."""

    name: str = Field(
        description="Title of the task. Use this when creating or updating a task."
    )
    description: str = Field(
        description="Detailed description of what the task is about."
    )
    completed: bool = Field(
        description="Task completion status. True means completed, False means not completed."
    )
    task_started: datetime = Field(
        description="Date and time when the task was started. Use the current datetime when creating a new task."
    )


class CreateTaskInput(BaseModel):
    """Input schema for creating a new task."""

    task: PLTask = Field(
        description="The task to be created, including its title, description, status, and metadata."
    )


class CompleteTaskInput(BaseModel):
    """Input schema for marking a task as completed."""

    name: str = Field(description="Name of the task to mark as completed.")


class GetTaskByNameInput(BaseModel):
    """Input schema for retrieving a task by its name."""

    name: str = Field(description="Exact name of the task to search for.")


class GetTaskByIdInput(BaseModel):
    """Input schema for retrieving a task by its name."""

    id: str = Field(description="Exact id of the task to search for.")


class DeleteTaskByNameInput(BaseModel):
    """Input schema for deleting a task by its name."""

    name: str = Field(description="Exact name of the task to delete.")


class ListTasksInput(BaseModel):
    """Input schema for listing tasks by status."""

    task_type: str = Field(
        description="Task status filter. Valid values are 'Pending' or 'Completed'. Defaults to 'Pending'."
    )


# GetOutput
class GetTaskOutput(BaseModel):
    """Response model returned by task manager tools.

    Attributes:
        success: Indicates whether the operation completed successfully.
        message: Human-readable message describing the result.
        task: The retrieved task, or None if no task was found.
    """

    success: bool = Field(
        description="Indicates whether the operation completed successfully."
    )
    message: str = Field(
        description="Human-readable message describing the result of the operation."
    )
    task: PLTask | None = Field(
        description="The task returned by the operation, or None if no task was found."
    )


class DeleteTaskByNameOutput(BaseModel):
    """Response model for deleting a task.

    Attributes:
        message: Human-readable message describing the result.
    """

    message: str = Field(
        description="Message describing the result of the delete operation."
    )


class CreateTaskOutput(BaseModel):
    """Response model for creating a task.

    Attributes:
        success: Indicates whether the task was created successfully.
        message: Human-readable message describing the result.
        task: The created task, or None if creation failed.
    """

    success: bool = Field(
        description="Indicates whether the task was created successfully."
    )
    message: str = Field(
        description="Human-readable message describing the result of the operation."
    )
    task: PLTask | None = Field(
        description="The created task, or None if task creation failed."
    )


class ListTasksOutput(BaseModel):
    """Response model for listing tasks.

    Attributes:
        success: Indicates whether the tasks were retrieved successfully.
        message: Human-readable message describing the result.
        tasks: List of tasks matching the requested criteria, or None if no tasks were found.
    """

    success: bool = Field(
        description="Indicates whether the tasks were retrieved successfully."
    )
    message: str = Field(
        description="Human-readable message describing the result of the operation."
    )
    tasks: list[PLTask] | None = Field(
        description="List of tasks returned by the operation, or None if no tasks were found."
    )


def create_task_tool(
    session: Annotated[Session, Depends(get_session_api)],
    principal: Principal,
    body: CreateTaskInput,
) -> CreateTaskOutput:
    """Create a new task in the task manager.

    Use this tool when the user wants to create or add a new task.
    Do not use this tool to update, complete, retrieve, or delete tasks.

    Args:
        session: Database session used to access task data.
        body: Request containing the task to create.
        principal: Authenticated principal used for permission checks.

    Returns:
        CreateTaskOutput containing:
        - success: Whether the task was created successfully.
        - message: Description of the operation result.
        - task: The created task, if successful.
    """
    enforce_task_write_permissions(principal)

    try:
        task = TaskHandler.add_task_to_db(session, body.task)
    except Exception as e:
        raise e

    if task is None:
        return CreateTaskOutput(
            success=False,
            message=f"Task '{body.task.name}' was not created",
            task=task,
        )

    return CreateTaskOutput(
        success=True,
        message=f"Task '{body.task.name}' was created",
        task=task,
    )


def delete_task_tool(
    session: Annotated[Session, Depends(get_session_api)],
    principal: Principal,
    body: DeleteTaskByNameInput,
) -> DeleteTaskByNameOutput:
    """Delete an existing task by its name.

    Use this tool only when the user explicitly requests to delete or remove a task.

    Args:
        session: Database session used to access task data.
        body: Request containing the exact name of the task to delete.
        principal: Authenticated principal used for permission checks.

    Returns:
        DeleteTaskByNameOutput containing:
        - message: Description of the operation result.
    """
    enforce_task_write_permissions(principal)

    TaskHandler.delete_task(session, body.name)
    return DeleteTaskByNameOutput(
        message=f"Task '{body.name}' was deleted",
    )


def get_task_by_name_tool(
    session: Annotated[Session, Depends(get_session_api)],
    principal: Principal,
    body: GetTaskByNameInput,
) -> GetTaskOutput:
    """Retrieve a task by its name.

    Use this tool when the user wants to view, find, or get information
    about a specific task.

    Args:
        session: Database session used to access task data.
        principal: Authenticated principal used for permission checks.
        body: Request containing the exact name of the task to retrieve.

    Returns:
        GetTaskOutput containing:
        - success: Whether the task was found.
        - message: Description of the operation result.
        - task: The retrieved task, if found.
    """
    enforce_task_read_permissions(principal)

    try:
        task = TaskHandler.get_task(session, body.name)
    except Exception as e:
        raise e

    if task is None:
        return GetTaskOutput(
            success=False,
            message=f"Task '{body.name}' was not found",
            task=task,
        )

    return GetTaskOutput(
        success=True,
        message=f"Task '{body.name}' was completed",
        task=task,
    )


def get_task_by_id_tool(
    session: Annotated[Session, Depends(get_session_api)],
    principal: Principal,
    body: GetTaskByIdInput,
) -> GetTaskOutput:
    """Retrieve a task by its ID.

    Use this tool when the user wants to view, find, or get information
    about a specific task and provides the task ID.

    Args:
        session: Database session used to access task data.
        body: Request containing the unique ID of the task to retrieve.
        principal: Authenticated principal used for permission checks.

    Returns:
        GetTaskOutput containing:
        - success: Whether the task was found.
        - message: Description of the operation result.
        - task: The retrieved task, if found.
    """
    enforce_task_read_permissions(principal)

    try:
        task = TaskHandler.get_task(session, body.id)
    except Exception as e:
        raise e

    if task is None:
        return GetTaskOutput(
            success=False,
            message=f"Task '{body.id}' was not found",
            task=task,
        )

    return GetTaskOutput(
        success=True,
        message=f"Task '{body.id}' was completed",
        task=task,
    )


def list_tasks_tool(
    session: Annotated[Session, Depends(get_session_api)],
    principal: Principal,
    body: ListTasksInput,
) -> ListTasksOutput:
    """Retrieve a list of tasks filtered by status.

    Use this tool when the user wants to view multiple tasks,
    such as all pending or all completed tasks.

    Args:
        session: Database session used to access task data.
        body: Request containing the task status filter.
        principal: Authenticated principal used for permission checks.

    Returns:
            ListTasksOutput containing:
        - success: Whether matching tasks were found.
        - message: Description of the operation result.
        - tasks: List of tasks matching the requested status.
    """
    enforce_task_read_permissions(principal)

    filtered_tasks = TaskHandler.list_tasks(session, body.task_type)
    if filtered_tasks is None:
        return ListTasksOutput(
            success=False,
            message="No matching tasks were found",
            tasks=filtered_tasks,
        )

    return ListTasksOutput(
        success=True,
        message="Tasks retrieved successfully",
        tasks=filtered_tasks,
    )


def complete_task_tool(
    session: Annotated[Session, Depends(get_session_api)],
    principal: Principal,
    body: CompleteTaskInput,
) -> GetTaskOutput:
    """Mark an existing task as completed.

    Use this tool when the user wants to complete, finish,
    or mark a task as done.

    Args:
        session: Database session used to access task data.
        body: Request containing the name of the task to complete.
        principal: Authenticated principal used for permission checks.

    Returns:
        GetTaskOutput containing:
        - success: Whether the task was found and completed.
        - message: Description of the operation result.
        - task: The updated task with completed status set to True.
    """
    enforce_task_write_permissions(principal)

    task = TaskHandler.get_task(session, body.name)

    if task is None:
        return GetTaskOutput(
            success=False,
            message=f"Task '{body.name}' was not found",
            task=task,
        )
    completed_task = TaskHandler.complete_task(session, task)

    return GetTaskOutput(
        success=True,
        message=f"Task '{body.name}' was completed",
        task=completed_task,
    )


TOOL_DEFINITION = [
    {
        "name": "create_task",
        "description": (
            "Create a new task in the task manager. "
            "Use when the user wants to add a task."
        ),
        "func": create_task_tool,
        "tags": {"task", "create", "add"},
    },
    {
        "name": "delete_task",
        "description": (
            "Delete an existing task by its name. "
            "Use only when the user explicitly requests task removal."
        ),
        "func": delete_task_tool,
        "tags": {"task", "delete", "remove"},
    },
    {
        "name": "get_task_by_name",
        "description": (
            "Retrieve a task using its exact name. "
            "Use when the user wants to view information about a specific task."
        ),
        "func": get_task_by_name_tool,
        "tags": {"task", "get", "find", "search", "name"},
    },
    {
        "name": "get_task_by_id",
        "description": (
            "Retrieve a task using its unique identifier. "
            "Use when the task ID is known."
        ),
        "func": get_task_by_id_tool,
        "tags": {"task", "get", "find", "search", "id"},
    },
    {
        "name": "list_tasks",
        "description": (
            "List tasks filtered by status. Use to retrieve pending or completed tasks."
        ),
        "func": list_tasks_tool,
        "tags": {"task", "list", "filter", "completed", "pending"},
    },
    {
        "name": "complete_task",
        "description": (
            "Mark a task as completed. "
            "Use when the user wants to finish, complete, or mark a task as done."
        ),
        "func": complete_task_tool,
        "tags": {"task", "complete", "finish", "done"},
    },
]
