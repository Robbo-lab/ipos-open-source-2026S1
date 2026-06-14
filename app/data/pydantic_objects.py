from datetime import datetime

from pydantic import BaseModel


# PLTask stands for Pydantic Task
class PLTask(BaseModel):
    id: int | None = None
    name: str | None = None
    type: str | None = None
    description: str | None = None
    completed: bool | None = False
    task_started: datetime | None = datetime.now()
    task_ended: datetime | None = None
