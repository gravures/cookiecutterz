# Copyright (c) 2023 - Gilles Coissac
# See end of file for extended copyright information
"""A cookiecutter extension package."""
from __future__ import annotations

import sys
from pathlib import Path

from cookiecutter import generate, hooks
from cookiecutter.generate import _run_hook_from_repo_dir, generate_file
from cookiecutter.hooks import run_hook

from cookiecutterz.extensions import (
    install_inherited,
    load_inherited_templates,
)


def uncache(exclude):
    """Remove package modules from cache except excluded ones."""
    pkgs = []
    for mod in exclude:
        pkg = mod.split(".", 1)[0]
        pkgs.append(pkg)

    to_uncache = []
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


##
# MONKEY PATCHING COOKIECUTTER


def __run_hook_from_repo_dir(
    repo_dir,
    hook_name,
    project_dir,
    context,
    delete_project_on_failure,
):
    """Hook for registring cwd for further update of project."""
    if hook_name == "pre_gen_project":  # noqa: PLR2004
        context["cookiecutter"]["_cwd"] = str(Path.cwd())
    _run_hook_from_repo_dir(
        repo_dir,
        hook_name,
        project_dir,
        context,
        delete_project_on_failure,
    )


def _run_hook(hook_name: str, project_dir: str, context: dict):
    """Hook for installing inherited templates if provided."""
    run_hook(hook_name, project_dir, context)
    if hook_name == "pre_gen_project":  # noqa: PLR2004
        install_inherited(project_dir, context)


def _generate_file(
    project_dir,
    infile,
    context,
    env,
    skip_if_file_exists=False,
):
    """Hook for loading inherited jinja templates in jinja environment."""
    env = load_inherited_templates(context, env)
    generate_file(project_dir, infile, context, env, skip_if_file_exists)


generate._run_hook_from_repo_dir = __run_hook_from_repo_dir
# generate._run_hook = hooks.run_hook = _run_hook  # type: ignore - generate._run_hook !?
hooks.run_hook = _run_hook
generate.generate_file = _generate_file
uncache(["cookiecutter.hooks", "cookiecutter.generate"])


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
