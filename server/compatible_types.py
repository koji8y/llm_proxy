from __future__ import annotations
from typing import Iterable, TypeAlias, Mapping, Union, Optional
from pydantic import BaseModel, Field, ConfigDict
from httpx._config import TimeoutTypes


# Original: httpx._types.TimeoutTypes
TimeoutTypes: TypeAlias = Union[
    Optional[float],
    tuple[Optional[float], Optional[float], Optional[float], Optional[float]],
    "Httpx_Timeout",
]

# Original: httpxs._config.Timeout
class Httpx_Timeout(BaseModel):
    timeout: TimeoutTypes | None = None
    connect: float | None = None
    read: float | None = None
    write: float | None = None
    pool: float | None = None


# Original: openai._streaming.Stream
OpenAIStream: TypeAlias = Iterable


# Original: openai._types.Headers
OpenAIHeaders = Mapping[str, Union[str, None]]
