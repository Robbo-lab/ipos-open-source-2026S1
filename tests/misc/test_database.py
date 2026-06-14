import unittest

from app.data.database_objects import DBTestObject
from app.services.database import DataBaseMethods, LocalSession, clear_table


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.session = LocalSession()

    def test_add_to_db(self):
        clear_table(self.session, DBTestObject)
        obj = DBTestObject(id=1, name="Test1", type="Flying")

        new_obj = DataBaseMethods.add_object(self.session, obj)

        self.assertEqual(obj, new_obj)

    def test_get_object_by_name(self):
        clear_table(self.session, DBTestObject)
        db_obj = DataBaseMethods.add_object(self.session, DBTestObject(id=1, name="Test1", type="Flying"))

        self.assertEqual(db_obj, DataBaseMethods.get_object_by_name(self.session, DBTestObject, "Test1"))

    def test_get_object_by_id(self):
        clear_table(self.session, DBTestObject)
        db_obj = DataBaseMethods.add_object(self.session, DBTestObject(id=1, name="Test1", type="Flying"))

        self.assertEqual(db_obj, DataBaseMethods.get_object_by_id(self.session, DBTestObject, 1))

    def test_db_query(self):
        clear_table(self.session, DBTestObject)
        db_obj1 = DataBaseMethods.add_object(self.session, DBTestObject(id=1, name="Test1", type="Flying"))
        db_obj2 = DataBaseMethods.add_object(self.session, DBTestObject(id=2, name="Test2", type="Ground"))

        self.assertNotEqual([db_obj1, db_obj2], DataBaseMethods.query_db(self.session, DBTestObject, "type", "Flying"))
        self.assertEqual([db_obj1], DataBaseMethods.query_db(self.session, DBTestObject, "type", "Flying"))

    def test_object_delete(self):
        clear_table(self.session, DBTestObject)

        db_obj1 = DataBaseMethods.add_object(self.session, DBTestObject(id=1, name="Test1", type="Flying"))
        self.assertEqual(db_obj1, DataBaseMethods.get_object_by_name(self.session, DBTestObject, "Test1"))

        DataBaseMethods.delete_object(self.session, db_obj1)

        self.assertNotEqual(db_obj1, DataBaseMethods.get_object_by_name(self.session, DBTestObject, "Test1"))


if __name__ == "__main__":
    unittest.main()
