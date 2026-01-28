from pydantic import BaseModel, Field, ConfigDict
from typing import Iterable, Union, Optional, Dict, List, Literal, Sequence
import openai.resources.chat.completions.completions as openai_spec


class OpenAIChatNonStreamingRequest(BaseModel):
    messages: Iterable[openai_spec.ChatCompletionMessageParam]
    model: Union[str, openai_spec.ChatModel]
    audio: Optional[openai_spec.ChatCompletionAudioParam] | openai_spec.Omit = openai_spec.omit
    frequency_penalty: Optional[float] | openai_spec.Omit = openai_spec.omit
    function_call: openai_spec.completion_create_params.FunctionCall | openai_spec.Omit = openai_spec.omit
    functions: Iterable[openai_spec.completion_create_params.Function] | openai_spec.Omit = openai_spec.omit
    logit_bias: Optional[Dict[str, int]] | openai_spec.Omit = openai_spec.omit
    logprobs: Optional[bool] | openai_spec.Omit = openai_spec.omit
    max_completion_tokens: Optional[int] | openai_spec.Omit = openai_spec.omit
    max_tokens: Optional[int] | openai_spec.Omit = openai_spec.omit
    metadata: Optional[openai_spec.Metadata] | openai_spec.Omit = openai_spec.omit
    modalities: Optional[List[Literal["text", "audio"]]] | openai_spec.Omit = openai_spec.omit
    n: Optional[int] | openai_spec.Omit = openai_spec.omit
    parallel_tool_calls: bool | openai_spec.Omit = openai_spec.omit
    prediction: Optional[openai_spec.ChatCompletionPredictionContentParam] | openai_spec.Omit = openai_spec.omit
    presence_penalty: Optional[float] | openai_spec.Omit = openai_spec.omit
    prompt_cache_key: str | openai_spec.Omit = openai_spec.omit
    prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | openai_spec.Omit = openai_spec.omit
    reasoning_effort: Optional[openai_spec.ReasoningEffort] | openai_spec.Omit = openai_spec.omit
    response_format: openai_spec.completion_create_params.ResponseFormat | openai_spec.Omit = openai_spec.omit
    safety_identifier: str | openai_spec.Omit = openai_spec.omit
    seed: Optional[int] | openai_spec.Omit = openai_spec.omit
    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | openai_spec.Omit = openai_spec.omit
    stop: Union[Optional[str], openai_spec.SequenceNotStr[str], None] | openai_spec.Omit = openai_spec.omit
    store: Optional[bool] | openai_spec.Omit = openai_spec.omit
    stream: Optional[Literal[False]] | openai_spec.Omit = openai_spec.omit
    stream_options: Optional[openai_spec.ChatCompletionStreamOptionsParam] | openai_spec.Omit = openai_spec.omit
    temperature: Optional[float] | openai_spec.Omit = openai_spec.omit
    tool_choice: openai_spec.ChatCompletionToolChoiceOptionParam | openai_spec.Omit = openai_spec.omit
    tools: Iterable[openai_spec.ChatCompletionToolUnionParam] | openai_spec.Omit = openai_spec.omit
    top_logprobs: Optional[int] | openai_spec.Omit = openai_spec.omit
    top_p: Optional[float] | openai_spec.Omit = openai_spec.omit
    user: str | openai_spec.Omit = openai_spec.omit
    verbosity: Optional[Literal["low", "medium", "high"]] | openai_spec.Omit = openai_spec.omit
    web_search_options: openai_spec.completion_create_params.WebSearchOptions | openai_spec.Omit = openai_spec.omit
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: openai_spec.Headers | None = None
    extra_query: openai_spec.Query | None = None
    extra_body: openai_spec.Body | None = None
    timeout: float | openai_spec.httpx.Timeout | None | openai_spec.NotGiven = openai_spec.not_given


class OpenAIChatStreamingRequest(BaseModel):
    messages: Iterable[openai_spec.ChatCompletionMessageParam]
    model: Union[str, openai_spec.ChatModel]
    stream: Literal[True]
    audio: Optional[openai_spec.ChatCompletionAudioParam] | openai_spec.Omit = openai_spec.omit
    frequency_penalty: Optional[float] | openai_spec.Omit = openai_spec.omit
    function_call: openai_spec.completion_create_params.FunctionCall | openai_spec.Omit = openai_spec.omit
    functions: Iterable[openai_spec.completion_create_params.Function] | openai_spec.Omit = openai_spec.omit
    logit_bias: Optional[Dict[str, int]] | openai_spec.Omit = openai_spec.omit
    logprobs: Optional[bool] | openai_spec.Omit = openai_spec.omit
    max_completion_tokens: Optional[int] | openai_spec.Omit = openai_spec.omit
    max_tokens: Optional[int] | openai_spec.Omit = openai_spec.omit
    metadata: Optional[openai_spec.Metadata] | openai_spec.Omit = openai_spec.omit
    modalities: Optional[List[Literal["text", "audio"]]] | openai_spec.Omit = openai_spec.omit
    n: Optional[int] | openai_spec.Omit = openai_spec.omit
    parallel_tool_calls: bool | openai_spec.Omit = openai_spec.omit
    prediction: Optional[openai_spec.ChatCompletionPredictionContentParam] | openai_spec.Omit = openai_spec.omit
    presence_penalty: Optional[float] | openai_spec.Omit = openai_spec.omit
    prompt_cache_key: str | openai_spec.Omit = openai_spec.omit
    prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | openai_spec.Omit = openai_spec.omit
    reasoning_effort: Optional[openai_spec.ReasoningEffort] | openai_spec.Omit = openai_spec.omit
    response_format: openai_spec.completion_create_params.ResponseFormat | openai_spec.Omit = openai_spec.omit
    safety_identifier: str | openai_spec.Omit = openai_spec.omit
    seed: Optional[int] | openai_spec.Omit = openai_spec.omit
    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | openai_spec.Omit = openai_spec.omit
    stop: Union[Optional[str], openai_spec.SequenceNotStr[str], None] | openai_spec.Omit = openai_spec.omit
    store: Optional[bool] | openai_spec.Omit = openai_spec.omit
    stream_options: Optional[openai_spec.ChatCompletionStreamOptionsParam] | openai_spec.Omit = openai_spec.omit
    temperature: Optional[float] | openai_spec.Omit = openai_spec.omit
    tool_choice: openai_spec.ChatCompletionToolChoiceOptionParam | openai_spec.Omit = openai_spec.omit
    tools: Iterable[openai_spec.ChatCompletionToolUnionParam] | openai_spec.Omit = openai_spec.omit
    top_logprobs: Optional[int] | openai_spec.Omit = openai_spec.omit
    top_p: Optional[float] | openai_spec.Omit = openai_spec.omit
    user: str | openai_spec.Omit = openai_spec.omit
    verbosity: Optional[Literal["low", "medium", "high"]] | openai_spec.Omit = openai_spec.omit
    web_search_options: openai_spec.completion_create_params.WebSearchOptions | openai_spec.Omit = openai_spec.omit
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: openai_spec.Headers | None = None
    extra_query: openai_spec.Query | None = None
    extra_body: openai_spec.Body | None = None
    timeout: float | openai_spec.httpx.Timeout | None | openai_spec.NotGiven = openai_spec.not_given
