from __future__ import annotations
from abc import abstractmethod
from typing import Iterable, Iterator, TypeVar, Callable, Literal
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi import HTTPException
import logging
import sys
import json


T = TypeVar('T')
T2 = TypeVar('T2')
T3 = TypeVar('T3')
E = TypeVar('E', bound=Exception)

class CommonServiceLogger(logging.Logger):
    instance: CommonServiceLogger | None = None

    def __init__(self):
        super().__init__(__name__, level=logging.INFO)
        logging.basicConfig(
            stream=sys.stdout, 
            level=logging.INFO,
        )

    @classmethod
    def get_instance(cls) -> CommonServiceLogger:
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance


def get_wrapper_after_getting_first_item_successfully(
    responses: Iterable[T],
    exception_type_to_catch: type[E],
    wrapper_in_case_of_success: Callable[[Iterable[T]], T2],
    wrapper_in_case_of_exception: Callable[[E], T3] | None = None,
) -> T2:
    one_time_sequence = (item for item in responses)
    try:
        try:
            first_item: T = next(one_time_sequence)
            have_got_first = True
        except StopIteration:
            have_got_first = False
        def emit():
            if not have_got_first:
                return
            yield first_item
            yield from one_time_sequence

        return wrapper_in_case_of_success(emit())
    except exception_type_to_catch as e:
        raise wrapper_in_case_of_exception(e)


class StreamingResponseHTTPExceptionDispatcher:
    def __init__(
        self,
        response: Iterator[BaseModel | dict[str, ...]],
        exception_type_to_catch: type[E],
        additional_strings: list[str] | None = None,
        log_to_info: bool = False,
    ):
        self.response = response
        self.generation_id_in_stream_start: str | None = None
        self.exception_type_to_catch = exception_type_to_catch
        self.log_to_info = log_to_info
        self.additional_string = additional_strings or []

    @abstractmethod
    def _set_generation_id(self, piece: ...):
        ...

    @abstractmethod
    def _stringify(self, a_dict: dict[str, ...]) -> str:
        ...

    @abstractmethod
    def _detect_finishing(self, piece: ...) -> bool:
        ...

    @abstractmethod
    def _create_intermediate_response(self, piece: str):
        ...

    def _feed_response(self):
        added = False
        for piece in self.response:
            if not added:
                piece_dict = (
                    piece.model_dump(exclude_unset=True, exclude_none=True) if hasattr(piece, 'model_dump') else
                    piece if isinstance(piece, dict) else
                    {}
                )
                if self._detect_finishing(piece_dict):
                    from icecream import ic; ic(self.additional_string)
                    for text in self.additional_string:
                        intermediate_response = self._create_intermediate_response(text)
                        yield intermediate_response
                    added = True
            yield piece

    def _yield_items(self):
        for piece in self._feed_response():
            if self.log_to_info:
                CommonServiceLogger.get_instance().info(f"Received piece: {piece}")
            self._set_generation_id(piece)
            from icecream import ic
            ic(type(piece))
            ic(piece.model_dump(exclude_unset=True, exclude_none=True))
            yield self._stringify(piece.model_dump(exclude_unset=True, exclude_none=True))

    def get_StreamingResponse_or_raise_HTTPException(self):
        return get_wrapper_after_getting_first_item_successfully(
            responses=self._yield_items(),
            exception_type_to_catch=self.exception_type_to_catch,
            wrapper_in_case_of_success=lambda items: StreamingResponse(
                map(lambda item: item, items),
                media_type="text/event-stream",
            ),
            wrapper_in_case_of_exception=lambda e: HTTPException(
                status_code=e.status_code,
                detail=e.body.get('message', 'An error occurred.') if isinstance(e.body, dict) else str(e.body),
            ),
        )
