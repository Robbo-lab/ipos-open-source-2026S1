import json
from collections.abc import Iterable
from typing import Any

from fastmcp import FastMCP
from fastmcp.resources import BinaryResource, TextResource


def register_resources(
    mcp: FastMCP,
    definitions: Iterable[dict[str, Any]],
    uri_template: str = "resource://converter/{name}",
    include_static: bool = True,
) -> None:
    """Register a dynamic resource route that serves all definitions via URI parameters."""
    lookup_table = {}

    for define in definitions:
        lookup_table[define["name"]] = define

    def as_text(value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return json.dumps(value, indent=2)
        return str(value)

    def handler(name: str) -> str:
        if name not in lookup_table:
            raise ValueError(f"Unknown resource name '{name}'")
        definition = lookup_table[name]
        content = definition["func"]()
        # return as_text(content)
        if not isinstance(content, (bytes, bytearray)):
            return as_text(content)
        return content

    # Dynamic template (with parameters)
    mcp.resource(
        uri_template,
        name="Converter resources",
        description="Dynamic converter resources",
        mime_type="text/plain",
    )(handler)

    # Concrete URIs for discoverability in inspectors
    if include_static:
        for definition in definitions:
            uri = uri_template.replace("{name}", definition["name"])
            mime = definition.get("mime_type", "text/plain")
            content = definition["func"]()
            payload = (
                content if isinstance(content, (bytes, bytearray)) else as_text(content)
            )
            if isinstance(payload, (bytes, bytearray)):
                resource = BinaryResource(
                    uri=uri,
                    name=definition.get("display_name", definition["name"]),
                    mime_type=mime,
                    data=bytes(payload),
                )
            else:
                resource = TextResource(
                    uri=uri,
                    name=definition.get("display_name", definition["name"]),
                    mime_type=mime,
                    text=payload,
                )
            mcp.add_resource(resource)
