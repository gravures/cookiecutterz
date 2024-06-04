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
"""Extensions module implementing template inheritance."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, ClassVar, cast, final

from cookiecutter import config, main, repository
from cookiecutter.utils import work_in
from jinja2 import FileSystemLoader

from cookiecutterz.helpers import create_tmp_repo_dir
from cookiecutterz.jenvironment import SharedEnvironment
from cookiecutterz.main import LOG_LEVEL
from cookiecutterz.mapping import OrderableDict
from cookiecutterz.types import CircularInheritanceException, Context, RepoID, Unique, Url


logger = logging.getLogger(f"cookiecutter.{__name__}")


# TODO: handle the complete set of options to expand
#       a cookiecutter template (eg: directory, ...)


def _log_context(context: dict[str, Any]) -> None:
    logger.log(LOG_LEVEL, "\n%s", json.dumps(context, indent=2))


class Template(Unique):
    """Template data."""

    __slots__ = ("_cc", "_id", "_repo", "_url")

    def __init__(self, *, repo: Path, url: Url | None = None) -> None:
        self._repo: Path = repo
        self._url: Url = url or Url("Undefined")
        self._cc: OrderableDict[str, Any] = OrderableDict()
        super().__init__(RepoID(self._repo))

    @property
    def repo(self) -> Path:  # noqa: D102
        return self._repo

    @repo.setter
    def repo(self, value: Path) -> None:
        self._repo = value
        if RepoID(self._repo) != self.repo_id:
            msg = f"new value {value} does not meet actual template name {value.stem}"
            raise ValueError(msg)

    @property
    def url(self) -> Url:  # noqa: D102
        return self._url

    @property
    def cookiecutter(self) -> OrderableDict[str, Any]:  # noqa: D102
        return self._cc

    def import_cookiecutter(self) -> None:
        """Return cookiecutter.json content as a dictionary."""
        cc_json = self._repo / "cookiecutter.json"
        with cc_json.open("r") as stream:
            self._cc = OrderableDict(json.loads(stream.read()))

    def export_cookiercutter(self) -> None:
        """Export cookiecutter.json content from dictionary."""
        cc_json = self._repo / "cookiecutter.json"
        with cc_json.open("w") as stream:
            json.dump(self._cc, stream, indent=2)

    @staticmethod
    def from_url(url: Url) -> Template:
        """Return Template instance from remote/local url."""
        user_config: dict[str, Any] = config.get_user_config()  # pyright: ignore [reportUnknownMemberType]
        # clone the template from url locally
        # or use it if it's already a cloned directory
        repo, _ = repository.determine_repo_dir(  # pyright: ignore[reportUnknownMemberType]
            template=url,
            abbreviations=user_config["abbreviations"],
            clone_to_dir=user_config["cookiecutters_dir"],
            checkout=None,
            no_input=True,
        )
        repo = Path(cast(str, repo))
        _t = Template(repo=repo, url=url)
        _t.import_cookiecutter()
        return _t


@final
class Master:
    """Master Template singleton class."""

    _instance: ClassVar[Master | None] = None
    _init: ClassVar[bool] = False

    __slots__ = (
        "__tro__",
        "_bases_installed",
        "_cloned",
        "_inspected",
        "current",
        "cwd",
        "stage",
        "template",
    )

    def __new__(cls, *, repo: Path | None = None, work_dir: Path | None = None) -> Master:  # noqa: D102, ARG003
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *, repo: Path | None = None, work_dir: Path | None = None) -> None:
        if Master._init:
            return

        if repo is None:
            msg = "First call to Master() should supply a repo parameter"
            raise ValueError(msg)

        self._bases_installed: bool = False
        self._inspected: bool = False
        self.__tro__: OrderableDict[RepoID, Template] = OrderableDict()
        self._cloned: bool = bool(work_dir and work_dir != repo)
        self.cwd: Path = Path.cwd()
        self.template = Template(repo=work_dir or repo)
        self.current: RepoID = self.template.repo_id
        self.stage: str = "init"

        Master._init = True
        self._prepare()

    def get_current_template(self) -> Template:
        """Return current template."""
        return (
            self.template if self.current == self.template.repo_id else self.__tro__[self.current]
        )

    def _prepare(self) -> None:  # sourcery skip: extract-method
        """Inspect and prepare the master template.

        This function is executed as a pre_prompt hook for the master template.
        It will run after any real pre_prompt hook and before any prompts will
        be sent to the user.
        """
        if self._inspected:
            return

        self.template.import_cookiecutter()
        if self.template.cookiecutter.get("_bases"):
            self.template.repo = (
                self.template.repo if self._cloned else create_tmp_repo_dir(self.template.repo)
            )
            self.template.cookiecutter.setdefault("_copy_without_render", [])
            self.template.cookiecutter.setdefault("__prompts__", {})
            self._inspect_template(self.template)

            # export merged cookiecutter mapping to json in place of original
            self.template.export_cookiercutter()
            _log_context(self.template.cookiecutter)

        self._inspected = True
        self.stage = "inspected"

    def _inspect_template(self, template: Template) -> None:
        """Inspect template and populate base templates."""
        if not (bases := cast(list[Url], template.cookiecutter.get("_bases"))):
            return

        # template could have multiples inheritance
        for base_t in bases:
            base = self._register_template(url=base_t)
            cc_master = self.template.cookiecutter
            cc_base = base.cookiecutter

            # recursively inspect bases template hierarchy
            self._inspect_template(base)

            # Assure proper Templates Resolution Order
            self.__tro__.move_to_end(base.repo_id, last=True)

            # Forward input fields if not defined in master template
            _curr: str = cc_master.first
            for k, v in self.get_public_keys(Context(cc_base)).items():
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

    def _register_template(self, url: Url) -> Template:
        """Register a template as a base template..

        Avoid circular inheritance in a very restrictive way.
        """
        tmpl = Template.from_url(url)
        if tmpl.repo_id == self.template.repo_id or (
            self.__tro__ and tmpl.repo_id in self.__tro__
        ):
            raise CircularInheritanceException
        self.__tro__[tmpl.repo_id] = tmpl
        return tmpl

    def update_jinja_environment(self) -> None:
        """Update the jinja environment with inherited extensions and templates."""
        m_env = SharedEnvironment._cached_environments[self.template.repo_id]
        for _id, exts in SharedEnvironment._cached_extensions.items():
            if _id != self.template.repo_id:
                for e in exts:
                    m_env.add_extension(e)
        if SharedEnvironment._global_template_dirs:
            m_env.loader = FileSystemLoader([
                ".",
                "../templates",
                *SharedEnvironment._global_template_dirs,
            ])

        logger.log(
            LOG_LEVEL,
            "<%s>: Updating the jinja environment(%s) with %s and %s",
            self.stage,
            m_env.repo_id,
            SharedEnvironment._cached_extensions,
            SharedEnvironment._global_template_dirs,
        )

    @staticmethod
    def get_public_keys(context: Context) -> Context:
        """Filter out private keys from a context."""
        return Context({k: v for k, v in context.items() if not k.startswith("_")})

    def install_bases(self, project_dir: str, context: Context) -> None:
        """Install inherited cookiecutter templates.

        This function is call as the pre_gen_project hook stage ut after
        any real pre_gen_project hook. It will be called for any template
        expansion, including base templates installation triggered by this
        function.
        """
        self.stage = "install"

        if self.current == self.template.repo_id:
            logger.log(LOG_LEVEL, "will %s template %s", self.stage, self.current)

        # Safe guard preventing recursive expansion of base template
        if (not self.__tro__) or self.current != self.template.repo_id:
            return

        # Get the user input from the master template provided by cookiecutter
        # logger.log(LOG_LEVEL, "DEBUG INSTALL: %s", context)
        cc_input: Context = context.get("cookiecutter", {})
        public_keys: Context = self.get_public_keys(cc_input)

        # Expands base templates using our Template Resolution Order
        for base_t in self.__tro__.values():
            # expands overwriting files if necessary
            self.current = base_t.repo_id
            logger.log(LOG_LEVEL, "will %s base template %s", self.stage, self.current)

            with work_in(self.cwd):
                main.cookiecutter(  # pyright: ignore[reportUnknownMemberType]
                    template=str(base_t.repo),
                    no_input=True,
                    extra_context=public_keys,
                    output_dir=str(Path(project_dir).parent),
                    accept_hooks=True,
                    overwrite_if_exists=True,
                    skip_if_file_exists=False,
                )
        self._bases_installed = True
        self.update_jinja_environment()
