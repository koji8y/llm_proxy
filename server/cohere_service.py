from __future__ import annotations
from typing import Iterator, Literal, Iterable, Callable, TypeVar, Collection
from fastapi import HTTPException
from server.payloads import CohereChatV1StreamRequest, CohereChatV1NonStreamRequest, CohereChatV2Request
from pydantic import BaseModel

import cohere
import json
from fastapi.responses import StreamingResponse
from cohere import StreamedChatResponse, StreamedChatResponseV2
from cohere.core.api_error import ApiError
from cohere.base_client import OMIT
from cohere.v2.types.v2chat_stream_response import V2ChatStreamResponse

import ast
import logging
import sys
from logging import Logger

from server.payloads_openai import openai_spec
from server.generic_service import create_generation_id
from server.common_service import StreamingResponseHTTPExceptionDispatcher
from resources.environment import Environment


T = TypeVar('T')
E = TypeVar('E', bound=Exception)


class StreamingResponseHTTPExceptionDispatcherForCohere(StreamingResponseHTTPExceptionDispatcher):
    def __init__(
        self,
        response: Iterator[BaseModel | dict[str, ...]],
        api_version: Literal["v1", "v2", "openai"],
        exception_type_to_catch: type[E] = ApiError,
        log_to_info: bool = False,
    ):
        super().__init__(
            response=response,
            exception_type_to_catch=ApiError,
            log_to_info=log_to_info,
        )
        api_versions = ("v1", "v2", "openai")
        if api_version not in api_versions:
            raise ValueError(f"Invalid API version: {api_version}. Expected 'v1', 'v2', or 'openai'.")
        self.exception_type_to_catch = exception_type_to_catch
        self._stringify_proper = (
            self._stringify_v1 if api_version == "v1" else
            self._stringify_v2 if api_version == "v2" else
            self._stringify_openai
        )
        self._set_generation_id_proper = (
            self._set_generation_id_for_v1 if api_version == "v1" else
            self._set_generation_id_for_v2 if api_version == "v2" else
            self._set_generation_id_for_openai
        )

    def _stringify(self, a_dict: dict[str, ...]) -> str:
        return self._stringify_proper(a_dict)

    def _set_generation_id(self, piece: ...):
        return self._set_generation_id_proper(piece)

    def _set_generation_id_for_v1(self, piece: StreamedChatResponse):
        if piece.event_type == 'stream-start':
            self.generation_id_in_stream_start = piece.generation_id or ""

    def _set_generation_id_for_v2(self, piece: StreamedChatResponseV2):
        if piece.type == 'message-start':
            self.generation_id_in_stream_start = piece.id or ""
    
    def _set_generation_id_for_openai(self, piece: openai_spec.ChatCompletionChunk | dict[str, ...]):
        if self.generation_id_in_stream_start is not None:
            return
        if hasattr(piece, 'model_dump'):
            piece_dict = piece.model_dump(exclude_unset=True, exclude_none=True)
        elif isinstance(piece, dict):
            piece_dict = piece
        else:
            piece_dict = {}
        if 'id' in piece_dict:
            self.generation_id_in_stream_start = piece_dict.get('id') or ""

    @staticmethod
    def _stringify_v1(a_dict: dict[str, ...]) -> str:
        return f"{json.dumps(a_dict)}\n"

    @staticmethod
    def _stringify_v2(a_dict: dict[str, ...]) -> str:
        return f'event: {a_dict.get("type")}\ndata: {json.dumps(a_dict)}\n\n'

    @staticmethod
    def _stringify_openai(a_dict: dict[str, ...]) -> str:
        return f'data: {json.dumps(a_dict)}\n\n'


class CohereLogger(Logger):
    instance: CohereLogger | None = None

    def __init__(self):
        super().__init__(__name__, level=logging.INFO)
        logging.basicConfig(
            stream=sys.stdout, 
            level=logging.INFO,
        )

    @classmethod
    def get_instance(cls) -> CohereLogger:
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance


