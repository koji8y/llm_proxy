from typing import Iterable, Union
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse
from server.payloads import (
    CohereChatV1NonStreamRequest,
    CohereChatV1StreamRequest,
    CohereChatV1Response,
    CohereChatV2Request,
    CohereChatV2Response,
)
from server.error_utils import unified_exception_handler
from server.cohere_service import (
    cohere_chat_v1_stream,
    cohere_chat_v1_non_stream,
    cohere_chat_v2_stream,
    generate_v1_style_response_json_strings,
    generate_v2_style_response_json_strings,
    StreamingResponseHTTPExceptionDispatcher,
    create_generation_id,
    cohere,
)
from resources.environment import Environment
from icecream import ic

app = FastAPI()
app.add_exception_handler(Exception, unified_exception_handler)


def record(chunks: Iterable[any], path):
    with open(path, 'w') as out_file:
        for chunk in chunks:
            print(f'[{type(chunk)}]: {chunk}', file=out_file)
            yield chunk


@app.post("/v1/chat", response_model=Union[cohere.NonStreamedChatResponse, cohere.StreamedChatResponse])
async def cohere_v1_chat(
    request: Union[CohereChatV1NonStreamRequest, CohereChatV1StreamRequest],
    authorization: str | None = Header(None),
    ocp_apim_subscription_key: str | None = Header(None),
    accepts: str = Header("text/event-stream"),
    x_client_name: str | None = Header(None),
# ) -> StreamingResponse | CohereChatV1Response:
) -> cohere.NonStreamedChatResponse | cohere.StreamedChatResponse:
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
            dispatcher = StreamingResponseHTTPExceptionDispatcher(cohere_chat_v1_stream(
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

@app.post("/v2/chat", response_model=CohereChatV2Response)
async def cohere_v2_chat(
    request: CohereChatV2Request,
    authorization: str | None = Header(None),
    ocp_apim_subscription_key: str | None = Header(None),
    accepts: str = Header("text/event-stream"),
    x_client_name: str | None = Header(None),
) -> StreamingResponse | CohereChatV2Response:
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
            dispatcher = StreamingResponseHTTPExceptionDispatcher(cohere_chat_v2_stream(
                request=request,
                api_key=api_key,
                x_client_name=x_client_name,
                accepts=accepts,
            ), api_version="v2")
            return dispatcher.get_StreamingResponse_or_raise_HTTPException()
        except Exception as guardrails_block_exp:
            if 'block' not in exp.__class__.__name__.lower():
                raise
            generation_id = create_generation_id()

            if Environment.get_instance().raise_4xx_when_blocked:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": guardrails_block_exp.body.get('message', 'An error occurred.'),
                    }
                )
            else:
                return StreamingResponse(
                    generate_v2_style_response_json_strings(
                        chunked_message=[str(guardrails_block_exp.body.get('message', 'An error occurred.'))],
                        generation_id=generation_id,
                        finished_reason="ERROR",
                        debug_do_ic=True,
                    ),
                    media_type="text/event-stream",
                )
    else:
        raise HTTPException(
            status_code=400,
            detail="Streaming is required for this endpoint. Please set 'stream' to true in the request."
        )

@app.get("/ping")
def pong() -> str:
    return "pong2"
