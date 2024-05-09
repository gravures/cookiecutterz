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
"""Extensions module for cookiecutter."""

from __future__ import annotations

import json
import shutil
import tempfile
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint
from typing import TYPE_CHECKING, Any, ClassVar, cast, final

import jinja2
from cookiecutter import config, main, repository
from cookiecutter.exceptions import CookiecutterException


if TYPE_CHECKING:
    import os


# TODO: report a bug to cooikecutter team
#       copy hidden dir like .venv and fails
def create_tmp_repo_dir(repo_dir: os.PathLike[str]) -> Path:
    """Create a temporary dir with a copy of the contents of repo_dir."""
    repo_dir = Path(repo_dir).resolve()
    base_dir = tempfile.mkdtemp(prefix="cookiecutter")
    new_dir = f"{base_dir}/{repo_dir.name}"
    # logger.debug(f"Copying repo_dir from {repo_dir} to {new_dir}")
    shutil.copytree(
        repo_dir,
        new_dir,
        ignore=shutil.ignore_patterns(
            ".git", "__pycache__", "*.pyc", "venv", ".venv", "pyproject.toml"
        ),
    )
    return Path(new_dir)


class CircularInheritanceException(CookiecutterException):
    """Exception raised with circular reference in inheritance resolution."""

    def __str__(self) -> str:
        """Text representation of CircularInheritanceException."""
        return "Circular reference found in template inheritance resolution."


@final
class Master:
    """Singleton Template Master class."""

    @dataclass(slots=True, kw_only=True)
    class Template:
        """Template data."""

        repo: Path
        url: str | None
        cookiecutter: dict[str, Any]

    _instance: ClassVar[Master | None] = None
    _inspected: ClassVar[bool] = False
    name: ClassVar[str]
    template: ClassVar[Master.Template]
    ancestors: ClassVar[OrderedDict[str, Master.Template]] = OrderedDict()
    work_dir: ClassVar[Path]

    def __new__(cls, *, repo: Path | None = None, work_dir: Path | None = None) -> Master:  # noqa: D102
        if cls._instance is None:
            if repo is None:
                raise TypeError
            cls._instance = super().__new__(cls)
            cls.name = repo.stem
            cls.work_dir = work_dir or repo
            cls.template = Master.Template(url=None, repo=repo, cookiecutter={})
            cls._instance._inspect()
        return cls._instance

    @staticmethod
    def import_cookiecutter(repo: Path) -> dict[str, Any]:
        """Return cookiecutter.json content as a dictionary."""
        cc_json = repo / "cookiecutter.json"
        with cc_json.open("r") as stream:
            return json.loads(stream.read())

    @staticmethod
    def export_cookiercutter(repo: Path, cooikecutter: dict[str, Any]) -> None:
        """Export cookiecutter.json content from dictionary."""
        cc_json = repo / "cookiecutter.json"
        with cc_json.open("w") as stream:
            json.dump(cooikecutter, stream, indent=2)

    @classmethod
    def _inspect(cls) -> None:
        if Master._inspected:
            return

        cls.template.cookiecutter = cls.import_cookiecutter(repo=cls.work_dir)

        # TODO: should be recursive through the hierarchy
        #       here we only go one level deep in inheritance
        if extends := cls.template.cookiecutter.get("_extends"):
            cc_master = cls.template.cookiecutter
            if cls.work_dir == cls.template.repo:
                cls.work_dir = create_tmp_repo_dir(cls.template.repo)
                print(f"DEBUG: {cls.work_dir}")

            if not cc_master.get("__prompts__"):
                cc_master["__prompts__"] = {}
            if not cc_master.get("_copy_without_render"):
                cc_master["_copy_without_render"] = []

            # template could have multiples inheritance
            for ancestor in extends:
                name = cls.register(url=ancestor)
                cc_ancestor = cls.ancestors[name].cookiecutter

                # template dont have to overload input field of ancestors.
                # forward them if not defined in master template
                for k, v in get_public_keys(cc_ancestor).items():
                    if k not in cc_master:
                        cls.template.cookiecutter[k] = v
                        if cc_ancestor.get("__prompts__", {}).get(k):
                            cc_master["__prompts__"][k] = cc_ancestor["__prompts__"][k]

                # forwards _copy_without_render dict from ancestors.
                for v in cc_ancestor.get("_copy_without_render", []):
                    if v not in cc_master["_copy_without_render"]:
                        cc_master["_copy_without_render"].append(v)  # pyright: ignore [reportUnknownMemberType]

            # export merged cookiecutter mapping to json in place of original
            cls.export_cookiercutter(repo=cls.work_dir, cooikecutter=cls.template.cookiecutter)
        Master._inspected = True

    @staticmethod
    def _template_from_url(url: str) -> Template:
        user_config: dict[str, Any] = config.get_user_config()  # pyright: ignore [reportUnknownMemberType]
        # clone the inherited template locally
        # or use it if it's already a directory
        repo, _ = repository.determine_repo_dir(  # pyright: ignore[reportUnknownMemberType]
            template=url,
            abbreviations=user_config["abbreviations"],
            clone_to_dir=user_config["cookiecutters_dir"],
            checkout=None,
            no_input=True,
        )
        repo = cast(str, repo)
        cc = Master.import_cookiecutter(Path(repo))
        return Master.Template(url=url, repo=Path(repo), cookiecutter=cc)

    @classmethod
    def register(cls, url: str) -> str:
        """Register a template as ancestor.

        Avoid circular inheritance in a very restrictive way.
        We check against repo.stem because repo could be a tmp copy
        of a genuine repo (see: run_pre_prompt_hook()).
        """
        tmpl = cls._template_from_url(url)
        name: str = tmpl.repo.stem
        if name == cls.name or (cls.ancestors and name in cls.ancestors):
            raise CircularInheritanceException
        cls.ancestors[name] = tmpl
        return name

    @classmethod
    def update(cls, name: str, key: str, value: Any) -> None:
        """Update a value of a registered template."""
        if key == "repo" and Path(value).stem != name:
            raise TypeError
        setattr(cls.ancestors[name], key, value)


