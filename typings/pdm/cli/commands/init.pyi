"""
This type stub file was generated by pyright.
"""

import argparse
from typing import Any, TYPE_CHECKING
from pdm.cli.commands.base import BaseCommand
from pdm.cli.hooks import HookManager
from pdm.project import Project

if TYPE_CHECKING:
    ...
class Command(BaseCommand):
    """Initialize a pyproject.toml for PDM"""
    def __init__(self) -> None:
        ...

    def do_init(self, project: Project, options: argparse.Namespace) -> None:
        """Bootstrap the project and create a pyproject.toml"""
        ...

    def set_interactive(self, value: bool) -> None:
        ...

    def ask(self, question: str, default: str) -> str:
        ...

    def ask_project(self, project: Project) -> str:
        ...

    def get_metadata_from_input(self, project: Project, options: argparse.Namespace) -> dict[str, Any]:
        ...

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        ...

    def set_python(self, project: Project, python: str | None, hooks: HookManager) -> None:
        ...

    def handle(self, project: Project, options: argparse.Namespace) -> None:
        ...
