from typing import Iterable, Union
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse
from datetime import datetime
from server.payloads import (
    CohereChatV1NonStreamRequest,
    CohereChatV1StreamRequest,
    # CohereChatV1Response,
    CohereChatV2Request,
    CohereChatV2Response,
)
from server.error_utils import unified_exception_handler
from server.cohere_service import (
    cohere_chat_v1_stream,
    cohere_chat_v1_non_stream,
    cohere_chat_v2_stream,
    cohere_chat_v2_non_stream,
    generate_v1_style_response_json_strings,
    generate_v2_style_response_json_strings,
    StreamingResponseHTTPExceptionDispatcherForCohere,
    create_generation_id,
    cohere,
)
from resources.environment import Environment
from server.openai_service import (
    openai_spec,
    OpenAIChatNonStreamingRequest,
    OpenAIChatStreamingRequest,
    openai_chat_stream,
    openai_chat_non_stream,
    generate_openai_style_response_json_strings,
    StreamingResponseHTTPExceptionDispatcherForOpenAI,
)
import server.compatible_types as compat_spec
from server import payloads_openai
from server.func_utils import show_result

app = FastAPI()
app.add_exception_handler(Exception, unified_exception_handler)


def record(chunks: Iterable[any], path):
    with open(path, 'w') as out_file:
        for chunk in chunks:
            print(f'[{type(chunk)}]: {chunk}', file=out_file)
            yield chunk


@app.post(
    "/compatibility/v1/chat/completions",
    # response_model=Union[
    #     compat_spec.OpenAIStream[openai_spec.ChatCompletionChunk],
    #     openai_spec.ChatCompletion,
    #     payloads_openai.ChatCompletion,
    #     dict,
    # ]
    response_model=dict,
)
@show_result
async def compatibility_v1_chat_completions(
    request: Union[OpenAIChatNonStreamingRequest, OpenAIChatStreamingRequest],
    authorization: str | None = Header(None),
    accepts: str = Header("text/event-stream"),
    x_client_name: str | None = Header(None),
) -> openai_spec.Stream[openai_spec.ChatCompletionChunk] | openai_spec.ChatCompletion:
    base_url = Environment._ensure_trailing_slash(
        Environment.get_instance().cohere_url or "https://api.cohere.com/"
    )
    
    result = await openai_chat_completions(
        request=request,
        authorization=authorization,
        accepts=accepts,
        x_client_name=x_client_name,
        base_url=f'{base_url}compatibility/v1',
    )
    if request.stream:
        return result
    else:
        return result.model_dump(exclude_computed_fields=True, exclude_none=True, exclude_defaults=True, exclude_unset=True)


@app.post(
    "/v1/chat/completions",
    # response_model=Union[
    #     compat_spec.OpenAIStream[openai_spec.ChatCompletionChunk],
    #     openai_spec.ChatCompletion,
    # ]
    # response_model=Union[
    #     compat_spec.OpenAIStream[openai_spec.ChatCompletionChunk],
    #     dict,
    # ]
    # response_model=None,
    response_model=dict
    # response_model=Union[
    #     compat_spec.OpenAIStream[openai_spec.ChatCompletionChunk],
    #     payloads_openai.ChatCompletion,
    #     dict,
    # ]
)
@show_result
async def v1_chat_completions(
    request: Union[OpenAIChatNonStreamingRequest, OpenAIChatStreamingRequest],
    authorization: str | None = Header(None),
    accepts: str = Header("text/event-stream"),
    x_client_name: str | None = Header(None),
    base_url: str | None = None,
# ) -> openai_spec.Stream[openai_spec.ChatCompletionChunk] | payloads_openai.ChatCompletion:
) -> openai_spec.Stream[openai_spec.ChatCompletionChunk] | openai_spec.ChatCompletion:
# ) -> openai_spec.ChatCompletion:
# ) -> dict:
# ):
    result = await openai_chat_completions(
        request=request,
        authorization=authorization,
        accepts=accepts,
        x_client_name=x_client_name,
        base_url=Environment.get_instance().openai_url,
    )
    # from icecream import ic; ic(30, result)
    # from icecream import ic; ic('v1_chat_completions', type(result))
    if request.stream:
        return result
    else:
        return result.model_dump(exclude_computed_fields=True, exclude_none=True, exclude_defaults=True, exclude_unset=True)


