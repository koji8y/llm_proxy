from __future__ import annotations
from typing import Iterable, Literal, Iterator, TypeVar
from pydantic import BaseModel
import logging
from logging import Logger
import sys
import json
# %%
from openai import OpenAI
from dotenv import load_dotenv
from server.func_utils import show_result
from server.payloads_openai import (
    openai_spec,
    openai_spec_types,
    openai_spec_chunk_types,
    OpenAIChatNonStreamingRequest,
    OpenAIChatStreamingRequest
)
from server.common_service import StreamingResponseHTTPExceptionDispatcher
from server.generic_service import create_generation_id
from openai import APIError
import server.payloads_openai as payloads
from resources.environment import Environment
from server.debug_utils import get_test_info_for_debug

load_dotenv()


def try_openai_api():
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {'role': 'user', 'content': "How to make a pancake?"}
        ]
    )

    print(completion.choices[0].message)
    return completion.choices[0]

def try_openai_api_stream():
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {'role': 'user', 'content': "How to make a pancake?"}
        ],
        stream=True
    )

    for chunk in completion:
        print(
            chunk.choices[0].delta, flush=True,
            # end='', 
        )
    return completion
# %%
if __name__ == "__main__":
    choice = try_openai_api()
# %%
if __name__ == "__main__":
    response = try_openai_api_stream()

# %%
class OpenAILogger(Logger):
    instance: OpenAILogger | None = None

    def __init__(self):
        super().__init__(__name__, level=logging.INFO)
        logging.basicConfig(
            stream=sys.stdout, 
            level=logging.INFO,
        )

    @classmethod
    def get_instance(cls) -> OpenAILogger:
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance
# %%

E = TypeVar('E', bound=Exception)

class StreamingResponseHTTPExceptionDispatcherForOpenAI(StreamingResponseHTTPExceptionDispatcher):
    def __init__(
        self,
        response: Iterator[BaseModel | dict[str, ...]],
        exception_type_to_catch: type[E] = APIError,
        additional_strings: list[str] | None = None,
        log_to_info: bool = False,
    ):
        super().__init__(
            response=response,
            exception_type_to_catch=exception_type_to_catch,
            log_to_info=log_to_info,
            additional_strings=additional_strings,
        )

    def _set_generation_id(self, piece: ...):
        if hasattr(piece, 'model_dump'):
            piece_dict = piece.model_dump(exclude_unset=True, exclude_none=True)
        elif isinstance(piece, dict):
            piece_dict = piece
        else:
            piece_dict = {}
        if 'id' in piece_dict:
            self.generation_id_in_stream_start = piece_dict.get('id') or ""

    @staticmethod
    def _stringify(a_dict: dict[str, ...]) -> str:
        return f'data: {json.dumps(a_dict)}\n\n'

    # @staticmethod
    # def _stringify_proper(a_dict: dict[str, ...]) -> str:
    #     return f'data: {json.dumps(a_dict)}\n\n'

    def _detect_finishing(self, piece: dict[str, ...]) -> bool:
        return piece.get('choices', {})[0].get('finish_reason')

    def _create_intermediate_response(self, text: str) :
        data = openai_spec.ChatCompletionChunk(
            id=self.generation_id_in_stream_start,
            object="chat.completion.chunk",
            choices=[
                openai_spec_chunk_types.Choice(
                    delta=openai_spec_chunk_types.ChoiceDelta(
                        content=text,
                    ),
                    index=0,
                    finish_reason=None,
                )
            ],
            created=0,
            model="",
        )
        return data

def openai_chat_stream(
    request: OpenAIChatStreamingRequest,
    api_key: str | None = None,
    x_client_name: str | None = None,
    accepts: str = "text/event-stream",
    base_url: str | None = None,
    organization: str | None = None,
    project: str | None = None,
    # ) -> openai_spec.ChatCompletion:
) -> tuple[openai_spec.Stream[openai_spec.ChatCompletionChunk], dict | None]:

    client = OpenAI(api_key=api_key, base_url=base_url, organization=organization, project=project)

    opts = request.model_dump(exclude_defaults=True, exclude_none=True, exclude_unset=True)
    reqponse_iterator: openai_spec.Stream[openai_spec.ChatCompletionChunk] = \
        client.chat.completions.create(
            **opts,
        )

    additional_info = (
        get_test_info_for_debug()
        if Environment.get_instance().debug_append_test_info else
        None
    )
    return reqponse_iterator, additional_info


@show_result
def openai_chat_non_stream(
    request: OpenAIChatNonStreamingRequest,
    api_key: str | None = None,
    x_client_name: str | None = None,
    accepts: str = "application/json",
    base_url: str | None = None,
    organization: str | None = None,
    project: str | None = None,
) -> tuple[openai_spec.ChatCompletion, dict | None]:

    client = OpenAI(api_key=api_key, base_url=base_url, organization=organization, project=project)

    opts = request.model_dump(exclude_defaults=True, exclude_none=True, exclude_unset=True)
    response = \
        client.chat.completions.create(
            **opts,
        )
    # from icecream import ic; ic('openai_chat_non_stream', type(response))
    additional_info = (
        get_test_info_for_debug()
        if Environment.get_instance().debug_append_test_info else
        None
    )
    return response, additional_info


def generate_openai_style_response_json_strings(
    chunked_message: Iterable[str],
    generation_id: str | None = None,
    send_stream_start: bool = True,
    finished_reason: Literal[
        "stop",
    ] = "stop",
    debug_do_ic: bool = False,
):
    if generation_id is None:
        generation_id = create_generation_id()
    if send_stream_start:
        yield StreamingResponseHTTPExceptionDispatcherForOpenAI._stringify(dict(
            choices=[dict(delta=dict(content="", refusal=None, role="assistant"), finish_reason=None, index=0)],
            id=generation_id,
            object="chat.completion.chunk",
        ))

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
        yield StreamingResponseHTTPExceptionDispatcherForOpenAI._stringify(dict(
            choices=[dict(delta=dict(content=chunk), finish_reason=None, index=0)],
            id=generation_id,
            object="chat.completion.chunk",
        ))

    yield StreamingResponseHTTPExceptionDispatcherForOpenAI._stringify(dict(
        choices=[dict(delta=dict(), finish_reason=finished_reason, index=0)],
        id=generation_id,
        object="chat.completion.chunk",
    ))
