from __future__ import annotations

import os
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

if TYPE_CHECKING:
    from app.data.database_objects import DBTask

Database_url = os.getenv("DATABASE_URL", "sqlite:///./Database.db")
Engine = create_engine(Database_url, connect_args={"check_same_thread": False})
LocalSession = sessionmaker(bind=Engine, autocommit=False, autoflush=False)
Base = declarative_base()


class DataBaseMethods:
    """
    Database class is a static class that creates
    an in Memory Database Engine and
    allows the creation of new data objects,
    as well as finding objects saved through
    the ID or Name.

    Args:
        None

    Returns:
        None
    """

    # Adds a data object to database
    @staticmethod
    def add_object(db: Session, new_object: DBTask) -> DBTask:
        """
        Adds a database object to the database.

        Args:
            db (Session): Database session,
            can be grabbed with get_db()
            new_object (DBTask): New
            database object to be added
            must be inside the database_objects.py module

        Returns:
            DBTask: returns the entered object
             if it was successfully added
        """
        try:
            print(new_object)
            print(db)
            db.add(new_object)
            db.commit()
            db.refresh(new_object)
            return new_object
        except Exception as err:
            db.rollback()
            raise HTTPException(
                status_code=404, detail="Object already exists"
            ) from err

    # deletes a data object from database
    @staticmethod
    def delete_object(db: Session, object_to_delete: DBTask) -> bool:
        """
        Deletes a database object from the database.

        Args:
            db (Session): Database session, can be grabbed with get_db()
            object_to_delete (DBTask): New database object to be added
            must be inside the database_objects.py module

        Returns:
            boolean: False if failed & True if succeeded
        """
        if not object_to_delete:
            return False

        try:
            db.delete(object_to_delete)
            db.commit()
            return True
        except Exception as err:
            db.rollback()
            raise HTTPException(
                status_code=404, detail=f"Object does not exist, {err}"
            ) from err

    # Gets an object by Name from the database
    @staticmethod
    def get_object_by_name(db: Session, obj_ref, name: str) -> DBTask | None:
        """
        Gets an object based on the name entered.

        Args:
            db (Session): Database session, can be grabbed with get_db()
            name (string): Name of the object
            obj_ref (DBTask): Object reference, so an object from
            the database_objects.py module

        Returns:
            DBTask: returns the object if it was successfully found, otherwise None
        """
        if not obj_ref.name:
            raise HTTPException(status_code=500, detail="Object must have a name")

        try:
            param = obj_ref.name
            return db.query(obj_ref).filter(param == name).first()
        except Exception:
            HTTPException(
                status_code=404, detail=f"Object with name: {name}, does not exist"
            )

    # Gets an object by ID from the database, data object must have ID field
    @staticmethod
    def get_object_by_id(db: Session, obj_ref, object_id: int) -> DBTask | None:
        """
        Gets an object based on the id entered.

        Args:
            db (Session): Database session, can be grabbed with get_db()
            object_id (int): ID of the object
            obj_ref (DBTask): Object reference, so an object from
            the database_objects.py module

        Returns:
            DBTask: returns the object if it was successfully found
        """
        try:
            param = obj_ref.id
            return db.query(obj_ref).filter(param == object_id).first()
        except Exception:
            HTTPException(
                status_code=404, detail=f"Object with id: {id}, does not exist"
            )

    @staticmethod
    def query_db(db: Session, obj_ref, field: str, value) -> list[DBTask]:
        if value is None:
            try:
                return db.query(obj_ref).filter(obj_ref.id).all()
            except Exception as err:
                raise HTTPException(
                    status_code=404,
                    detail=f"Object with field: {field}, does not exist",
                ) from err
        else:
            try:
                param = getattr(obj_ref, field)
                return db.query(obj_ref).filter(param == value).all()
            except Exception as err:
                raise HTTPException(
                    status_code=404,
                    detail=f"Object with field: {field}, does not exist",
                ) from err


def get_session() -> Session:
    return Session()


def get_session_api():
    session = LocalSession()
    try:
        yield session
    finally:
        session.close()


def clear_table(session, db_object):

    try:
        deleted = session.query(db_object).delete(synchronize_session=False)

        session.commit()

        print(f"Deleted {deleted} rows")

    except Exception as e:
        session.rollback()

        print("CLEAR ERROR:", e)

        raise

    finally:
        session.close()
