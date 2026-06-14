import unittest

from app.api.task_handler import TaskHandler
from app.data.database_objects import DBTask
from app.data.pydantic_objects import PLTask
from app.services.database import LocalSession, clear_table


class TaskTests(unittest.TestCase):

    def setUp(self):
        self.session = LocalSession()
        self.example_pltasks = [
            PLTask(name="Task1", type="Agriculture", description="Give names for 100 plants", completed=False),
            PLTask(name="Task2", type="Construction", description="Give price for new airport", completed=True)
        ]
        self.example_dbtask = [
            PLTask(id=1, name="Task1", type="Agriculture", description="Give names for 100 plants", completed=False),
            PLTask(id=2, name="Task2", type="Construction", description="Give price for new airport", completed=True)
        ]

    def test_creating_tasks(self):
        task1 = TaskHandler.create_task("Task1", "Agriculture", "Give names for 100 plants", False)
        task2 = TaskHandler.create_task("Task2", "Construction", "Give price for new airport", True)

        self.assertEqual(self.example_pltasks[0], task1)
        self.assertEqual(self.example_pltasks[1], task2)

    def test_adding_task_to_db(self):
        clear_table(self.session, DBTask)
        self.assertEqual(self.example_dbtask[0], TaskHandler.add_task_to_db(self.session, self.example_pltasks[0]))
        self.assertEqual(self.example_dbtask[1], TaskHandler.add_task_to_db(self.session, self.example_pltasks[1]))

    def test_finding_task_by_name(self):
        clear_table(self.session, DBTask)
        TaskHandler.add_task_to_db(self.session, self.example_pltasks[0])
        TaskHandler.add_task_to_db(self.session, self.example_pltasks[1])

        self.assertEqual(self.example_dbtask[0], TaskHandler.get_task(self.session, "Task1"))
        self.assertEqual(self.example_dbtask[1], TaskHandler.get_task(self.session, "Task2"))

    def test_finding_task_by_id(self):
        clear_table(self.session, DBTask)
        TaskHandler.add_task_to_db(self.session, self.example_pltasks[0])
        TaskHandler.add_task_to_db(self.session, self.example_pltasks[1])

        self.assertEqual(self.example_dbtask[0], TaskHandler.get_task(self.session, 1))
        self.assertEqual(self.example_dbtask[1], TaskHandler.get_task(self.session, 2))

    def test_deleting_tasks(self):
        clear_table(self.session, DBTask)
        TaskHandler.add_task_to_db(self.session, self.example_pltasks[0])
        TaskHandler.add_task_to_db(self.session, self.example_pltasks[1])

        TaskHandler.delete_task(self.session, "Task1")
        TaskHandler.delete_task(self.session, "Task2")

        self.assertFalse(TaskHandler.get_task(self.session, "Task1"))
        self.assertFalse(TaskHandler.get_task(self.session, "Task2"))

    def test_list_tasks_and_filtering(self):
        clear_table(self.session, DBTask)
        TaskHandler.add_task_to_db(self.session, self.example_pltasks[0])
        TaskHandler.add_task_to_db(self.session, self.example_pltasks[1])

        tasks = TaskHandler.list_tasks(self.session)
        self.assertEqual(self.example_dbtask, tasks)
        tasks = TaskHandler.list_tasks(self.session, "Agriculture")
        self.assertEqual([self.example_dbtask[0]], tasks)

    def test_completing_task(self):
        clear_table(self.session, DBTask)
        task = TaskHandler.add_task_to_db(self.session, self.example_pltasks[0])
        task = TaskHandler.complete_task(self.session, task)

        etask = self.example_dbtask[0]
        etask.completed = True
        etask.task_ended = task.task_ended
        self.assertEqual(etask, task)


if __name__ == "__main__":
    unittest.main()
