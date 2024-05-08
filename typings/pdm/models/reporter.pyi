"""
This type stub file was generated by pyright.
"""

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING
from rich.progress import Progress, TaskID

if TYPE_CHECKING:
    ...
class BaseReporter:
    def report_download(self, link: Any, completed: int, total: int | None) -> None:
        ...

    def report_build_start(self, filename: str) -> None:
        ...

    def report_build_end(self, filename: str) -> None:
        ...

    def report_unpack(self, filename: str, completed: int, total: int | None) -> None:
        ...



@dataclass
class RichProgressReporter(BaseReporter):
    progress: Progress
    task_id: TaskID
    def report_download(self, link: Any, completed: int, total: int | None) -> None:
        ...

    def report_unpack(self, filename: str, completed: int, total: int | None) -> None:
        ...

    def report_build_start(self, filename: str) -> None:
        ...

    def report_build_end(self, filename: str) -> None:
        ...
