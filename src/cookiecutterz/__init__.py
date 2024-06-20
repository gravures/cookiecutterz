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

from pathlib import Path
from typing import TYPE_CHECKING, Any

import cookiecutterz.inheritance
from cookiecutterz._version import __version__
from cookiecutterz.importer import monkey
from cookiecutterz.inheritance import Master
from cookiecutterz.jenvironment import SharedEnvironment
from cookiecutterz.types import Context, Repo, Url


if TYPE_CHECKING:
    import jinja2


__all__ = ["__version__"]


# MONKEY PATCHING COOKIECUTTER
@monkey(module="cookiecutter.repository", target="determine_repo_dir")
def determine_repo_dir_patch(  # noqa: PLR0917
    template: str,
    abbreviations: dict[str, str],
    clone_to_dir: Path | str,
    checkout: str | None,
    no_input: bool,
    password: str | None = None,
    directory: str | None = None,
) -> tuple[str, bool]:
    """Main entry point in template generation process."""
    repo = Repo(
        url=Url(template, abbreviations=abbreviations),
        directory=directory or "",
    )
    Master(repo=repo)
    return repo.clone(
        location=Path(clone_to_dir),
        checkout=checkout,
        no_input=no_input,
        password=password,
    )


@monkey(module="cookiecutter.hooks", target="run_hook")
def run_hook_patch(
    hook_name: str,
    project_dir: str,
    context: dict[str, Any],
) -> None:
    """Secondary entry point in template generation process.

    Those will happened inside te generate_files() cookicutter function.
    """
    origin = monkey.target("cookiecutter.hooks.run_hook")
    if hook_name == "post_gen_project":
        origin(hook_name, project_dir, context)
    elif hook_name == "pre_gen_project":
        origin(hook_name, project_dir, context)
        master = Master()
        master.install_bases(project_dir, Context(context=context))


@monkey(module="cookiecutter.utils", target="create_tmp_repo_dir")
def create_tmp_repo_dir_patch(repo_dir: Path | str) -> Path:
    """Create a temporary dir with a copy of the contents of repo_dir.

    Raises: RuntimeError if a corresponding Repo instance cannot be found.
    """
    if not (repo := Repo.get(location=Path(repo_dir))):
        raise RuntimeError
    repo.clone_workspace()
    return repo.workspace


@monkey(module="cookiecutter.config", target="get_user_config")
def get_user_config_patch(
    config_file: str | None = None,
    default_config: bool | dict[str, Any] = False,
) -> dict[str, Any]:
    """Register user config globally."""
    origin = monkey.target("cookiecutter.config.get_user_config")
    cookiecutterz.inheritance.user_config = origin(
        config_file=config_file, default_config=default_config
    )
    return cookiecutterz.inheritance.user_config


@monkey(module="cookiecutter.utils", target="create_env_with_context")
def create_env_with_template(**_kwargs: Any) -> jinja2.Environment:
    """Patch for updating jinja environment with inherited templates.

    Create a jinja environment using the provided current template.
    """
    master = Master()
    return SharedEnvironment(template=master.get_current_template())


monkey.apply_all()
