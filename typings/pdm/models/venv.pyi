"""
This type stub file was generated by pyright.
"""

import dataclasses as dc
from functools import cached_property
from pathlib import Path

IS_WIN = ...
BIN_DIR = ...
def get_venv_python(venv: Path) -> Path:
    """Get the interpreter path inside the given venv."""
    ...

def is_conda_venv(root: Path) -> bool:
    ...

@dc.dataclass(frozen=True)
class VirtualEnv:
    root: Path
    is_conda: bool
    interpreter: Path
    @classmethod
    def get(cls, root: Path) -> VirtualEnv | None:
        ...

    @classmethod
    def from_interpreter(cls, interpreter: Path) -> VirtualEnv | None:
        ...

    def env_vars(self) -> dict[str, str]:
        ...

    @cached_property
    def venv_config(self) -> dict[str, str]:
        ...

    @property
    def include_system_site_packages(self) -> bool:
        ...

    @cached_property
    def base_paths(self) -> list[str]:
        ...
