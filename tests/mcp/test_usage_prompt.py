import asyncio

from main import mcp


async def main():
    prompt = await mcp.get_prompt("api_usage")

    api_reference = """Available endpoints:
- GET /health → Check server status
- POST /convert → Convert between units
- GET /history → View recent conversions"""

    result = await prompt.render({
        "operation": "convert",
        "resource_text": api_reference,
    })

    print(f"Resource provided to the model:\n{api_reference}\n")

    for msg in result.messages:
        print(f"[{msg.role.upper()}]")
        content = msg.content.text if hasattr(msg.content, "text") else str(msg.content)
        print(content.strip())
        print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
