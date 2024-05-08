"""
This type stub file was generated by pyright.
"""

from pathlib import Path
from typing import List, Optional
from cruft import _commands

"""This module defines CLI interactions when using `cruft`."""
app = ...
@app.command(short_help="Check if the linked Cookiecutter template has been updated", help=_get_help_string(_commands.check))
def check(project_dir: Path = ..., checkout: Optional[str] = ..., strict: bool = ...) -> None:
    ...

@app.command(short_help="Create a new project from a Cookiecutter template", help=_get_help_string(_commands.create))
def create(template_git_url: str = ..., output_dir: Path = ..., config_file: Optional[Path] = ..., default_config: bool = ..., extra_context: str = ..., no_input: bool = ..., directory: Optional[str] = ..., checkout: Optional[str] = ..., overwrite_if_exists: bool = ..., skip: Optional[List[str]] = ...) -> None:
    ...

@app.command(short_help="Link an existing project to a Cookiecutter template", help=_get_help_string(_commands.link))
def link(template_git_url: str = ..., project_dir: Path = ..., checkout: Optional[str] = ..., no_input: bool = ..., config_file: Optional[Path] = ..., default_config: bool = ..., extra_context: str = ..., directory: Optional[str] = ...) -> None:
    ...

@app.command(short_help="Update the project to the latest version of the linked Cookiecutter template", help=_get_help_string(_commands.update))
def update(project_dir: Path = ..., cookiecutter_input: bool = ..., refresh_private_variables: bool = ..., skip_apply_ask: bool = ..., skip_update: bool = ..., checkout: Optional[str] = ..., strict: bool = ..., allow_untracked_files: bool = ..., extra_context: str = ..., extra_context_file: Path = ...) -> None:
    ...

@app.command(short_help="Show the diff between the project and the current cruft template", help=_get_help_string(_commands.diff))
def diff(project_dir: Path = ..., exit_code: bool = ..., checkout: Optional[str] = ...) -> None:
    ...