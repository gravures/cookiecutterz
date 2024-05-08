"""
This type stub file was generated by pyright.
"""

import enum
from functools import cached_property
from typing import Any, Iterable, Mapping
from pdm.project.toml_file import TOMLBase

GENERATED_COMMENTS = ...
FLAG_STATIC_URLS = ...
FLAG_CROSS_PLATFORM = ...
FLAG_DIRECT_MINIMAL_VERSIONS = ...
FLAG_INHERIT_METADATA = ...
SUPPORTED_FLAGS = ...
class Compatibility(enum.IntEnum):
    NONE = ...
    SAME = ...
    BACKWARD = ...
    FORWARD = ...


class Lockfile(TOMLBase):
    spec_version = ...
    @cached_property
    def default_strategies(self) -> set[str]:
        ...

    @property
    def hash(self) -> str:
        ...

    @property
    def file_version(self) -> str:
        ...

    @property
    def groups(self) -> list[str] | None:
        ...

    @property
    def strategy(self) -> set[str]:
        ...

    def apply_strategy_change(self, changes: Iterable[str]) -> set[str]:
        ...

    def compare_groups(self, groups: Iterable[str]) -> list[str]:
        ...

    def set_data(self, data: Mapping[str, Any]) -> None:
        ...

    def write(self, show_message: bool = ...) -> None:
        ...

    def __getitem__(self, key: str) -> dict:
        ...

    def compatibility(self) -> Compatibility:
        """We use a three-part versioning scheme for lockfiles:
        The first digit represents backward compatibility and the second digit represents forward compatibility.
        """
        ...
