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
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, cast, final

import jinja2
from cookiecutter import config, main, repository
from cookiecutter.exceptions import CookiecutterException

from cookiecutterz.collections import NewOrderedDict


if TYPE_CHECKING:
    import os
    from collections import OrderedDict


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

    @dataclass()
    class Template:
        """Template data."""

        repo: Path
        url: str | None
        cookiecutter: NewOrderedDict[str, Any]

    _instance: ClassVar[Master | None] = None
    _inspected: ClassVar[bool] = False
    _safe_guard: ClassVar[int]
    name: ClassVar[str]
    template: ClassVar[Master.Template]
    __TRO__: ClassVar[NewOrderedDict[str, Master.Template]] = NewOrderedDict()
    work_dir: ClassVar[Path]

    def __new__(cls, *, repo: Path | None = None, work_dir: Path | None = None) -> Master:  # noqa: D102
        if cls._instance is None:
            # code in this scope will execute once by cookiecutter session
            # at the pre_prompt stage
            if repo is None:
                raise TypeError
            cls._instance = super().__new__(cls)
            cls._safe_guard = 0
            cls.name = repo.stem
            cls.work_dir = work_dir or repo
            cls.template = Master.Template(url=None, repo=repo, cookiecutter=NewOrderedDict())
            cls._instance.prepare()
        return cls._instance

    @staticmethod
    def import_cookiecutter(repo: Path) -> NewOrderedDict[str, Any]:
        """Return cookiecutter.json content as a dictionary."""
        cc_json = repo / "cookiecutter.json"
        with cc_json.open("r") as stream:
            return NewOrderedDict(json.loads(stream.read()))

    @staticmethod
    def export_cookiercutter(repo: Path, cooikecutter: OrderedDict[str, Any]) -> None:
        """Export cookiecutter.json content from dictionary."""
        cc_json = repo / "cookiecutter.json"
        with cc_json.open("w") as stream:
            json.dump(cooikecutter, stream, indent=2)

    @classmethod
    def prepare(cls) -> None:
        """Inspect and prepare the master template.

        This function is executed as a pre_prompt hook for the master template.
        It will run after any real pre_prompt hook and before any prompts will
        be sent to the user.
        """
        if Master._inspected:
            return

        cls.template.cookiecutter = cls.import_cookiecutter(repo=cls.work_dir)
        if cls.template.cookiecutter.get("_bases"):
            cls.work_dir = (
                cls.work_dir
                if cls.work_dir != cls.template.repo
                else create_tmp_repo_dir(cls.template.repo)
            )
            cls.template.cookiecutter.setdefault("_copy_without_render", [])
            cls.template.cookiecutter.setdefault("__prompts__", {})

            cls.inspect_template(cls.template)

            # export merged cookiecutter mapping to json in place of original
            # cls.template.cookiecutter._debug()
            cls.export_cookiercutter(repo=cls.work_dir, cooikecutter=cls.template.cookiecutter)
            # print(f"\n{json.dumps(cls.template.cookiecutter, indent=2)}")
        Master._inspected = True

    @classmethod
    def inspect_template(cls, template: Template) -> None:
        """Inspect template and populate base templates."""
        if not (bases := cast(list[str], template.cookiecutter.get("_bases"))):
            return

        # template could have multiples inheritance
        for base_t in bases:
            name = cls.register(url=base_t)
            cc_master = cls.template.cookiecutter
            cc_base = cls.__TRO__[name].cookiecutter

            # recursively inspect bases template hierarchy
            cls.inspect_template(cls.__TRO__[name])

            # Assure proper Templates Resolution Order
            cls.__TRO__.move_to_end(name, last=True)

            # Forward input fields if not defined in master template
            _curr: str = cc_master.first
            for k, v in cls.get_public_keys(cc_base).items():
                # Assure bases keys are first
                # cc_master.setdefault(k, v)
                if k in cc_master:
                    _curr = k
                    continue
                cc_master.after(k, _curr, v)
                _curr = k
                # add prompt value if exists (order does not matter)
                if "__prompts__" in cc_base and k in cc_base["__prompts__"]:
                    cc_master["__prompts__"].setdefault(k, cc_base["__prompts__"][k])

            # Forwards _copy_without_render list from base templates using set operations
            cc_master["_copy_without_render"] = list(
                set(cc_master["_copy_without_render"]).union(
                    cc_base.get("_copy_without_render", [])
                )
            )

    @staticmethod
    def template_from_url(url: str) -> Template:
        """Return Template instance from remote/local url."""
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
        """Register a template as a base template..

        Avoid circular inheritance in a very restrictive way.
        We check against repo.stem because repo could be a tmp copy
        of a genuine repo (see: run_pre_prompt_hook()).
        """
        # NOTE: this implies the limation of forbid different template
        #       (eg: frm different authors and diifferent url) resolving
        #       to the same name
        tmpl = cls.template_from_url(url)
        name: str = tmpl.repo.stem
        if name == cls.name or (cls.__TRO__ and name in cls.__TRO__):
            raise CircularInheritanceException
        cls.__TRO__[name] = tmpl
        return name

    @staticmethod
    def get_public_keys(context: dict[str, Any]) -> dict[str, Any]:
        """Filter out private keys from a context."""
        return {k: v for k, v in context.items() if not k.startswith("_")}

    @staticmethod
    def load_inherited_jinja_templates(
        context: dict[str, Any], env: jinja2.Environment
    ) -> jinja2.Environment:
        """Load inherited jinja templates in jinja environment."""
        if jinja_base_templates := context.get("cookiecutter", {}).get(
            "_jinja_base_templates",
            [],
        ):
            env.loader = jinja2.FileSystemLoader([".", "../templates", *jinja_base_templates])
        return env

    def install_inherited_templates(self, project_dir: str, context: dict[str, Any]) -> None:
        """Install inherited cookiecutter templates.

        This function is call as a pre_gen_project hook and after
        any real pre_gen_project hook. It will be called for any template
        expansion, including base templates installation triggered by this
        function.
        """
        self.__class__._safe_guard += 1
        # Safe guard preventing recursive expansion of base template
        if self._safe_guard > 1 or not self.__TRO__:
            return

        # Get the user input from the master template provided by cookecutter
        # print(f"DEBUG INSTALL: {context}")
        cc_input: dict[str, Any] = context.get("cookiecutter", {})
        public_keys: dict[str, Any] = self.get_public_keys(cc_input)
        jinja_templates: list[str] = []

        # Expands base templates using our Template Resolution Order
        for base_t in self.__TRO__.values():
            # collect jinja templates from inherited cookiecutter
            templates_dir = base_t.repo / "templates"
            if templates_dir.is_dir():
                jinja_templates.append(str(templates_dir))

            # expands overwriting files if necessary
            main.cookiecutter(  # pyright: ignore[reportUnknownMemberType]
                template=str(base_t.repo),
                no_input=True,
                extra_context=public_keys,
                output_dir=str(Path(project_dir).parent),
                accept_hooks=True,
                overwrite_if_exists=True,
                skip_if_file_exists=False,
            )

        # Register base jina templates for final master expansion
        if jinja_templates:
            context["cookiecutter"]["_jinja_base_templates"] = jinja_templates
