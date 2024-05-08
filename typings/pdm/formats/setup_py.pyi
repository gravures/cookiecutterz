"""
This type stub file was generated by pyright.
"""

from pathlib import Path
from typing import Any, Mapping, TYPE_CHECKING
from pdm.project import Project

if TYPE_CHECKING:
    ...
def check_fingerprint(project: Project, filename: Path) -> bool:
    ...

def convert(project: Project, filename: Path, options: Any | None) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    ...

def export(project: Project, candidates: list, options: Any | None) -> str:
    ...
