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
from server.payloads_openai import openai_spec, OpenAIChatNonStreamingRequest, OpenAIChatStreamingRequest
from server.common_service import StreamingResponseHTTPExceptionDispatcher
from server.generic_service import create_generation_id
from openai import APIError
import server.payloads_openai as payloads

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
        log_to_info: bool = False,
    ):
        super().__init__(
            response=response,
            exception_type_to_catch=APIError,
            log_to_info=log_to_info,
        )

    def _set_generation_id(self, piece: openai_spec.ChatCompletionChunk | dict[str, ...]):
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

    def _stringify(self, a_dict: dict[str, ...]) -> str:
        return self._stringify_proper(a_dict)

    @staticmethod
    def _stringify_proper(a_dict: dict[str, ...]) -> str:
        return f'data: {json.dumps(a_dict)}\n\n'


def openai_chat_stream(
    request: OpenAIChatNonStreamingRequest,
    api_key: str | None = None,
    x_client_name: str | None = None,
    accepts: str = "text/event-stream",
    base_url: str | None = None,
    organization: str | None = None,
    project: str | None = None,
    # ) -> openai_spec.ChatCompletion:
) -> openai_spec.Stream[openai_spec.ChatCompletionChunk]:

    client = OpenAI(api_key=api_key, base_url=base_url, organization=organization, project=project)

    opts = request.model_dump(exclude_defaults=True, exclude_none=True, exclude_unset=True)
    reqponse_iterator: openai_spec.Stream[openai_spec.ChatCompletionChunk] = \
        client.chat.completions.create(
            **opts,
        )

    return reqponse_iterator


@show_result
def openai_chat_non_stream(
    request: OpenAIChatNonStreamingRequest,
    api_key: str | None = None,
    x_client_name: str | None = None,
    accepts: str = "application/json",
    base_url: str | None = None,
    organization: str | None = None,
    project: str | None = None,
) -> openai_spec.ChatCompletion:
# ) -> payloads.ChatCompletion:

    client = OpenAI(api_key=api_key, base_url=base_url, organization=organization, project=project)

    opts = request.model_dump(exclude_defaults=True, exclude_none=True, exclude_unset=True)
    response = \
        client.chat.completions.create(
            **opts,
        )
    # from icecream import ic; ic('openai_chat_non_stream', type(response))
    return response


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
        # json[0].choices = [];
        # json[0].choices[0] = {};
        # json[0].choices[0].delta = {};
        # json[0].choices[0].delta.content = "";
        # json[0].choices[0].delta.refusal = null;
        # json[0].choices[0].delta.role = "assistant";
        # json[0].choices[0].finish_reason = null;
        # json[0].choices[0].index = 0;
        # json[0].created = 1769573307;
        # json[0].id = "chatcmpl-D2r8txbp7PuQoI756vdZd1dZ1jsvn";
        # json[0].model = "gpt-5-2025-08-07";
        # json[0].obfuscation = "E2Dsqz6";
        # json[0].object = "chat.completion.chunk";
        # json[0].service_tier = "default";
        # json[0].system_fingerprint = null;
        yield StreamingResponseHTTPExceptionDispatcherForOpenAI._stringify(dict(
            choices=[dict(delta=dict(content="", refusal=None, role="assistant"), finish_reason=None, index=0)],
            id=generation_id,
            object="chat.completion.chunk",
        ))

    # json[1] = {};
    # json[1].choices = [];
    # json[1].choices[0] = {};
    # json[1].choices[0].delta = {};
    # json[1].choices[0].delta.content = "As";
    # json[1].choices[0].finish_reason = null;
    # json[1].choices[0].index = 0;
    # json[1].created = 1769573307;
    # json[1].id = "chatcmpl-D2r8txbp7PuQoI756vdZd1dZ1jsvn";
    # json[1].model = "gpt-5-2025-08-07";
    # json[1].obfuscation = "rsEqbqo";
    # json[1].object = "chat.completion.chunk";
    # json[1].service_tier = "default";
    # json[1].system_fingerprint = null;
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

    # json[43] = {};
    # json[43].choices = [];
    # json[43].choices[0] = {};
    # json[43].choices[0].delta = {};
    # json[43].choices[0].finish_reason = "stop";
    # json[43].choices[0].index = 0;
    # json[43].created = 1769573307;
    # json[43].id = "chatcmpl-D2r8txbp7PuQoI756vdZd1dZ1jsvn";
    # json[43].model = "gpt-5-2025-08-07";
    # json[43].obfuscation = "LkM";
    # json[43].object = "chat.completion.chunk";
    # json[43].service_tier = "default";
    # json[43].system_fingerprint = null;
    yield StreamingResponseHTTPExceptionDispatcherForOpenAI._stringify(dict(
        choices=[dict(delta=dict(), finish_reason=finished_reason, index=0)],
        id=generation_id,
        object="chat.completion.chunk",
    ))
