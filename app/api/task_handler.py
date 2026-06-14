from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.data.database_objects import DBTask
from app.data.pydantic_objects import PLTask
from app.services.database import DataBaseMethods


class TaskHandler:
    """
    Task Handler class manages the creation, deleting & finding of tasks.
    This class uses only TaskMethods so creating an instance of this class
    isn't required.

    Args:
        None

    Returns:
        None
    """

    @classmethod
    def create_task(cls, name: str, _type: str,
                    description: str, completed: bool = False) -> PLTask:
        return PLTask(name=name,
                      type=_type,
                      description=description,
                      completed=completed)

    # creates a task with curl content
    @classmethod
    def add_task_to_db(cls, db: Session, task: PLTask):
        """Creates a task and adds it to the misc."""
        print(db)
        new_task_obj = DBTask(id=task.id or None,
                              name=task.name,
                              type=task.type,
                              description=task.description,
                              completed=task.completed or False,
                              task_started=task.task_started or datetime.now())

        new_task_obj = DataBaseMethods.add_object(db, new_task_obj)

        if not new_task_obj:
            raise Exception("No new task obj")

        task.id = new_task_obj.id

        return task

    # Deletes a task based on int or str inputted
    @classmethod
    def delete_task(cls, db: Session, name_or_id: int | str):
        if type(name_or_id) is int:
            task = DataBaseMethods.get_object_by_id(db, DBTask, name_or_id)
        elif type(name_or_id) is str:
            task = DataBaseMethods.get_object_by_name(db, DBTask, name_or_id)
        else:
            task = None
            raise Exception("name_or_id must be either a name or a id")

        if task:
            DataBaseMethods.delete_object(db, task)

    # Don't like repetitive nature of this func
    @classmethod
    def get_task(cls, db, name: str | int):
        """
        This method gets a task by either it's name or id.

        Args:
            db (Session): Session
            name (str, int): Name or ID of task

        Returns:
            task (PLTask): pydantic object of task in this case a PLTask
        """
        if type(name) is str:
            dbtask = DataBaseMethods.get_object_by_name(db, DBTask, name)
        elif type(name) is int:
            dbtask = DataBaseMethods.get_object_by_id(db, DBTask, name)
        else:
            raise Exception("Name must be int or str")

        if dbtask:
            # makes sure that the returned task is a pydantic object
            return cls.__from_db_to_pl(dbtask)
        return False

    @classmethod
    def list_tasks(cls, db: Session, _type: str | None = None):

        tasks = DataBaseMethods.query_db(db, DBTask, "type", _type)
        new_list = []

        for task in tasks:
            new_list.append(cls.__from_db_to_pl(task))

        return new_list

    @classmethod
    def complete_task(cls, db: Session, task: PLTask):
        task.completed = True
        task.task_ended = datetime.now()

        dbtask = DataBaseMethods.get_object_by_id(db, DBTask, task.id)

        if dbtask:
            try:
                dbtask.completed = True
                dbtask.task_ended = task.task_ended

                db.commit()
                return task
            except Exception as err:
                raise HTTPException(status_code=500,
                                    detail=str(err)) from err
        else:
            raise HTTPException(status_code=404, detail="Task not found")

    @classmethod
    def task_run_duration(cls, task: PLTask):
        if task.task_started and task.task_ended:
            time_elapsed = task.task_ended - task.task_started
            return time_elapsed.total_seconds()
        raise HTTPException(status_code=500,
                            detail="Task hasn't finished running")

    @classmethod
    def __from_db_to_pl(cls, dbtask: DBTask):
        return PLTask(
            id=dbtask.id,
            name=dbtask.name,
            type=dbtask.type,
            description=dbtask.description,
            completed=dbtask.completed,
            task_started=dbtask.task_started,
        )
