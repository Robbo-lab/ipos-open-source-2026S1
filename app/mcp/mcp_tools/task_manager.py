# from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.api.task_handler import TaskHandler
from datetime import datetime
from app.data.pydantic_objects import PLTask
from app.services.database import get_session_api
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated


# router = APIRouter(prefix="", tags=["managing-task"])

class TaskInput(BaseModel):
    name: str = Field(description="Task title")
    description: str = Field(description="Task description")
    completed: bool = Field(description="Shows whether the task is completed or not. Contains True if completed or False if not")
    name_or_id: int | str = Field(description="Contains either id of a task or its name")
    task_started: datetime = Field(description="Date when the task was started, or current one if task was just added")

class CreateTaskInput(BaseModel):
    task: PLTask = Field(description="An PLTask instance of created task")

class CompleteTaskInput(BaseModel):
    name: str = Field(description="Name of the task to complete")

class GetTaskByNameInput(BaseModel):
    name: str = Field(description="Name of the task to find")

class GetTaskByIdInput(BaseModel):
    id: str = Field(description="Id of the task to find")

class DeleteTaskByNameInput(BaseModel):
    name: str = Field(description="Name of the task to delete")

class ListTasksInput(BaseModel):
    task_type: str = Field(description="Task status (Pending/Completed) Pending by default")



class GetTaskOutput(BaseModel):
    """Response model for task manager.

    Attributes:
        task: is an PLTask instance of created task.
    """
    success: bool = Field(description="Shows whether the task was completed successfully or not")
    message: str = Field(description="Saves the message when the function is completed")
    task: PLTask | None= Field(description="Saves an instance of PLTask if it has been returned")

class DeleteTaskByNameOutput(BaseModel):
    message: str = Field(description="Saves the message when the function is completed")

class CreateTaskOutput(BaseModel):
    """Response model for task manager.

    Attributes:
        task: is an PLTask instance of created task.
    """
    success: bool = Field(description="Shows whether the task was completed successfully or not")
    message: str = Field(description="Saves the message when the function is completed")
    task: PLTask | None= Field(description="Saves an instance of PLTask if it has been returned")

class ListTasksOutput(BaseModel):
    """Response model for task manager.

    Attributes:
        task: is an PLTask instance of created task.
    """
    success: bool = Field(description="Shows whether the task was completed successfully or not")
    message: str = Field(description="Saves the message when the function is completed")
    task: list[PLTask] | None= Field(description="Saves an instance of PLTask if it has been returned")





def create_task_tool(session: Annotated[Session, Depends(get_session_api)], body: CreateTaskInput = None) -> CreateTaskOutput:
    try:
        task = TaskHandler.add_task_to_db(session, body.task)
    except Exception as e:
        raise e

    if task is None:
        return CreateTaskOutput(
            success= False,
            message= f"Task '{body.task.name}' was not created",
            task=task,
        )

    return CreateTaskOutput(
        success=True,
        message=f"Task '{body.task.name}' was completed",
        task= task,
    )

def delete_task_tool(session: Annotated[Session, Depends(get_session_api)], body: DeleteTaskByNameInput = None)->DeleteTaskByNameOutput:

    TaskHandler.delete_task(session, body.name)
    return DeleteTaskByNameOutput(
        message=f"Task '{body.name}' was deleted",
    )


def get_task_by_name_tool(session: Annotated[Session, Depends(get_session_api)], body: GetTaskByNameInput = None)->GetTaskOutput:
    try:
        task = TaskHandler.get_task(session, body.name)
    except Exception as e:
        raise e

    if task is None:
        return GetTaskOutput(
            success= False,
            message= f"Task '{body.name}' was not found",
            task=task,
        )

    return GetTaskOutput(
        success=True,
        message=f"Task '{body.name}' was completed",
        task= task,
    )

def get_task_by_id_tool(session: Annotated[Session, Depends(get_session_api)], body: GetTaskByIdInput = None)->GetTaskOutput:
    try:
        task = TaskHandler.get_task(session, body.id)
    except Exception as e:
        raise e

    if task is None:
        return GetTaskOutput(
            success= False,
            message= f"Task '{body.name}' was not found",
            task=task,
        )

    return GetTaskOutput(
        success=True,
        message=f"Task '{body.name}' was completed",
        task= task,
    )

def list_tasks_tool(session: Annotated[Session, Depends(get_session_api)], body: ListTasksInput = None) -> ListTasksOutput:
    filtered_tasks =TaskHandler.list_tasks(session, body.task_type)

    if filtered_tasks is None:
        return ListTasksOutput(
            success= False,
            message= f"Task was not finished",
            task=filtered_tasks,
        )

    return ListTasksOutput(
        success=True,
        message=f"Task was completed",
        task= filtered_tasks,
    )



def complete_task_tool(session: Annotated[Session, Depends(get_session_api)], body: CompleteTaskInput = None)->GetTaskOutput:
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
        message= f"Task '{body.name}' was completed",
        task=completed_task,
    )

TOOL_DEFINITION = [
    {
        "name": "create_task",
        "description": "Creates a task as an instance of PLTask",
        "func": create_task_tool,
        "tags": {"task", "create"},
    },
    {
        "name": "delete_task",
        "description": "deletes a task from database",
        "func": delete_task_tool,
        "tags": {"task", "delete"},
    },
    {
        "name": "get_task",
        "description": "gets the specified by the name task and returns it",
        "func": get_task_by_name_tool,
        "tags": {"get", "task", "check", "name"},
    },
    {
        "name": "get_task",
        "description": "gets the specified by id task and returns it",
        "func": get_task_by_id_tool,
        "tags": {"get", "task", "id", "check"},
    },
    {
        "name": "list_tasks",
        "description": "filters tasks by status either completed or pending and returns as a list",
        "func": list_tasks_tool,
        "tags": {"filter", "task", "completed", "pending"},
    },
]
