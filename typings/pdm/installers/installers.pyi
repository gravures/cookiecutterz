"""
This type stub file was generated by pyright.
"""

from functools import cached_property
from pathlib import Path
from typing import Any, BinaryIO, Iterable, Iterator, Literal, TYPE_CHECKING
from installer.destinations import Scheme, SchemeDictionaryDestination, WheelDestination
from installer.records import RecordEntry
from installer.sources import WheelContentElement, WheelFile as _WheelFile, WheelSource
from pdm.models.cached_package import CachedPackage
from pdm.environments import BaseEnvironment

if TYPE_CHECKING:
    LinkMethod = Literal["symlink", "hardlink", "copy"]
class WheelFile(_WheelFile):
    @cached_property
    def dist_info_dir(self) -> str:
        ...



class PackageWheelSource(WheelSource):
    def __init__(self, package: CachedPackage) -> None:
        ...

    @cached_property
    def dist_info_dir(self) -> str:
        ...

    @property
    def dist_info_filenames(self) -> list[str]:
        ...

    def read_dist_info(self, filename: str) -> str:
        ...

    def iter_files(self) -> Iterable[Path]:
        ...

    def get_contents(self) -> Iterator[WheelContentElement]:
        ...



class InstallDestination(SchemeDictionaryDestination):
    def __init__(self, *args: Any, link_method: LinkMethod = ..., rename_pth: bool = ..., **kwargs: Any) -> None:
        ...

    def write_to_fs(self, scheme: Scheme, path: str, stream: BinaryIO, is_executable: bool) -> RecordEntry:
        ...



def install_wheel(wheel: Path, environment: BaseEnvironment, direct_url: dict[str, Any] | None = ..., install_links: bool = ..., rename_pth: bool = ...) -> str:
    """Only create .pth files referring to the cached package.
    If the cache doesn't exist, create one.
    """
    ...

def install(source: WheelSource, destination: WheelDestination, additional_metadata: dict[str, bytes] | None = ...) -> str:
    """A lower level installation method that is copied from installer
    but is controlled by extra parameters.

    Return the .dist-info path
    """
    ...
