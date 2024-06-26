"""
This type stub file was generated by pyright.
"""

import os
import re
import shutil
import subprocess
import tempfile
from __future__ import annotations
from pathlib import Path
from typing import Any, Callable, TYPE_CHECKING, TypeVar
from pdm.exceptions import PdmException
from pdm.utils import normalize_name
from importlib.resources.abc import Traversable

if TYPE_CHECKING:
    ST = TypeVar("ST", Traversable, Path)
TEMPLATE_PACKAGE = ...
BUILTIN_TEMPLATES = ...
class ProjectTemplate:
    _path: Path
    def __init__(self, path_or_url: str | None) -> None:
        ...

    def __enter__(self) -> ProjectTemplate:
        ...

    def __exit__(self, *args: Any) -> None:
        ...

    def generate(self, target_path: Path, metadata: dict[str, Any], overwrite: bool = ...) -> None:
        ...

    def prepare_template(self) -> None:
        ...

    @staticmethod
    def mirror(src: ST, dst: Path, skip: list[ST] | None = ..., copyfunc: Callable[[ST, Path], Any] = ..., *, overwrite: bool = ...) -> None:
        ...
