"""
This type stub file was generated by pyright.
"""

from typing import Any, TYPE_CHECKING
from argparse import Namespace
from os import PathLike
from pdm._types import RequirementDict
from pdm.models.backends import BuildBackend
from pdm.project import Project

if TYPE_CHECKING:
    ...
MARKER_KEYS = ...
def convert_pipfile_requirement(name: str, req: RequirementDict, backend: BuildBackend) -> str:
    ...

def check_fingerprint(project: Project, filename: PathLike) -> bool:
    ...

def convert(project: Project, filename: PathLike, options: Namespace | None) -> tuple[dict[str, Any], dict[str, Any]]:
    ...

def export(project: Project, candidates: list, options: Any) -> None:
    ...