def get_public_keys(context: dict[str, Any]) -> dict[str, Any]:
    """Filter out private keys from a context."""
    return {k: v for k, v in context.items() if not k.startswith("_")}


def load_inherited_jinja_templates(
    context: dict[str, Any], env: jinja2.Environment
) -> jinja2.Environment:
    """Load inherited jinja templates in jinja environment."""
    if ancestors_templates := context.get("cookiecutter", {}).get(
        "_ancestors_templates",
        [],
    ):
        env.loader = jinja2.FileSystemLoader([".", "../templates", *ancestors_templates])
    return env


def install_inherited_templates(project_dir: str, context: dict[str, Any]) -> None:
    """Install inherited cookiecutter templates."""
    master: Master = Master()
    if not master.ancestors:
        return

    pprint(f"DEBUG INSTALL: {context}")
    # public_keys: dict[str, Any] = get_public_keys(master.template.cookiecutter)

    jinja_templates: list[str] = []
    for ancestor in master.ancestors.values():
        # jinja templates from inherited cookiecutter
        templates_dir = ancestor.repo / "templates"
        if templates_dir.is_dir():
            jinja_templates.append(str(templates_dir))

        # generate project from inherited cookiecutter
        # overwriting files if necessary
        main.cookiecutter(  # pyright: ignore[reportUnknownMemberType]
            template=ancestor.repo,
            no_input=True,
            # extra_context=public_keys,
            output_dir=str(Path(project_dir).parent),
            accept_hooks=True,
            overwrite_if_exists=True,
            skip_if_file_exists=False,
        )

    if jinja_templates:
        context["cookiecutter"]["_ancestors_templates"] = jinja_templates
