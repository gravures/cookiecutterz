"""
This type stub file was generated by pyright.
"""

import abc
import unearth
from contextlib import contextmanager
from functools import cached_property
from typing import Generator, TYPE_CHECKING, no_type_check
from pdm.models.python import PythonInfo
from pdm.models.working_set import WorkingSet
from pdm._types import RepositoryConfig
from pdm.models.session import PDMPyPIClient
from pdm.project import Project

if TYPE_CHECKING:
    ...
@no_type_check
def get_paths_wrapper(get_paths): # -> _Wrapped[Callable[..., Any], Any, Callable[..., Any], dict[str, str]]:
    ...

class BaseEnvironment(abc.ABC):
    """Environment dependent stuff related to the selected Python interpreter."""
    project: Project
    is_local = ...
    def __init_subclass__(cls) -> None:
        ...

    def __init__(self, project: Project, *, python: str | None = ...) -> None:
        """
        :param project: the project instance
        """
        ...

    @property
    def is_global(self) -> bool:
        """For backward compatibility, it is opposite to ``is_local``."""
        ...

    @property
    def interpreter(self) -> PythonInfo:
        ...

    @abc.abstractmethod
    def get_paths(self, dist_name: str | None = ...) -> dict[str, str]:
        """Get paths like ``sysconfig.get_paths()`` for installation.

        :param dist_name: The package name to be installed, if any.
        """
        ...

    @property
    def process_env(self) -> dict[str, str]:
        """Get the process env var dict for the environment."""
        ...

    @cached_property
    def target_python(self) -> unearth.TargetPython:
        ...

    @cached_property
    def session(self) -> PDMPyPIClient:
        """Build the session and cache it."""
        ...

    @contextmanager
    def get_finder(self, sources: list[RepositoryConfig] | None = ..., ignore_compatibility: bool = ..., minimal_version: bool = ...) -> Generator[unearth.PackageFinder, None, None]:
        """Return the package finder of given index sources.

        :param sources: a list of sources the finder should search in.
        :param ignore_compatibility: whether to ignore the python version
            and wheel tags.
        """
        ...

    def get_working_set(self) -> WorkingSet:
        """Get the working set based on local packages directory."""
        ...

    @cached_property
    def marker_environment(self) -> dict[str, str]:
        """Get environment for marker evaluation"""
        ...

    def which(self, command: str) -> str | None:
        """Get the full path of the given executable against this environment."""
        ...

    @cached_property
    def pip_command(self) -> list[str]:
        """Get a pip command for this environment, and download one if not available.
        Return a list of args like ['python', '-m', 'pip']
        """
        ...

    @property
    def script_kind(self) -> str:
        ...



class BareEnvironment(BaseEnvironment):
    """Bare environment that does not depend on project files."""
    def __init__(self, project: Project) -> None:
        ...

    def get_paths(self, dist_name: str | None = ...) -> dict[str, str]:
        ...

    def get_working_set(self) -> WorkingSet:
        ...
