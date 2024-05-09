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
from cookiecutter.generate import generate_file
from cookiecutter.hooks import run_hook, run_pre_prompt_hook

from cookiecutterz._version import __version__
from cookiecutterz.extensions import (
    Master,
    install_inherited_templates,
    load_inherited_jinja_templates,
)


if TYPE_CHECKING:
    import os

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
def run_hook_patched(
    hook_name: str,
    project_dir: str,
    context: dict[str, Any],
) -> None:
    """Main entry point in template generation process."""
    if hook_name == "post_gen_project":
        run_hook(hook_name, project_dir, context)
    elif hook_name == "pre_gen_project":
        context["cookiecutter"]["_cwd"] = str(Path.cwd())
        run_hook(hook_name, project_dir, context)
        install_inherited_templates(project_dir, context)


def run_pre_prompt_hook_patched(repo_dir: os.PathLike[str]) -> Path:
    work_dir: Path = run_pre_prompt_hook(repo_dir)
    master = Master(repo=Path(repo_dir), work_dir=Path(work_dir))
    return master.work_dir


def generate_file_patched(
    project_dir: str,
    infile: str,
    context: dict[str, Any],
    env: jinja2.Environment,
    skip_if_file_exists: bool = False,
):
    """Patch for loading inherited jinja templates in jinja environment."""
    env = load_inherited_jinja_templates(context, env)
    generate_file(project_dir, infile, context, env, skip_if_file_exists)


# Applying patched functions
hooks.run_pre_prompt_hook = run_pre_prompt_hook_patched
hooks.run_hook = run_hook_patched
generate.generate_file = generate_file_patched
uncache(["cookiecutter.hooks", "cookiecutter.generate"])
