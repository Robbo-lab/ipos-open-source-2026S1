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


def api_usage_prompt(
    operation: str,
    resource_text: str,
) -> list[Message]:
    """Provides instructions on how to use a specific API operation."""
    instructions = (
        "You are an expert API assistant. "
        "Your task is to explain how to use the specified API operation based on the provided API reference. "
        "Keep your explanation clear, concise, and provide examples if possible."
    )

    user_prompt = (
        f"Explain how to use the '{operation}' operation.\n\n"
        f"API Reference:\n{resource_text}"
    )

    return [
        Message(role="assistant", content=instructions),
        Message(role="user", content=user_prompt),
    ]


PROMPT_DEFINITIONS = [
    {
        "name": "explain_conversion",
        "description": "Guide a learner through the math for a specific conversion.",
        "func": explain_conversion_prompt,
    },
    {
        "name": "api_usage",
        "description": "Explain how to use a specific API operation.",
        "func": api_usage_prompt,
    },
]