# def parse_expression(expression: str) -> dict | list | str:
#     """Parse a JSON-like expression into a Python dictionary or list."""
#     try:
#         # Convert the expression to a JSON object
#         parsed_expression = json.loads(expression)
#         return parsed_expression
#     except json.JSONDecodeError as e1:
#         # If the expression is not in JSON format, return it as a string
#         try:
#             parsed_expression = ast.literal_eval(expression)
#             return parsed_expression
#         except (SyntaxError, ValueError) as e2:
#             # If the expression is not a valid Python literal, return it as a string
#             CohereLogger.get_instance().info(f"Failed to parse expression: {expression}")
#         return expression


def generate_v1_style_response_json_strings(
    chunked_message: Iterable[str],
    generation_id: str | None = None,
    send_stream_start: bool = True,
    finished_reason: Literal[
            "COMPLETE", "STOP_SEQUENCE", "ERROR", "ERROR_TOXIC", "ERROR_LIMIT", "USER_CANCEL", "MAX_TOKENS"
        ] = "COMPLETE",
    debug_do_ic: bool = False,
):
    if generation_id is None:
        generation_id = create_generation_id()
    if send_stream_start:
        stream_start = dict(
            event_type='stream-start',
            generation_id=generation_id,
            is_finished=False,
        )
        if debug_do_ic:
            from icecream import ic
            ic(stream_start)
        yield StreamingResponseHTTPExceptionDispatcherForCohere._stringify_v1(stream_start)

    emitted_chunks: list[str] = []
    for chunk in chunked_message:
        text_generation = dict(
            event_type='text-generation',
            text=chunk,
            is_finished=False,
        )
        emitted_chunks.append(chunk)
        if debug_do_ic:
            from icecream import ic
            ic(text_generation)
        yield StreamingResponseHTTPExceptionDispatcherForCohere._stringify_v1(text_generation)

    stream_end = dict(
        event_type="stream-end",
        finish_reason=finished_reason,
        generation_id=generation_id,
        response=dict(
            text="".join(emitted_chunks),
            finish_reason=finished_reason,
        ),
        is_finished=True,
    )
    if debug_do_ic:
        from icecream import ic
        ic(stream_end)
    yield StreamingResponseHTTPExceptionDispatcherForCohere._stringify_v1(stream_end)


def generate_v2_style_response_json_strings(
    chunked_message: Iterable[str],
    generation_id: str | None = None,
    send_stream_start: bool = True,
    finished_reason: Literal[
            "COMPLETE", "STOP_SEQUENCE", "MAX_TOKENS", "TOOL_CALL", "ERROR",
        ] = "COMPLETE",
    debug_do_ic: bool = False,
):
    if generation_id is None:
        generation_id = create_generation_id()
    if send_stream_start:
        message_start = dict(
            type='message-start',
            generation_id=generation_id,
            delta=dict(
                message=dict(
                    role='assistant',
                    content=[],
                    tool_plan='',
                    tool_calls=[],
                    citations=[],
                ),
            ),
        )
        content_start = dict(
            type='content-start',
            index=0,
            delta=dict(
                message=dict(
                    content=dict(
                        text='',
                        type='text',
                    ),
                ),
            ),
        )
        if debug_do_ic:
            from icecream import ic
            ic(message_start)
            ic(content_start)
        yield StreamingResponseHTTPExceptionDispatcherForCohere._stringify_v2(message_start)
        yield StreamingResponseHTTPExceptionDispatcherForCohere._stringify_v2(content_start)

    emitted_chunks: list[str] = []
    for chunk in chunked_message:
        content_delta = dict(
            type='content-delta',
            index=0,
            delta=dict(
                message=dict(
                    content=dict(
                        text=chunk,
                        type='text',
                    ),
                ),
            ),
        )
        emitted_chunks.append(chunk)
        if debug_do_ic:
            from icecream import ic
            ic(content_delta)
        yield StreamingResponseHTTPExceptionDispatcherForCohere._stringify_v2(content_delta)

    content_end = dict(
        type='content-end',
        index=0,
    )
    message_end = dict(
        type="message-end",
        delta=dict(
            finished_reason=finished_reason,
            usage=dict(
                billed_units=dict(
                    input_tokens=25,
                    output_tokens=114,
                ),
                tokens=dict(
                    input_tokens=1,
                    output_tokens=sum(map(lambda a_chunk: len(a_chunk.split()), emitted_chunks)),
                ),
            ),
        ),
    )
    if debug_do_ic:
        from icecream import ic
        ic(message_end)
    yield StreamingResponseHTTPExceptionDispatcherForCohere._stringify_v2(message_end)


