"""OpenAI API Pydantic V2 Models."""
# unlike the app/llm/providers/gemini/models.py implementation, this has been implemented
# using the https://developers.openai.com/api/docs/guides/structured-outputs spec with the
# help of generative AI, i do not guarantee the correctness of the output compared to the gemini
# implementation and may need to be adjusted

from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Role(StrEnum):
    DEVELOPER = "developer"
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


# --- Content Parts ---


class TextContentPart(BaseModel):
    type: Literal["text"] = "text"
    text: str


class ImageUrl(BaseModel):
    url: str
    detail: Literal["auto", "low", "high"] = "auto"


class ImageContentPart(BaseModel):
    type: Literal["image_url"] = "image_url"
    image_url: ImageUrl


ContentPart = Annotated[
    TextContentPart | ImageContentPart,
    Field(union_mode="left_to_right"),
]


# --- Messages ---


class ChatCompletionMessageToolCall(BaseModel):
    id: str
    type: Literal["function"] = "function"
    function: dict[str, Any]  # name and arguments (JSON string)


class ChatCompletionDeveloperMessage(BaseModel):
    role: Literal[Role.DEVELOPER] = Role.DEVELOPER
    content: str | list[TextContentPart]
    name: str | None = None


class ChatCompletionSystemMessage(BaseModel):
    role: Literal[Role.SYSTEM] = Role.SYSTEM
    content: str | list[TextContentPart]
    name: str | None = None


class ChatCompletionUserMessage(BaseModel):
    role: Literal[Role.USER] = Role.USER
    content: str | list[ContentPart]
    name: str | None = None


class ChatCompletionAssistantMessage(BaseModel):
    role: Literal[Role.ASSISTANT] = Role.ASSISTANT
    content: str | list[TextContentPart] | None = None
    refusal: str | None = None
    name: str | None = None
    tool_calls: list[ChatCompletionMessageToolCall] | None = Field(
        None, alias="tool_calls"
    )


class ChatCompletionToolMessage(BaseModel):
    role: Literal[Role.TOOL] = Role.TOOL
    content: str | list[TextContentPart]
    tool_call_id: str


ChatCompletionRequestMessage = Annotated[
    ChatCompletionDeveloperMessage
    | ChatCompletionSystemMessage
    | ChatCompletionUserMessage
    | ChatCompletionAssistantMessage
    | ChatCompletionToolMessage,
    Field(union_mode="left_to_right"),
]


# --- Tools and Response Format ---


class FunctionObject(BaseModel):
    name: str
    description: str | None = None
    parameters: dict[str, Any] | None = None
    strict: bool | None = None


class ChatCompletionTool(BaseModel):
    type: Literal["function"] = "function"
    function: FunctionObject


class ResponseFormatJsonObject(BaseModel):
    type: Literal["json_object"]


class JsonSchemaObject(BaseModel):
    name: str
    description: str | None = None
    schema_: dict[str, Any] | None = Field(None, alias="schema")
    strict: bool | None = None


class ResponseFormatJsonSchema(BaseModel):
    type: Literal["json_schema"]
    json_schema: JsonSchemaObject


ResponseFormat = Annotated[
    ResponseFormatJsonObject | ResponseFormatJsonSchema,
    Field(union_mode="left_to_right"),
]


# --- Request/Response Payloads ---


class StreamOptions(BaseModel):
    include_usage: bool | None = None


class ChatCompletionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    messages: list[ChatCompletionRequestMessage]
    model: str
    store: bool | None = None
    reasoning_effort: Literal["low", "medium", "high"] | None = None
    frequency_penalty: float | None = Field(None, ge=-2.0, le=2.0)
    logit_bias: dict[str, int] | None = None
    logprobs: bool | None = None
    top_logprobs: int | None = Field(None, ge=0, le=20)
    max_tokens: int | None = None
    max_completion_tokens: int | None = None
    n: int | None = Field(None, ge=1)
    presence_penalty: float | None = Field(None, ge=-2.0, le=2.0)
    response_format: ResponseFormat | None = None
    seed: int | None = None
    service_tier: Literal["auto", "default"] | None = None
    stop: str | list[str] | None = None
    stream: bool | None = False
    stream_options: StreamOptions | None = None
    temperature: float | None = Field(None, ge=0.0, le=2.0)
    top_p: float | None = Field(None, ge=0.0, le=1.0)
    tools: list[ChatCompletionTool] | None = None
    tool_choice: str | dict[str, Any] | None = None
    parallel_tool_calls: bool | None = None
    user: str | None = None


class ChoiceMessage(BaseModel):
    role: Role
    content: str | None = None
    tool_calls: list[ChatCompletionMessageToolCall] | None = None
    refusal: str | None = None


class Choice(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    finish_reason: str | None = Field(None, alias="finishReason")
    index: int
    message: ChoiceMessage
    logprobs: dict[str, Any] | None = None


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    choices: list[Choice]
    created: int
    model: str
    system_fingerprint: str | None = None
    object: Literal["chat.completion"] = "chat.completion"
    usage: Usage | None = None


# --- Stream Response ---


class DeltaMessage(BaseModel):
    role: Role | None = None
    content: str | None = None
    tool_calls: list[ChatCompletionMessageToolCall] | None = None
    refusal: str | None = None


class StreamChoice(BaseModel):
    delta: DeltaMessage
    finish_reason: str | None = None
    index: int
    logprobs: dict[str, Any] | None = None


class ChatCompletionStreamResponse(BaseModel):
    id: str
    choices: list[StreamChoice]
    created: int
    model: str
    system_fingerprint: str | None = None
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    usage: Usage | None = None
