"""
This type stub file was generated by pyright.
"""

import dataclasses
from pathlib import Path
from typing import Any, Sequence, TYPE_CHECKING, TypeVar
from packaging.requirements import Requirement as PackageRequirement
from packaging.specifiers import SpecifierSet
from pdm.compat import Distribution
from pdm.models.backends import BuildBackend
from pdm.models.markers import Marker
from unearth import Link
from pdm._types import RequirementDict

if TYPE_CHECKING:
    ...
VCS_SCHEMA = ...
_vcs_req_re = ...
_file_req_re = ...
_egg_info_re = ...
T = TypeVar("T", bound="Requirement")
ALLOW_ANY = ...
def strip_extras(line: str) -> tuple[str, tuple[str, ...] | None]:
    ...

@dataclasses.dataclass(eq=False)
class Requirement:
    """Base class of a package requirement.
    A requirement is a (virtual) specification of a package which contains
    some constraints of version, python version, or other marker.
    """
    name: str | None = ...
    marker: Marker | None = ...
    extras: Sequence[str] | None = ...
    specifier: SpecifierSet = ...
    editable: bool = ...
    prerelease: bool | None = ...
    groups: list[str] = ...
    def __post_init__(self) -> None:
        ...

    @property
    def project_name(self) -> str | None:
        ...

    @property
    def key(self) -> str | None:
        ...

    @property
    def is_pinned(self) -> bool:
        ...

    def as_pinned_version(self: T, other_version: str | None) -> T:
        """Return a new requirement with the given pinned version."""
        ...

    def __hash__(self) -> int:
        ...

    def __eq__(self, o: object) -> bool:
        ...

    def identify(self) -> str:
        ...

    def __repr__(self) -> str:
        ...

    def __str__(self) -> str:
        ...

    @classmethod
    def create(cls: type[T], **kwargs: Any) -> T:
        ...

    @classmethod
    def from_dist(cls, dist: Distribution) -> Requirement:
        ...

    @classmethod
    def from_req_dict(cls, name: str, req_dict: RequirementDict) -> Requirement:
        ...

    @property
    def is_named(self) -> bool:
        ...

    @property
    def is_vcs(self) -> bool:
        ...

    @property
    def is_file_or_url(self) -> bool:
        ...

    def as_line(self) -> str:
        ...

    def matches(self, line: str) -> bool:
        """Return whether the passed in PEP 508 string
        is the same requirement as this one.
        """
        ...

    @classmethod
    def from_pkg_requirement(cls, req: PackageRequirement) -> Requirement:
        ...



@dataclasses.dataclass(eq=False)
class NamedRequirement(Requirement):
    def as_line(self) -> str:
        ...



@dataclasses.dataclass(eq=False)
class FileRequirement(Requirement):
    url: str = ...
    path: Path | None = ...
    subdirectory: str | None = ...
    def __post_init__(self) -> None:
        ...

    def guess_name(self) -> str | None:
        ...

    @classmethod
    def create(cls: type[T], **kwargs: Any) -> T:
        ...

    @property
    def str_path(self) -> str | None:
        ...

    def relocate(self, backend: BuildBackend) -> None:
        """Change the project root to the given path"""
        ...

    @property
    def is_local(self) -> bool:
        ...

    @property
    def is_local_dir(self) -> bool:
        ...

    def as_file_link(self) -> Link:
        ...

    def get_full_url(self) -> str:
        ...

    def as_line(self) -> str:
        ...



@dataclasses.dataclass(eq=False)
class VcsRequirement(FileRequirement):
    vcs: str = ...
    ref: str | None = ...
    revision: str | None = ...
    def __post_init__(self) -> None:
        ...

    def get_full_url(self) -> str:
        ...



def filter_requirements_with_extras(requirement_lines: list[str], extras: Sequence[str], include_default: bool = ...) -> list[str]:
    """Filter the requirements with extras.
    If extras are given, return those with matching extra markers.
    Otherwise, return those without extra markers.
    """
    ...

def parse_as_pkg_requirement(line: str) -> PackageRequirement:
    """Parse a requirement line as packaging.requirement.Requirement"""
    ...

def parse_requirement(line: str, editable: bool = ...) -> Requirement:
    ...
