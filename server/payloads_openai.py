from pydantic import BaseModel, Field, ConfigDict
from typing import Iterable, Union, Optional, Dict, List, Literal, Sequence
import openai.resources.chat.completions.completions as openai_spec


class OpenAIChatNonStreamingRequest(BaseModel):
    messages: Iterable[openai_spec.ChatCompletionMessageParam]
    model: Union[str, openai_spec.ChatModel]
    audio: Optional[openai_spec.ChatCompletionAudioParam] = None
    frequency_penalty: Optional[float] = None
    function_call: Optional[openai_spec.completion_create_params.FunctionCall] = None
    functions: Iterable[openai_spec.completion_create_params.Function] = None
    logit_bias: Optional[Dict[str, int]] = None
    logprobs: Optional[bool] = None
    max_completion_tokens: Optional[int] = None
    max_tokens: Optional[int] = None
    metadata: Optional[openai_spec.Metadata] = None
    modalities: Optional[List[Literal["text", "audio"]]] = None
    n: Optional[int] = None
    parallel_tool_calls: Optional[bool] = None
    prediction: Optional[openai_spec.ChatCompletionPredictionContentParam] = None
    presence_penalty: Optional[float] = None
    prompt_cache_key: Optional[str] = None
    prompt_cache_retention: Optional[Literal["in-memory", "24h"]] = None
    reasoning_effort: Optional[openai_spec.ReasoningEffort] = None
    response_format: Optional[openai_spec.completion_create_params.ResponseFormat] = None
    safety_identifier: Optional[str] = None
    seed: Optional[int] = None
    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] = None
    stop: Union[Optional[str], openai_spec.SequenceNotStr[str], None] = None
    store: Optional[bool] = None
    stream: Optional[Literal[False]] = None
    stream_options: Optional[openai_spec.ChatCompletionStreamOptionsParam] = None
    temperature: Optional[float] = None
    tool_choice: Optional[openai_spec.ChatCompletionToolChoiceOptionParam] = None
    tools: Iterable[openai_spec.ChatCompletionToolUnionParam] = None
    top_logprobs: Optional[int] = None
    top_p: Optional[float] = None
    user: Optional[str] = None
    verbosity: Optional[Literal["low", "medium", "high"]] = None
    web_search_options: Optional[openai_spec.completion_create_params.WebSearchOptions] = None
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Optional[openai_spec.Headers | None] = None
    extra_query: Optional[openai_spec.Query | None] = None
    extra_body: Optional[openai_spec.Body | None] = None
    timeout: float | openai_spec.httpx.Timeout | None | openai_spec.NotGiven = openai_spec.not_given


class OpenAIChatStreamingRequest(BaseModel):
    messages: Iterable[openai_spec.ChatCompletionMessageParam]
    model: Union[str, openai_spec.ChatModel]
    stream: Literal[True]
    audio: Optional[openai_spec.ChatCompletionAudioParam] = None
    frequency_penalty: Optional[float] = None
    function_call: Optional[openai_spec.completion_create_params.FunctionCall] = None
    functions: Iterable[openai_spec.completion_create_params.Function] = None
    logit_bias: Optional[Dict[str, int]] = None
    logprobs: Optional[bool] = None
    max_completion_tokens: Optional[int] = None
    max_tokens: Optional[int] = None
    metadata: Optional[openai_spec.Metadata] = None
    modalities: Optional[List[Literal["text", "audio"]]] = None
    n: Optional[int] = None
    parallel_tool_calls: Optional[bool] = None
    prediction: Optional[openai_spec.ChatCompletionPredictionContentParam] = None
    presence_penalty: Optional[float] = None
    prompt_cache_key: Optional[str] = None
    prompt_cache_retention: Optional[Literal["in-memory", "24h"]] = None
    reasoning_effort: Optional[openai_spec.ReasoningEffort] = None
    response_format: Optional[openai_spec.completion_create_params.ResponseFormat] = None
    safety_identifier: Optional[str] = None
    seed: Optional[int] = None
    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] = None
    stop: Union[Optional[str], openai_spec.SequenceNotStr[str], None] = None
    store: Optional[bool] = None
    stream_options: Optional[openai_spec.ChatCompletionStreamOptionsParam] = None
    temperature: Optional[float] = None
    tool_choice: Optional[openai_spec.ChatCompletionToolChoiceOptionParam] = None
    tools: Iterable[openai_spec.ChatCompletionToolUnionParam] = None
    top_logprobs: Optional[int] = None
    top_p: Optional[float] = None
    user: Optional[str] = None
    verbosity: Optional[Literal["low", "medium", "high"]] = None
    web_search_options: Optional[openai_spec.completion_create_params.WebSearchOptions] = None
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Optional[openai_spec.Headers | None] = None
    extra_query: Optional[openai_spec.Query | None] = None
    extra_body: Optional[openai_spec.Body | None] = None
    timeout: float | openai_spec.httpx.Timeout | None | openai_spec.NotGiven = openai_spec.not_given
