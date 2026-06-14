from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.mysql import DATETIME

from app.services.database import Base, Engine


# DBTask stands for Data Base Task
class DBTask(Base):
    __tablename__ = "task_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    type = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=True)
    completed = Column(Boolean(), nullable=True, default=False)
    task_started = Column(DATETIME(), nullable=True, default=datetime.now())
    task_ended = Column(DATETIME(), nullable=True)


class DBTestObject(Base):
    __tablename__ = "test_object"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    type = Column(String(100), nullable=False)


# Has to be last line
Base.metadata.create_all(bind=Engine)
