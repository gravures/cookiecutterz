"""
This type stub file was generated by pyright.
"""

from __future__ import annotations
from typing import Iterable, Mapping, Protocol, TYPE_CHECKING, Union, cast
from pdm.formats import flit, pipfile, poetry, requirements, setup_py
from pdm.formats.base import MetaConvertError as MetaConvertError
from argparse import Namespace
from pathlib import Path
from pdm.models.candidates import Candidate
from pdm.models.requirements import Requirement
from pdm.project import Project

if TYPE_CHECKING:
    ExportItems = Union[Iterable[Candidate], Iterable[Requirement]]
    class _Format(Protocol):
        def check_fingerprint(self, project: Project | None, filename: str | Path) -> bool:
            ...

        def convert(self, project: Project | None, filename: str | Path, options: Namespace | None) -> tuple[Mapping, Mapping]:
            ...

        def export(self, project: Project, candidates: ExportItems, options: Namespace | None) -> str:
            ...



FORMATS: Mapping[str, _Format] = ...