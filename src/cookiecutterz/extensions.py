# Copyright (c) 2023 - Gilles Coissac
# See end of file for extended copyright information
"""Extensions module for cookiecutter."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from cookiecutter import config, main, repository
from cookiecutter.exceptions import CookiecutterException
from jinja2 import Environment, FileSystemLoader


class UpdateException(CookiecutterException):
    """Exception for update command."""

    def __init__(self, message):
        """Exception for update command."""
        self.message = message

    def __str__(self):
        """Text representation of UndefinedVariableInTemplate."""
        return self.message


def get_public_keys(context: dict) -> dict:
    """Filter out private keys from a context."""
    return {k: v for k, v in context.items() if not k.startswith("_")}


def load_inherited_templates(context: dict, env: Environment) -> Environment:
    """Load inherited jinja templates in jinja environment."""
    if ancestors_templates := context.get("cookiecutter", {}).get(
        "_ancestors_templates",
        [],
    ):
        env.loader = FileSystemLoader([".", "../templates", *ancestors_templates])
    return env


def install_inherited(project_dir: str, context: dict) -> None:
    """Install inherited cookiecutter templates."""
    _context: dict[str, Any] = context.get("cookiecutter", {})
    extends: list[str] = _context.get("_extends", [])
    if not extends:
        return

    public_keys: dict = get_public_keys(_context)
    this_repo: Path = Path(_context.get("_repo_dir", ""))
    this_repo = this_repo if this_repo.is_absolute() else Path.cwd()
    config_dict = config.get_user_config()
    ancestors_templates = []

    for ancestor in extends:
        repo, _ = repository.determine_repo_dir(
            template=ancestor,
            abbreviations=config_dict["abbreviations"],
            clone_to_dir=config_dict["cookiecutters_dir"],
            checkout=None,
            no_input=False,
        )

        # templates from inherited cookiecutters
        templates_dir = Path(repo) / "templates"
        if templates_dir.is_dir():
            ancestors_templates.append(str(templates_dir))

        # generate project from inherited cookiecutter
        # overwriting files if necessary
        main.cookiecutter(
            repo,
            no_input=True,
            extra_context=public_keys,
            output_dir=str(Path(project_dir).parent),
            accept_hooks=True,
            overwrite_if_exists=True,
            skip_if_file_exists=False,
        )

    if ancestors_templates:
        context["cookiecutter"]["_ancestors_templates"] = ancestors_templates


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
