from __future__ import annotations
from typing import Iterable, Literal
import logging
from logging import Logger
import sys
# %%
from openai import OpenAI
from dotenv import load_dotenv
from server.payloads_openai import openai_spec, OpenAIChatNonStreamingRequest, OpenAIChatStreamingRequest
from server.generic_service import create_generation_id

load_dotenv()


def try_openai_api():
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-5.2",
        messages=[
            {'role': 'user', 'content': "How to make a pancake?"}
        ]
    )

    print(completion.choices[0].message)
    return completion.choices[0]

def try_openai_api_stream():
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-5.2",
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

def openai_chat_stream(
    request: OpenAIChatNonStreamingRequest,
    api_key: str | None = None,
    x_client_name: str | None = None,
    acceepts: str = "text/event-stream",
    base_url: str | None = None,
    organization: str | None = None,
    project: str | None = None,
    # ) -> openai_spec.ChatCompletion:
) -> openai_spec.Stream[openai_spec.ChatCompletionChunk]:

    client = OpenAI(api_key=api_key, base_url=base_url, organization=organization, project=project)

    opts = request.model_dump(exclude_defaults=True, exclude_none=True, exclude_unset=True)
    reqponse_iterator: openai_spec.Stream[openai_spec.ChatCompletionChunk] = client.chat.completions.create(
        **opts,
    )

    return reqponse_iterator


def generate_openai_style_response_json_strings(
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
        yield StreamingResponseHTTPExceptionDispatcher._stringify_v2(message_start)
        yield StreamingResponseHTTPExceptionDispatcher._stringify_v2(content_start)

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
        yield StreamingResponseHTTPExceptionDispatcher._stringify_v2(content_delta)

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
    yield StreamingResponseHTTPExceptionDispatcher._stringify_v2(message_end)
