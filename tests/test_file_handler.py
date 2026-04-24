from pprint import pprint
from src.file_handler import load_tasks, save_tasks
from src.task import Task


def test_file_handler():
    """
    Test the binary file content by loading tasks
    and printing them in a readable format.
    """
    # Load tasks from the binary file
    tasks = load_tasks()

    if not tasks:
        print("No tasks found in the binary file.")
    else:
        print("Tasks loaded from the binary file:")
        pprint([task.to_dict() for task in tasks])  # Convert tasks to dict


if __name__ == "__main__":
    # Test Script: Save sample tasks and load them back
    sample_tasks = [
        Task("Task 1", "Description 1", "12-12-2024", "pending"),
        Task("Task 2", "Description 2", "15-12-2024", "completed"),
    ]

    # Save tasks to the binary file
    save_tasks(sample_tasks)
    print("Sample tasks saved to binary file.")

    # Load and pretty-print tasks from the binary file
    test_file_handler()
