# Copyright (c) 2023 - Gilles Coissac
# See end of file for extended copyright information
"""Extensions module for cookiecutter."""
from __future__ import annotations

import json
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


def save_local_replay(project_dir: str, context: dict) -> None:
    """Save a context for futur replay in the project directory."""
    replay = Path(project_dir) / ".cookiecutter.json"
    with replay.open("w") as f:
        json.dump(context.get("cookiecutter", {}), f)


def load_local_replay(project_dir: str) -> dict:
    """Load a local context for replay from the project directory."""
    if not (replay := Path(project_dir) / ".cookiecutter.json").is_file():
        raise FileNotFoundError(
            "No cookiecutter local replay found. Maybe you try"
            "to use cookiecutterz with a genuine cookiecutter project.",
        )
    with replay.open("r") as f:
        return json.load(f)


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


def remake(project_dir: str) -> None:
    """Generates the project from its local replay in a <.remake> sub directory."""
    replay_context = load_local_replay(project_dir)
    remake_dir: Path = Path(project_dir) / ".remake"
    remake_dir.mkdir(parents=True, exist_ok=True)
    _template = replay_context.get("_template")
    _cwd = replay_context.get("_cwd")

    if not repository.is_repo_url(_template):
        _template = f"{_cwd}/{_template}"

    # Setup the cookiecutter context
    context = get_public_keys(replay_context)

    # Generate a new project from the updated template
    main.cookiecutter(
        _template,
        extra_context=context,
        output_dir=str(remake_dir),
        accept_hooks=True,
        overwrite_if_exists=True,
        skip_if_file_exists=False,
    )


def update(project_dir: str) -> None:
    """Update the current managed cookiecutter template distribution."""
    remake(project_dir, tmp_dir)


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
