from __future__ import annotations

from fastmcp.prompts import Message


def task_manager_prompt(user_request: str) -> list[Message]:
    """Creates a system + user prompt for task manager tool usage."""
    instructions = (
        "You are a task manager assistant that helps users manage tasks using available tools. "
        "Always follow these rules:\n"
        "1. Use task tools when the user wants to create, find, list, complete, or delete tasks.\n"
        "2. Do not invent task names, task IDs, dates, or task details.\n"
        "3. Use create_task only when the user clearly wants to add a new task.\n"
        "4. Use delete_task only when the user clearly asks to delete or remove a task.\n"
        "5. Use complete_task when the user wants to finish, complete, or mark a task as done.\n"
        "6. Use get_task_by_name or get_task_by_id when the user wants information about one specific task.\n"
        "7. Use list_tasks when the user wants to see multiple tasks, such as pending or completed tasks.\n"
        "8. If required information is missing, ask a short clarification question instead of guessing.\n"
        "9. After using a tool, explain the result clearly using the tool response."
    )

    user_prompt = (
        f"Handle this task manager request: {user_request}\n"
        "Decide which available task tool should be used, call it with the correct arguments, "
        "and return a clear final response to the user."
    )

    return [
        Message(role="assistant", content=instructions),
        Message(role="user", content=user_prompt),
    ]


# TODO
def api_usage_prompt():
    pass


PROMPT_DEFINITIONS = [
    {
        "name": "task_manager",
        "description": "Guide the LLM to choose and use task manager tools correctly.",
        "func": task_manager_prompt,
    },
]