# def generate_stream_response(
#     response: Iterator[StreamedChatResponse],
#     api_version: Literal["v1", "v2"],
# ):
#     CohereLogger.get_instance().info(f"type response of generator: {response}")

#     if api_version not in ["v1", "v2"]:
#         raise ValueError(f"Invalid API version: {api_version}. Expected 'v1' or 'v2'.")

#     # responseが未評価の場合、ここで例外が発生するのでこちらでも例外処理
#     try:
#         generation_id_in_stream_start: str | None = None
#         for piece in response:
#             CohereLogger.get_instance().info(f"Received piece: {piece}")
#             if api_version == 'v1':
#                 if piece.event_type == 'stream-start':
#                     generation_id_in_stream_start = piece.generation_id or ""
#             else:
#                 if piece.type == 'message-start':
#                     generation_id_in_stream_start = piece.id or ""
#             yield f"{piece.model_dump_json()}\n"
#     except ApiError as e:
#         if isinstance(e.body, str):
#             parsed_message = parse_expression(str(e.body))
#         else:
#             parsed_message = e.body
#         if isinstance (parsed_message, dict):
#             response = parsed_message
#         else:
#             response = {"message": parsed_message}
#         if "statusCode" not in response:
#             response["statusCode"] = e.status_code

#         generate_response_json_strings = (
#             generate_v1_style_response_json_strings if api_version == "v1" else
#             generate_v2_style_response_json_strings
#         )

#         yield from generate_response_json_strings(
#             chunked_message=[str(response.get('message')) or 'An error occurred.'],
#             generation_id=generation_id_in_stream_start,
#             send_stream_start=generation_id_in_stream_start is not None,
#             finished_reason="ERROR",
#         )


# OMITType: TypeAlias = type(OMIT)


# def omit_if_none(value: T | None) -> T | OMITType:
#     """Return the value if it is not None, otherwise return OMIT."""
#     return OMIT if value is None else value


def omit_none_values(param: BaseModel, keys_to_exclude: Collection[str] | None = None) -> dict[str, ...]:
    """Return a new dictionary with None values omitted."""
    keys_to_exclude = set() if keys_to_exclude is None else keys_to_exclude
    return {
        key: value for key, value in param.model_dump().items()
        if value is not None and value is not OMIT and key not in keys_to_exclude
    }


# Cohere V1 Chat API Spec
# https://docs.cohere.com/v1/reference/chat
def cohere_chat_v1_stream(
    request: CohereChatV1StreamRequest,
    api_key: str | None = None,
    x_client_name: str | None = None,
    accepts: str = "text/event-stream",
) -> Iterator[StreamedChatResponse]:

    client = cohere.Client(api_key=api_key, base_url=Environment.get_instance().cohere_url)

    # StreamedChatResponseのイテレータを生成
    response_iterator: Iterator[StreamedChatResponse] = client.chat_stream(
        model=request.model or "command-a-plus",
        message=request.message,
        chat_history=request.chat_history or OMIT,
        accepts=accepts,
        preamble=request.preamble or OMIT,
        conversation_id=request.conversation_id or OMIT,
        prompt_truncation=request.prompt_truncation or OMIT,
        connectors=request.connectors or OMIT,
        search_queries_only=request.search_queries_only or OMIT,
        documents=request.documents or OMIT,
        citation_quality=request.citation_quality or OMIT,
        temperature=request.temperature or OMIT,
        max_tokens=request.max_tokens or OMIT,
        max_input_tokens=request.max_input_tokens or OMIT,
        k=request.k or OMIT,
        p=request.p or OMIT,
        seed=request.seed or OMIT,
        stop_sequences=request.stop_sequences or OMIT,
        frequency_penalty=request.frequency_penalty or OMIT,
        presence_penalty=request.presence_penalty or OMIT,
        tools=request.tools or OMIT,
        tool_results=request.tool_results or OMIT,
        force_single_step=request.force_single_step or OMIT,
        # 下記のオプションはNone Typeで落ちるので一時的にコメントアウト
        # -> デフォルト引数のOMITでも落ちるので、このオプションが利用されるときは修正
        # File "/home/stratus/git-under/fre_pj_2025/for_dev/guardrails/venv/lib/python3.11/site-packages/cohere/client.py", line 95, in check_kwarg
        # return deprecated_kwarg in kwargs
        # response_format=cohereChatV1Request.response_format or OMIT,
        safety_mode=request.safety_mode or OMIT, 
    )
    
    
    return response_iterator
    