@show_result
async def openai_chat_completions(
    base_url: str | None,
    request: Union[OpenAIChatNonStreamingRequest, OpenAIChatStreamingRequest],
    authorization: str | None = Header(None),
    accepts: str = Header("text/event-stream"),
    x_client_name: str | None = Header(None),
# ) -> openai_spec.Stream[openai_spec.ChatCompletionChunk] | payloads_openai.ChatCompletion:
) -> openai_spec.Stream[openai_spec.ChatCompletionChunk] | openai_spec.ChatCompletion:
# ) -> openai_spec.ChatCompletion:
# ):
    # from icecream import ic; ic(base_url)
    # from icecream import ic; ic(request.model_dump(exclude_none=True, exclude_unset=True, exclude_defaults=True, exclude_computed_fields=True))
    # # if isinstance(request, dict):
    # #     if request.get('stream', False):
    # #         request = OpenAIChatStreamingRequest.model_validate(request)
    # #     else:
    # #         request = OpenAIChatNonStreamingRequest.model_validate(request)
    if authorization is not None and authorization.lower().startswith("bearer "):
        api_key = authorization[len("bearer "):].strip()
    elif Environment.get_instance().precheck_api_key:
        raise HTTPException(
            status_code=401,
            detail=(
                "Access denied due to invalid subscription key. Make sure to provide a valid key for an active subscription. "
                "Either 'Authorization' header with bearer token is required."
            )
        )
    else:
        api_key = 'invalid_key'

    if request.stream:
        try:
            dispatcher = StreamingResponseHTTPExceptionDispatcherForOpenAI(openai_chat_stream(
                request=request,
                api_key=api_key,
                x_client_name=x_client_name,
                accepts=accepts,
                base_url=base_url,
            ))
            return dispatcher.get_StreamingResponse_or_raise_HTTPException()
        except Exception as exp:  # TODO: should shrink the range from general Exception
            if 'block' not in exp.__class__.__name__.lower():
                raise
            generation_id = create_generation_id()

            if Environment.get_instance().raise_4xx_when_blocked:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": exp.body.get('message', 'An error occurred.'),
                    }
                )
            else:
                return StreamingResponse(
                    generate_openai_style_response_json_strings(
                        chunked_message=[str(exp.body.get('message', 'An error occurred.'))],
                        generation_id=generation_id,
                        finished_reason="ERROR",
                        debug_do_ic=True,
                    ),
                    media_type="text/event-stream",
                )
    else:
        # raise HTTPException(
        #     status_code=400,
        #     detail="Streaming is required for this endpoint. Please set 'stream' to true in the request."
        # )
        try:
            response = openai_chat_non_stream(
                request=request,
                api_key=api_key,
                x_client_name=x_client_name,
                accepts=accepts,
                base_url=base_url,
            )
            # from icecream import ic; ic(response)
            # ic('-', response.model_dump(exclude_none=True, exclude_unset=True, exclude_defaults=True, exclude_computed_fields=True))
            # response = openai_spec.ChatCompletion.model_validate(
            #     ic({
            #         ic(k): ic(vm)
            #         for k, v in response.model_dump(exclude_none=True, exclude_unset=True, exclude_defaults=True, exclude_computed_fields=True).items()
            #         if k in ['choices', 'id', 'object', 'created', 'model']
            #         for vm in [v if k == 'created' else v]
            #     })
            # )
            # ic('a', response)
            # response = response.model_dump(exclude_computed_fields=True, exclude_none=True, exclude_defaults=True, exclude_unset=True)
            # response = openai_spec.ChatCompletion.model_validate(response)
        except Exception:
            import traceback; traceback.print_exc()
            raise
        # response = payloads_openai.ChatCompletion.model_validate(
        #     response.model_dump(exclude_computed_fields=True, exclude_none=True, exclude_defaults=True, exclude_unset=True)
        # )
        return response


