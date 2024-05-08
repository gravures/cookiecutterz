"""
This type stub file was generated by pyright.
"""

from concurrent.futures import ThreadPoolExecutor
from functools import cached_property
from typing import Any, Callable, Collection, TYPE_CHECKING, TypeVar
from rich.progress import Progress
from pdm.environments import BaseEnvironment
from pdm.installers.manager import InstallManager
from pdm.models.candidates import Candidate
from pdm.compat import Distribution

if TYPE_CHECKING:
    ...
_T = TypeVar("_T")
class DummyFuture:
    _NOT_SET = ...
    def __init__(self) -> None:
        ...

    def set_result(self, result: Any) -> None:
        ...

    def set_exception(self, exc: Exception) -> None:
        ...

    def result(self) -> Any:
        ...

    def exception(self) -> Exception | None:
        ...

    def add_done_callback(self: _T, func: Callable[[_T], Any]) -> None:
        ...

    def cancel(self) -> bool:
        ...



class DummyExecutor:
    """A synchronous pool class to mimic ProcessPoolExecuter's interface.
    functions are called and awaited for the result
    """
    def submit(self, func: Callable, *args: Any, **kwargs: Any) -> DummyFuture:
        ...

    def __enter__(self: _T) -> _T:
        ...

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        ...



def editables_candidate(environment: BaseEnvironment) -> Candidate | None:
    """Return a candidate for `editables` package"""
    ...

class BaseSynchronizer:
    """Synchronize the working set with given installation candidates

    :param candidates: a dict of candidates to be installed
    :param environment: the environment associated with the project
    :param clean: clean unneeded packages
    :param dry_run: only prints summary but do not install or uninstall
    :param retry_times: retry times when installation failed
    :param install_self: whether to install self project
    :param no_editable: if True, override all editable installations,
        if a list, override editables with the given names
    :param use_install_cache: whether to use install cache
    :param reinstall: whether to reinstall all packages
    :param only_keep: If true, only keep the selected candidates
    :param fail_fast: If true, stop the installation on first error
    """
    SEQUENTIAL_PACKAGES = ...
    def __init__(self, candidates: dict[str, Candidate], environment: BaseEnvironment, clean: bool = ..., dry_run: bool = ..., retry_times: int = ..., install_self: bool = ..., no_editable: bool | Collection[str] = ..., reinstall: bool = ..., only_keep: bool = ..., fail_fast: bool = ..., use_install_cache: bool | None = ...) -> None:
        ...

    @cached_property
    def self_candidate(self) -> Candidate:
        """Return the candidate for self project"""
        ...

    @cached_property
    def candidates(self) -> dict[str, Candidate]:
        """Return the candidates to be installed"""
        ...

    def should_install_editables(self) -> bool:
        """Return whether to add editables"""
        ...

    @property
    def manager(self) -> InstallManager:
        ...

    def get_manager(self, rename_pth: bool = ...) -> InstallManager:
        ...

    @property
    def self_key(self) -> str | None:
        ...

    def compare_with_working_set(self) -> tuple[list[str], list[str], list[str]]:
        """Compares the candidates and return (to_add, to_update, to_remove)"""
        ...

    def synchronize(self) -> None:
        """Synchronize the working set with pinned candidates."""
        ...



class Synchronizer(BaseSynchronizer):
    def create_executor(self) -> ThreadPoolExecutor | DummyExecutor:
        ...

    def install_candidate(self, key: str, progress: Progress) -> Candidate:
        """Install candidate"""
        ...

    def update_candidate(self, key: str, progress: Progress) -> tuple[Distribution, Candidate]:
        """Update candidate"""
        ...

    def remove_distribution(self, key: str, progress: Progress) -> Distribution:
        """Remove distributions with given names."""
        ...

    def synchronize(self) -> None:
        ...
