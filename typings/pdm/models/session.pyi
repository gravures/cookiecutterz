"""
This type stub file was generated by pyright.
"""

import hishel
import httpx
from pathlib import Path
from typing import Any, TYPE_CHECKING
from hishel._serializers import Metadata
from httpcore import Request, Response
from unearth.fetchers import PyPIClient
from pdm._types import RepositoryConfig

if TYPE_CHECKING:
    ...
_ssl_context = ...
CACHES_TTL = ...
class MsgPackSerializer(hishel.BaseSerializer):
    KNOWN_REQUEST_EXTENSIONS = ...
    KNOWN_RESPONSE_EXTENSIONS = ...
    DATETIME_FORMAT = ...
    def dumps(self, response: Response, request: Request, metadata: Metadata) -> bytes:
        ...

    def loads(self, data: bytes) -> tuple[Response, Request, Metadata]:
        ...

    @property
    def is_binary(self) -> bool:
        ...



class PDMPyPIClient(PyPIClient):
    def __init__(self, *, sources: list[RepositoryConfig], cache_dir: Path, **kwargs: Any) -> None:
        ...

    def on_response(self, response: httpx.Response) -> None:
        ...