def cohere_chat_v1_non_stream(
    request: CohereChatV1NonStreamRequest,
    api_key: str | None = None,
    x_client_name: str | None = None,
    accepts: str = "application/json",
):
    client = cohere.Client(api_key=api_key, base_url=Environment.get_instance().cohere_url)
    if isinstance(request, CohereChatV1StreamRequest):
        request = CohereChatV1NonStreamRequest.model_validate(
            request.model_dump(exclude_unset=True, exclude_defaults=True),
            strict=False,
            extra='ignore',
        )

    additional_args = {}
    if 'response_format' in request.model_dump(exclude_unset=True):
        additional_args['response_format'] = request.response_format

    try:
        response: cohere.NonStreamedChatResponse = client.chat(
            message=request.message,
            accepts=accepts or request.accepts or None,
            model=request.model or OMIT,
            preamble=request.preamble or OMIT,
            chat_history=request.chat_history or OMIT,
            conversation_id=request.conversation_id or OMIT,
            prompt_truncation=request.prompt_truncation or OMIT,
            connectors=request.connectors or OMIT,
            search_queries_only=request.search_queries_only or OMIT,
            documents=request.documents or OMIT,
            citation_quality=request.citation_quality or OMIT,
            temperature=request.temperature or OMIT,
            max_tokens=request.max_tokens or OMIT,
            max_input_tokens=request.max_input_tokens or OMIT,
            k=request.k or OMIT,
            p=request.p or OMIT,
            seed=request.seed or OMIT,
            stop_sequences=request.stop_sequences or OMIT,
            frequency_penalty=request.frequency_penalty or OMIT,
            presence_penalty=request.presence_penalty or OMIT,
            raw_prompting=request.raw_prompting or OMIT,
            tools=request.tools or OMIT,
            tool_results=request.tool_results or OMIT,
            force_single_step=request.force_single_step or OMIT,
            # response_format=request.response_format or OMIT,
            **additional_args,
            safety_mode=request.safety_mode or OMIT,
            request_options=request.request_options or None,
        )
    except Exception as exp:
        print(str(exp))
        # import traceback; traceback.print_exc()
        raise
    return response


def cohere_chat_v2_stream(
    request: CohereChatV2Request,
    api_key: str | None = None,
    x_client_name: str | None = None,
    accepts: str = "text/event-stream",
) -> Iterator[V2ChatStreamResponse]:

    message: str | None = None
    if len(request.messages) > 0 and isinstance(request.messages[-1], dict):
        content = request.messages[-1].get('content')
        if isinstance(content, str):
            message = content
        elif isinstance(content, list):
            message = "\n".join(
                item.text for item in content
                if hasattr(item, 'text') and hasattr(item, 'type') and item.type == 'text'
            )

    client = cohere.ClientV2(api_key=api_key, base_url=Environment.get_instance().cohere_url)

    # StreamedChatResponseのイテレータを生成
    response_iterator: Iterator[StreamedChatResponse] = client.chat_stream(
        **omit_none_values(request, keys_to_exclude=('stream',))
    )
    return response_iterator


def cohere_chat_v2_non_stream(
    request: CohereChatV2Request,
    api_key: str | None = None,
    x_client_name: str | None = None,
    accepts: str = "application/json",
) -> cohere.NonStreamedChatResponseV2:

    client = cohere.ClientV2(api_key=api_key, base_url=Environment.get_instance().cohere_url)

    response: cohere.NonStreamedChatResponseV2 = client.chat(
        **omit_none_values(request, keys_to_exclude=('stream',))
    )
    return response
