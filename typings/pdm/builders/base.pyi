"""
This type stub file was generated by pyright.
"""

import subprocess
import threading
from logging import Logger
from pathlib import Path
from typing import Any, ClassVar, Iterable, TYPE_CHECKING
from pyproject_hooks import BuildBackendHookCaller
from pdm.environments import BaseEnvironment
from pdm.exceptions import BuildError
from pdm.models.requirements import Requirement

if TYPE_CHECKING:
    ...
class LoggerWrapper(threading.Thread):
    """
    Read messages from a pipe and redirect them
    to a logger (see python's logging module).
    """
    def __init__(self, logger: Logger, level: int) -> None:
        ...

    def fileno(self) -> int:
        ...

    @staticmethod
    def remove_newline(msg: str) -> str:
        ...

    def run(self) -> None:
        ...

    def stop(self) -> None:
        ...



def build_error(e: subprocess.CalledProcessError) -> BuildError:
    """Get a build error with meaningful error message
    from the subprocess output.
    """
    ...

def log_subprocessor(cmd: list[str], cwd: str | Path | None = ..., extra_environ: dict[str, str] | None = ...) -> None:
    ...

class _Prefix:
    def __init__(self, executable: str, shared: str, overlay: str) -> None:
        ...



class EnvBuilder:
    """A simple PEP 517 builder for an isolated environment"""
    DEFAULT_BACKEND: ClassVar[dict[str, Any]] = ...
    _shared_envs: ClassVar[dict[int, str]] = ...
    _overlay_envs: ClassVar[dict[str, str]] = ...
    if TYPE_CHECKING:
        _hook: BuildBackendHookCaller
        _requires: list[str]
        _prefix: _Prefix
        ...
    def get_shared_env(self, key: int) -> str:
        ...

    def get_overlay_env(self, key: str) -> str:
        ...

    def __init__(self, src_dir: str | Path, environment: BaseEnvironment) -> None:
        """If isolated is True(default), the builder will set up a *clean* environment.
        Otherwise, the environment of the host Python will be used.
        """
        ...

    def init_build_system(self, build_system: dict[str, Any]) -> None:
        """Initialize the build system and requires list from the PEP 517 spec"""
        ...

    def subprocess_runner(self, cmd: list[str], cwd: str | Path | None = ..., extra_environ: dict[str, str] | None = ..., isolated: bool = ...) -> None:
        ...

    def check_requirements(self, reqs: Iterable[str]) -> Iterable[Requirement]:
        ...

    def install(self, requirements: Iterable[str], shared: bool = ...) -> None:
        ...

    def prepare_metadata(self, out_dir: str) -> str:
        """Prepare metadata and store in the out_dir.
        Some backends doesn't provide that API, in that case the metadata will be
        retrieved from the built result.
        """
        ...

    def build(self, out_dir: str, metadata_directory: str | None = ...) -> str:
        """Build and store the artifact in out_dir,
        return the absolute path of the built result.
        """
        ...