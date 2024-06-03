# Copyright (c) 2023 - Gilles Coissac
# This file is part of Cookiecutterz program.
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

from cookiecutter import hooks, prompt, utils
from cookiecutter.hooks import run_hook, run_pre_prompt_hook

from cookiecutterz._version import __version__
from cookiecutterz.inheritance import Master, SharedEnvironment


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
        run_hook(hook_name, project_dir, context)
        master = Master()
        master.install_templates(project_dir, context)


def run_pre_prompt_hook_patched(repo_dir: os.PathLike[str]) -> Path:
    work_dir: Path = run_pre_prompt_hook(repo_dir)
    master = Master(repo=Path(repo_dir), work_dir=Path(work_dir))
    return master.template.repo


def create_env_with_context_patched(context: dict[str, Any]) -> jinja2.Environment:
    """Patch for updating jinja environment with inherited templates.

    Create a jinja environment using the provided context.
    """
    master = Master()
    env_vars = context.get("cookiecutter", {}).get("_jinja2_env_vars", {})
    context["cookiecutter"].setdefault("_repo_dir", str(master.get_current_template().repo))
    return SharedEnvironment(
        context=context,
        keep_trailing_newline=True,
        **env_vars,
    )


# Applying patched functions
hooks.run_pre_prompt_hook = run_pre_prompt_hook_patched
hooks.run_hook = run_hook_patched
prompt.create_env_with_context = create_env_with_context_patched  # pyright: ignore[reportAttributeAccessIssue]
hooks.create_env_with_context = create_env_with_context_patched  # pyright: ignore[reportAttributeAccessIssue]
utils.create_env_with_context = create_env_with_context_patched
uncache(["cookiecutter.hooks", "cookiecutter.utils", "cookiecutter.prompt"])
