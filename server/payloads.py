from pydantic import BaseModel, Field, ConfigDict
from typing import Any, List, Optional, Literal, Union, Sequence



class CohereChatV1StreamRequest(BaseModel):
    """request for performing chat with Cohere's chat API V1
    
    See https://docs.cohere.com/v1/reference/chat for details.
    """
    message: str
    stream: bool = False
    model: Optional[str] = None
    preamble: Optional[str] = None
    chat_history: Optional[list[dict]] = None
    conversation_id: Optional[str] = None
    prompt_truncation: Optional[Literal["OFF", "AUTO", "AUTO_PRESERVE_ORDER"]] = None
    connectors: Optional[list[dict]] = None
    search_queries_only: Optional[bool] = False
    documents: Optional[list[dict[str, str]]] = None
    citation_quality: Optional[Literal["fast", "accurate", "off"]] = "accurate"
    temperature: float = 0.3
    max_tokens: Optional[int] = None
    max_input_tokens: Optional[int] = None
    k: Optional[int] = 0
    p: Optional[float] = 0.75
    seed: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    tools: Optional[list[dict]] = None
    tool_results: Optional[list[dict]] = None
    force_single_step: Optional[bool] = False
    response_format: Optional[dict] = None
    safety_mode: Optional[Literal["CONTEXTUAL", "STRICT", "NONE"]] = "CONTEXTUAL"


class CohereChatV1NonStreamRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    message: str
    accepts: Optional[Literal["text/event-stream"]] = None
    model: Optional[str] = None
    preamble: Optional[str] = None
    chat_history: Optional[Sequence[dict]] = None  # actual element type is Message
    conversation_id: Optional[str] = None
    prompt_truncation: Optional[Union[Literal["OFF", "AUTO", "AUTO_PRESERVE_ORDER"], Any]] = None
    connectors: Optional[Sequence[dict]] = None # actual element type is ChatConnector
    search_queries_only: Optional[bool] = None
    documents: Optional[Sequence[dict[str, str]]] = None # actual element type is ChatDocument
    citation_quality: Optional[Union[Literal["ENABLED", "DISABLED", "FAST", "ACCURATE", "OFF"], Any]] = None  # actual type is ChatRequestCitationQuality
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    max_input_tokens: Optional[int] = None
    k: Optional[int] = None
    p: Optional[float] = None
    seed: Optional[int] = None
    stop_sequences: Optional[Sequence[str]] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    raw_prompting: Optional[bool] = Field(default=None)
    tools: Optional[Sequence[dict]] = None  # acutual element type is Tool
    tool_results: Optional[Sequence[dict]] = None  # actual element type is ToolResult
    force_single_step: Optional[bool] = None
    response_format: Optional[dict] = None  # actual type is ResponseFormat
    safety_mode: Optional[Union[Literal["CONTEXTUAL", "STRICT", "NONE"], Any]] = None  # actual type is ChatRequestSafetyMode
    request_options: Optional[dict] = None  # actual type is RequestOptions


# class CohereChatV1Response(BaseModel):
#     """response from Cohere's chat API V1
    
#     See https://docs.cohere.com/v1/reference/chat for details.
#     """
#     text: str
#     generation_id: Optional[str] = None
#     response_id: Optional[str] = None
#     citations: Optional[List[dict]] = None
#     documents: Optional[list[dict[str, str]]] = None
#     is_search_required: Optional[bool] = None
#     search_queries: Optional[List[dict]] = None
#     search_results: Optional[List[dict]] = None
#     finish_reason: Optional[Literal[
#         "COMPLETE", "STOP_SEQUENCE", "ERROR", "ERROR_TOXIC"
#         "ERROR_LIMIT", "USER_CANCEL", "MAX_TOKENS"
#     ]] = None
#     tool_calls: Optional[List[dict]] = None
#     chat_history: Optional[List[dict]] = None
#     meta: Optional[dict] = None


class CohereChatV2Request(BaseModel):
    """request for performing chat with Cohere's chat API V2
    
    See https://docs.cohere.com/v2/reference/chat for details.
    """
    messages: list[dict]
    model: str
    stream: bool = False
    tools: Optional[list[dict]] = None
    documents: Optional[list[Union[str, dict]]] = None
    citation_options: Optional[dict] = None
    response_format: Optional[dict] = None
    safety_mode: Optional[Literal["CONTEXTUAL", "STRICT", "OFF"]] = "CONTEXTUAL"
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    temperature: float = 0.3
    seed: Optional[int] = None
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    k: int = 0
    p: float = 0.75
    logprobs: bool = False
    tool_choice: Optional[Literal["REQUIRED", "NONE"]] = None
    strict_tools: Optional[bool] = None


class CohereChatV2NonStreamRequest(BaseModel):
    model: str
    messages: list[dict]  # actual element type is ChatMessages
    tools: Optional[Sequence[dict]] = None  # actual element type is ToolV2
    strict_tools: Optional[bool] = None
    documents: Optional[Sequence[Union[str, dict]]] = None  # actual element type is Union[str, Document]
    citation_options: Optional[dict] = None  # actual type is CitationOptions
    response_format: Optional[dict] = None  # actual type is ResponseFormatV2
    safety_mode: Optional[Union[Literal["CONTEXTUAL", "STRICT", "OFF"], Any]] = None  # actual type is V2ChatRequestSafetyMode
    max_tokens: Optional[int] = None
    stop_sequences: Optional[Sequence[str]] = None
    temperature: Optional[float] = None
    seed: Optional[int] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    k: Optional[int] = None
    p: Optional[float] = None
    logprobs: Optional[bool] = None
    tool_choice: Optional[Union[Literal["REQUIRED", "NONE"], Any]] = None  # actual type is V2ChatRequestToolChoice
    thinking: Optional[dict] = None  # actual type is Thinking
    priority: Optional[int] = None
    request_options: Optional[dict] = None  # actual type is RequestOptions

class CohereChatV2Response(BaseModel):
    """response from Cohere's chat API V2
    
    See https://docs.cohere.com/v2/reference/chat for details.
    """
    id: str
    finish_reason: Literal["COMPLETE", "STOP_SEQUENCE", "MAX_TOKENS", "TOOL_CALL", "ERROR"]
    message: dict
    usage: Optional[dict] = None
    logprobs: Optional[list[dict]] = None

class PromptHolder(BaseModel):
    prompt: str

class PromptToDetectInfo(PromptHolder):
    experiment: bool = True

class PromptToValidate(PromptHolder):
    with_lang_detection: bool = True

class LangJudgmentHistory(BaseModel):
    text: str
    lang: str
    prev_lang: str | None = None
    is_latin: bool = False

class LangInfo(BaseModel):
    final: str
    for_whole: str
    for_parts: list[LangJudgmentHistory] | None
    detail: dict[str, Any] | None = None
    prompt: str
    parameters: dict[str, Any]
