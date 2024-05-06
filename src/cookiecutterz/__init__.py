# Copyright (c) 2023 - Gilles Coissac
# This file is part of Cookicutterz program.
#
# Cookiecutterz is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# Cookiecutterz is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cookiecutterz. If not, see <https://www.gnu.org/licenses/>
"""A cookiecutter extension package."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from cookiecutter import generate, hooks
from cookiecutter.generate import (
    _run_hook_from_repo_dir,  # pyright: ignore[reportAttributeAccessIssue]
    generate_file,
)
from cookiecutter.hooks import run_hook

from cookiecutterz._version import __version__
from cookiecutterz.extensions import (
    install_inherited,
    load_inherited_templates,
)


if TYPE_CHECKING:
    import jinja2

__all__ = ["__version__"]


def uncache(exclude: list[str]) -> None:
    """Remove package modules from cache except excluded ones."""
    pkgs: list[str] = []
    for mod in exclude:
        pkg = mod.split(".", 1)[0]
        pkgs.append(pkg)

    to_uncache: list[str] = []
    for mod in sys.modules:
        if mod in exclude:
            continue
        if mod in pkgs:
            to_uncache.append(mod)
            continue
        for pkg in pkgs:
            if mod.startswith(f"{pkg}."):
                to_uncache.append(mod)
                break
    for mod in to_uncache:
        del sys.modules[mod]


# MONKEY PATCHING COOKIECUTTER
def __run_hook_from_repo_dir(
    repo_dir: str,
    hook_name: str,
    project_dir: str,
    context: dict[str, Any],
    delete_project_on_failure: bool,
) -> None:
    """Hook for registering cwd for further update of project."""
    if hook_name == "pre_gen_project":
        context["cookiecutter"]["_cwd"] = str(Path.cwd())
    _run_hook_from_repo_dir(
        repo_dir,
        hook_name,
        project_dir,
        context,
        delete_project_on_failure,
    )


def _run_hook(hook_name: str, project_dir: str, context: dict[str, Any]) -> None:
    """Hook for installing inherited templates if provided."""
    run_hook(hook_name, project_dir, context)
    if hook_name == "pre_gen_project":
        install_inherited(project_dir, context)


def _generate_file(
    project_dir: str,
    infile: str,
    context: dict[str, Any],
    env: jinja2.Environment,
    skip_if_file_exists: bool = False,
):
    """Hook for loading inherited jinja templates in jinja environment."""
    env = load_inherited_templates(context, env)
    generate_file(project_dir, infile, context, env, skip_if_file_exists)


generate._run_hook_from_repo_dir = __run_hook_from_repo_dir  # pyright: ignore[reportAttributeAccessIssue]
# generate._run_hook = hooks.run_hook = _run_hook
hooks.run_hook = _run_hook
generate.generate_file = _generate_file
uncache(["cookiecutter.hooks", "cookiecutter.generate"])
