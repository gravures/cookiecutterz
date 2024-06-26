"""
This type stub file was generated by pyright.
"""

from dataclasses import dataclass
from typing import Any, overload
from dep_logic.markers import BaseMarker
from packaging.markers import Marker as PackageMarker
from pdm.models.specifiers import PySpecSet

@dataclass(frozen=True, unsafe_hash=True, repr=False)
class Marker:
    inner: BaseMarker
    def __and__(self, other: Any) -> Marker:
        ...

    def __or__(self, other: Any) -> Marker:
        ...

    def is_any(self) -> bool:
        ...

    def is_empty(self) -> bool:
        ...

    def __str__(self) -> str:
        ...

    def __repr__(self) -> str:
        ...

    def evaluate(self, environment: dict[str, Any] | None = ...) -> bool:
        ...

    def split_pyspec(self) -> tuple[Marker, PySpecSet]:
        """Split `python_version` and `python_full_version` from marker string"""
        ...

    def split_extras(self) -> tuple[Marker, Marker]:
        """An element can be stripped from the marker only if all parts are connected
        with `and` operator. The rest part are returned as a string or `None` if all are
        stripped.
        """
        ...



@overload
def get_marker(marker: None) -> None:
    ...

@overload
def get_marker(marker: PackageMarker | Marker | str) -> Marker:
    ...

def get_marker(marker: PackageMarker | Marker | str | None) -> Marker | None:
    ...
