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
    type: str = Field(description="Distance in miles (>= 0)")
    description: str = Field(description="Task description")
    completed: bool = Field(description="Task status (Pending/Completed) Pending by default")
    name_or_id: int | str = Field(description="Contains either id of a task or its name")
    task_started: datetime = Field(description="Date when the task was started, or current one if task was just added")

class CompleteTaskInput(BaseModel):
    name: str = Field(description="Name of the task to complete")

class GetTaskByNameInput(BaseModel):
    name: str = Field(description="Name of the task to find")

class GetTaskByIdInput(BaseModel):
    id: str = Field(description="Id of the task to find")

class DeleteTaskByNameInput(BaseModel):
    name: str = Field(description="Name of the task to delete")

class GetTaskOutput(BaseModel):
    """Response model for task manager.

    Attributes:
        task: is an PLTask instance of created task.
    """
    success: bool = Field(description="Shows whether the task was completed successfully or not")
    message: str = Field(description="Saves the message when the function is completed")
    task: PLTask | None= Field(description="Saves an instance of PLTask if it has been returned")


def create_task_tool(session: Annotated[Session, Depends(get_session_api)], name: str | None = None) -> PLTask:
    """
    This method creates a new task

    Args:
        body: Request body containing the task parameters.

    Returns:
        PLTask type instance of a task which has been created.
    """

    taskHandler = TaskHandler()

    # task = taskHandler.create_task(body.name, body.type, body.description, body.completed)
    #
    # return TaskOutput(
    #     task=task
    # )


def add_task_to_db_tool(body: TaskInput):
    """
    This method  adds task to the database

    Args:
        body: Request body containing the database.
        TaskOutput: Contains PLTask instance of created task
    """
    # taskHandler = TaskHandler()
    # taskHandler.add_task_to_db(body.db, TaskOutput.task)


def delete_task_tool(session: Annotated[Session, Depends(get_session_api)], body: DeleteTaskByNameInput = None)->

    TaskHandler.delete_task(session, body.name)


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

def list_tasks_tool(body: TaskInput):
    """
    This method gets all the task filtering by specified type (Complete or Pending).

    Args:
        body: request type and db from the body.

    Returns:
        list: which contains filtered by status tasks from the database
    """

    taskHandler = TaskHandler()
    taskHandler.list_tasks(body.db, body.type)




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

def task_run_duration_tool():
    """
    This method calculated the duration of how much time has been spent on a task.

    Args:
        task (PLTask): request an PLTask instance of a task from the TaskOutput.

    Returns:
        float: time it took to finish the task
    """
    taskHandler = TaskHandler()
    taskHandler.task_run_duration(TaskOutput.task)


TOOL_DEFINITION = [
    {
        "name": "create_task",
        "description": "Creates a task as an instance of PLTask",
        "func": create_task_tool,
        "tags": {"task", "create"},
    },
    {
        "name": "add_task_to_db",
        "description": "Saves the task PLTask instance in db.database",
        "func": add_task_to_db_tool,
    },
    {
        "name": "delete_task",
        "description": "deletes a task from database",
        "func": delete_task_tool,
        "tags": {"task", "delete"},
    },
    {
        "name": "get_task",
        "description": "gets the specified by the name or id task and returns it",
        "func": get_task_tool,
        "tags": {"get", "task", "check"},
    },
    {
        "name": "list_tasks",
        "description": "filters tasks by status either completed or pending and returns as a list",
        "func": list_tasks_tool,
        "tags": {"filter", "task", "completed", "pending"},
    },
    {
        "name": "task_run_duration",
        "description": "calculates how long did it take to finish the task",
        "func": task_run_duration_tool,
        "tags": {"duration", "time", "task"},
    },
]