@app.post("/v1/chat", response_model=Union[cohere.NonStreamedChatResponse, cohere.StreamedChatResponse])
async def cohere_v1_chat(
    request: Union[CohereChatV1NonStreamRequest, CohereChatV1StreamRequest],
    authorization: str | None = Header(None),
    ocp_apim_subscription_key: str | None = Header(None),
    accepts: str = Header("text/event-stream"),
    x_client_name: str | None = Header(None),
# ) -> StreamingResponse | CohereChatV1Response:
) -> cohere.NonStreamedChatResponse | cohere.StreamedChatResponse:
    # from icecream import ic; ic(request)
    if Environment.get_instance().dev_show_incoming_message:
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} [Cohere V1 Chat] Incoming message: {request.message}')
    # _ready.wait()
    if Environment.get_instance().dev_avoid_accurate_citation_quality and (
        (request.citation_quality is None or request.citation_quality in ["accurate"])
    ):
        request.citation_quality = "fast"
    if authorization is not None and authorization.lower().startswith("bearer "):
        api_key = authorization[len("bearer "):].strip()
    elif ocp_apim_subscription_key is not None:
        api_key = ocp_apim_subscription_key.strip()
    elif Environment.get_instance().precheck_api_key:
        raise HTTPException(
            status_code=401,
            detail=(
                "Access denied due to invalid subscription key. Make sure to provide a valid key for an active subscription. "
                "Either 'Authorization' header with bearer token is required."
            )
        )
    else:
        api_key = 'invalid_key'

    if request.stream:
        try:
            dispatcher = StreamingResponseHTTPExceptionDispatcherForCohere(cohere_chat_v1_stream(
                request=request,
                api_key=api_key,
                x_client_name=x_client_name,
                accepts=accepts,
            ), api_version="v1")
            return dispatcher.get_StreamingResponse_or_raise_HTTPException()
        except Exception as exp:  # TODO: should shrink the range from general Exception
            if 'block' not in exp.__class__.__name__.lower():
                raise
            generation_id = create_generation_id()

            if Environment.get_instance().raise_4xx_when_blocked:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": exp.body.get('message', 'An error occurred.'),
                    }
                )
            else:
                return StreamingResponse(
                    generate_v1_style_response_json_strings(
                        chunked_message=[str(exp.body.get('message', 'An error occurred.'))],
                        generation_id=generation_id,
                        finished_reason="ERROR",
                        debug_do_ic=True,
                    ),
                    media_type="text/event-stream",
                )
    else:
        # raise HTTPException(
        #     status_code=400,
        #     detail="Streaming is required for this endpoint. Please set 'stream' to true in the request."
        # )
        try:
            response = cohere_chat_v1_non_stream(
                request=request,
                api_key=api_key,
                x_client_name=x_client_name,
                accepts=accepts,
            )
        except Exception:
            import traceback; traceback.print_exc()
            raise
        return response


@app.post("/v2/chat", response_model=Union[CohereChatV2Response, cohere.V2ChatResponse])
async def cohere_v2_chat(
    request: CohereChatV2Request,
    authorization: str | None = Header(None),
    ocp_apim_subscription_key: str | None = Header(None),
    accepts: str = Header("text/event-stream"),
    x_client_name: str | None = Header(None),
# ) -> StreamingResponse | CohereChatV2Response:
) -> cohere.V2ChatResponse | StreamingResponse | CohereChatV2Response:
    if Environment.get_instance().dev_show_incoming_message:
        LF = '\n'
        print(f'''{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} [Cohere V2 Chat] Incoming message:{LF}{LF.join(f"{message.get("role", "-")}: {message.get("content", "")}" for message in request.messages)}''')
    if authorization is not None and authorization.lower().startswith("bearer "):
        api_key = authorization[len("bearer "):].strip()
    elif ocp_apim_subscription_key is not None:
        api_key = ocp_apim_subscription_key.strip()
    elif Environment.get_instance().precheck_api_key:
        raise HTTPException(
            status_code=401,
            detail=(
                "Access denied due to invalid subscription key. Make sure to provide a valid key for an active subscription. "
                "Either 'Authorization' header with bearer token is required."
            )
        )
    else:
        api_key = 'invalid_key'

    if request.stream:
        try:
            dispatcher = StreamingResponseHTTPExceptionDispatcherForCohere(cohere_chat_v2_stream(
                request=request,
                api_key=api_key,
                x_client_name=x_client_name,
                accepts=accepts,
            ), api_version="v2")
            return dispatcher.get_StreamingResponse_or_raise_HTTPException()
        except Exception as exp:
            if 'block' not in exp.__class__.__name__.lower():
                raise
            generation_id = create_generation_id()

            if Environment.get_instance().raise_4xx_when_blocked:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": exp.body.get('message', 'An error occurred.'),
                    }
                )
            else:
                return StreamingResponse(
                    generate_v2_style_response_json_strings(
                        chunked_message=[str(exp.body.get('message', 'An error occurred.'))],
                        generation_id=generation_id,
                        finished_reason="ERROR",
                        debug_do_ic=True,
                    ),
                    media_type="text/event-stream",
                )
    else:
        # raise HTTPException(
        #     status_code=400,
        #     detail="Streaming is required for this endpoint. Please set 'stream' to true in the request."
        # )
        try:
            response = cohere_chat_v2_non_stream(
                request=request,
                api_key=api_key,
                x_client_name=x_client_name,
                accepts=accepts,
            )
            return response
        except Exception:
            import traceback; traceback.print_exc()
            raise

@app.get("/ping")
def pong() -> str:
    return "pong2"
