from __future__ import annotations

from fastmcp.prompts import Message


def explain_conversion_prompt(
    input_value: str,
    input_unit: str,
    target_unit: str,
) -> list[Message]:
    """Creates a tutoring-style system + user prompt for unit conversion explanations."""
    instructions = (
        "You are a clear, patient, and encouraging tutor helping students learn unit conversions. "
        "Always follow these rules:\n"
        "1. Show the conversion formula clearly.\n"
        "2. Substitute the given values into the formula.\n"
        "3. Show the calculation step-by-step.\n"
        "4. Give the final answer with the correct unit.\n"
        "5. Keep your entire response to a maximum of 5 steps.\n"
        "Use simple language suitable for beginners."
    )

    user_prompt = (
        f"Explain how to convert {input_value} {input_unit} to {target_unit}. "
        "Return both the step-by-step math and the final numerical result."
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
        "name": "explain_conversion",
        "description": "Guide a learner through the math for a specific conversion.",
        "func": explain_conversion_prompt,
    },
]
