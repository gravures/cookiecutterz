"""
This type stub file was generated by pyright.
"""

import argparse
from pdm.cli.commands.base import BaseCommand
from pdm.cli.hooks import HookManager
from pdm.models.python import PythonInfo
from pdm.project import Project

class Command(BaseCommand):
    """Use the given python version or path as base interpreter. If not found, PDM will try to install one."""
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        ...

    @staticmethod
    def select_python(project: Project, python: str, *, ignore_remembered: bool, ignore_requires_python: bool, venv: str | None, first: bool) -> PythonInfo:
        ...

    def do_use(self, project: Project, python: str = ..., first: bool = ..., ignore_remembered: bool = ..., ignore_requires_python: bool = ..., save: bool = ..., venv: str | None = ..., hooks: HookManager | None = ...) -> PythonInfo:
        """Use the specified python version and save in project config.
        The python can be a version string or interpreter path.
        """
        ...

    def handle(self, project: Project, options: argparse.Namespace) -> None:
        ...
