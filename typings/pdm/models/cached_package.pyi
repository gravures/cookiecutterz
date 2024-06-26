"""
This type stub file was generated by pyright.
"""

from functools import cached_property
from pathlib import Path
from typing import Any, ClassVar, ContextManager

class CachedPackage:
    """A package cached in the central package store.
    The directory name is similar to wheel's filename:

        $PACKAGE_ROOT/<checksum[:2]>/<dist_name>-<version>-<impl>-<abi>-<plat>/

    The checksum is stored in a file named `.checksum` under the directory.

    Under the directory there could be a text file named `.referrers`.
    Each line of the file is a distribution path that refers to this package.
    *Only wheel installations will be cached*
    """
    cache_files: ClassVar[tuple[str, ...]] = ...
    def __init__(self, path: str | Path, original_wheel: Path | None = ...) -> None:
        ...

    def lock(self) -> ContextManager[Any]:
        ...

    @cached_property
    def checksum(self) -> str:
        """The checksum of the path"""
        ...

    @cached_property
    def dist_info(self) -> Path:
        """The dist-info directory of the wheel"""
        ...

    @property
    def referrers(self) -> set[str]:
        """A set of entries in referrers file"""
        ...

    def add_referrer(self, path: str) -> None:
        """Add a new referrer"""
        ...

    def remove_referrer(self, path: str) -> None:
        """Remove a referrer"""
        ...

    def cleanup(self) -> None:
        ...
