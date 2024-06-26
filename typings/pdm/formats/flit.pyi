"""
This type stub file was generated by pyright.
"""

from pathlib import Path
from typing import Any, Mapping, TYPE_CHECKING
from pdm.formats.base import MetaConverter, convert_from
from argparse import Namespace
from os import PathLike
from pdm.project import Project

if TYPE_CHECKING:
    ...
def check_fingerprint(project: Project | None, filename: PathLike) -> bool:
    ...

def get_docstring_and_version_via_ast(target: Path) -> tuple[str | None, str | None]:
    """
    This function is borrowed from flit's implementation, but does not attempt to import
    that file. If docstring or version can't be retrieved by this function,
    they are just left empty.
    """
    ...

class FlitMetaConverter(MetaConverter):
    def warn_against_dynamic_version_or_docstring(self, source: Path, version: str, description: str) -> None:
        ...

    @convert_from("metadata")
    def name(self, metadata: dict[str, Any]) -> str:
        ...

    @convert_from("entrypoints", name="entry-points")
    def entry_points(self, value: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
        ...

    @convert_from("sdist")
    def includes(self, value: dict[str, list[str]]) -> None:
        ...



def convert(project: Project | None, filename: PathLike, options: Namespace | None) -> tuple[Mapping, Mapping]:
    ...

def export(project: Project, candidates: list, options: Namespace | None) -> None:
    ...
