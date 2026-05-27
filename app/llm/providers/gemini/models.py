"""Gemini API Pydantic V2 Models."""
# Design Rationale:
# - I've tried to follow the Gemini rest API specification as closely as possible while
#   trying to maintain Python's snake case, I've also used used runtime type narrowing
#   with some helpers I added to the `Part` model. I've also built support for both
#   unary (generateContent) and streaming (SSE) workflows.

# Resources & Specifications:
# - Google AI Studio API Reference:
#   https://ai.google.dev/api/rest/v1beta/models/generateContent
# - Model Context Protocol (MCP) Integration:
#   https://modelcontextprotocol.io
# - PEP 742 (TypeIs):
#   https://peps.python.org/pep-0742/

from enum import StrEnum
from typing import Annotated, Any, TypeIs

from pydantic import BaseModel, ConfigDict, Field


class Role(StrEnum):
    USER = "user"
    MODEL = "model"


class FunctionCall(BaseModel):
    name: str
    args: dict[str, Any]


class FunctionResponse(BaseModel):
    name: str
    response: dict[str, Any]


class InlineData(BaseModel):
    mime_type: str
    data: str


class TextPart(BaseModel):
    text: str


class FunctionCallPart(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    function_call: FunctionCall = Field(..., alias="functionCall")


class FunctionResponsePart(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    function_response: FunctionResponse = Field(..., alias="functionResponse")


class InlineDataPart(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    inline_data: InlineData = Field(..., alias="inlineData")


# Use Pydantic V2 Annotated Union with left-to-right matching,
# Since Gemini parts are mutually exclusive keys (can change in the future)
Part = Annotated[
    TextPart | FunctionCallPart | FunctionResponsePart | InlineDataPart,
    Field(union_mode="left_to_right"),
]


# Runtime Type Narrowing Helpers
def is_text_part(part: Part) -> TypeIs[TextPart]:
    return hasattr(part, "text")


def is_function_call_part(part: Part) -> TypeIs[FunctionCallPart]:
    return hasattr(part, "function_call")


def is_function_response_part(part: Part) -> TypeIs[FunctionResponsePart]:
    return hasattr(part, "function_response")


class Content(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    role: Role | str
    parts: list[Part]


# --- Tools and Configuration ---


class FunctionDeclaration(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any]


class Tool(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    function_declarations: list[FunctionDeclaration] = Field(
        default_factory=list, alias="functionDeclarations"
    )


class FunctionCallingConfigMode(StrEnum):
    AUTO = "AUTO"
    ANY = "ANY"
    NONE = "NONE"


class FunctionCallingConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    mode: FunctionCallingConfigMode = FunctionCallingConfigMode.AUTO
    allowed_function_names: list[str] | None = Field(None, alias="allowedFunctionNames")


class ToolConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    function_calling_config: FunctionCallingConfig = Field(
        ..., alias="functionCallingConfig"
    )


# --- Request/Response Payloads ---


class GenerationConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    candidate_count: int | None = Field(None, alias="candidateCount")
    stop_sequences: list[str] | None = Field(None, alias="stopSequences")
    max_output_tokens: int | None = Field(None, alias="maxOutputTokens")
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None


class GenerateContentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    contents: list[Content]
    tools: list[Tool] | None = None
    tool_config: ToolConfig | None = Field(None, alias="toolConfig")
    generation_config: GenerationConfig | None = Field(None, alias="generationConfig")
    system_instruction: Content | None = Field(None, alias="systemInstruction")


class Candidate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Content
    finish_reason: str | None = Field(None, alias="finishReason")
    index: int | None = None
    # safety_ratings: list[dict] | None = Field(None, alias="safetyRatings")


class UsageMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    prompt_token_count: int = Field(..., alias="promptTokenCount")
    candidates_token_count: int = Field(..., alias="candidatesTokenCount")
    total_token_count: int = Field(..., alias="totalTokenCount")


class GenerateContentResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    candidates: list[Candidate] = Field(default_factory=list)
    usage_metadata: UsageMetadata | None = Field(None, alias="usageMetadata")
