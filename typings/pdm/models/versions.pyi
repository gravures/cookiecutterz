"""
This type stub file was generated by pyright.
"""

from typing import Any, Literal, TYPE_CHECKING, Union, overload

if TYPE_CHECKING:
    VersionBit = Union[int, Literal["*"]]
PRE_RELEASE_SEGMENT_RE = ...
class Version:
    """A loosely semantic version implementation that allows '*' in version part.

    This class is designed for Python specifier set merging only, hence up to 3 version
    parts are kept, plus optional prerelease suffix.

    This is a slightly different purpose than packaging.version.Version which is
    focused on supporting PEP 440 version identifiers, not specifiers.
    """
    MIN: Version
    MAX: Version
    pre: tuple[str, int] | None = ...
    def __init__(self, version: tuple[VersionBit, ...] | str) -> None:
        ...

    def complete(self, complete_with: VersionBit = ..., max_bits: int = ...) -> Version:
        """
        Complete the version with the given bit if the version has less than max parts
        """
        ...

    def bump(self, idx: int = ...) -> Version:
        """Bump version by incrementing 1 on the given index of version part.
        If index is not provided: increment the last version bit unless version
        is a pre-release, in which case, increment the pre-release number.
        """
        ...

    def startswith(self, other: Version) -> bool:
        """Check if the version begins with another version."""
        ...

    @property
    def is_wildcard(self) -> bool:
        """Check if the version ends with a '*'"""
        ...

    @property
    def is_prerelease(self) -> bool:
        """Check if the version is a prerelease."""
        ...

    def __str__(self) -> str:
        ...

    def __repr__(self) -> str:
        ...

    def __eq__(self, other: Any) -> bool:
        ...

    def __lt__(self, other: Any) -> bool:
        ...

    def __gt__(self, other: Any) -> bool:
        ...

    def __le__(self, other: Any) -> bool:
        ...

    def __ge__(self, other: Any) -> bool:
        ...

    @overload
    def __getitem__(self, idx: int) -> VersionBit:
        ...

    @overload
    def __getitem__(self, idx: slice) -> Version:
        ...

    def __getitem__(self, idx: int | slice) -> VersionBit | Version:
        ...

    def __setitem__(self, idx: int, value: VersionBit) -> None:
        ...

    def __hash__(self) -> int:
        ...

    @property
    def is_py2(self) -> bool:
        ...
