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
"""Extensions module implementing template inheritance."""

from __future__ import annotations

import json
import logging
import shutil
import sys
import tempfile
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, NewType, cast, final

from cookiecutter import config, main, repository
from cookiecutter.exceptions import CookiecutterException, UnknownExtension
from cookiecutter.utils import work_in
from jinja2 import Environment, StrictUndefined

from cookiecutterz.ecollections import NewOrderedDict


if TYPE_CHECKING:
    import os
    from types import ModuleType

    from jinja2.ext import Extension


logger = logging.getLogger("cookiecutter.inheritance")
LOG_LEVEL = logging.INFO


# TODO: report a bug to cooikecutter team
#       copy hidden dir like .venv and fails
def create_tmp_repo_dir(repo_dir: os.PathLike[str]) -> Path:
    """Create a temporary dir with a copy of the contents of repo_dir."""
    repo_dir = Path(repo_dir).resolve()
    base_dir = tempfile.mkdtemp(prefix="cookiecutter")
    new_dir = f"{base_dir}/{repo_dir.name}"
    logger.log(LOG_LEVEL, "Copying repo_dir from %s to %s", repo_dir, new_dir)
    shutil.copytree(
        repo_dir,
        new_dir,
        ignore=shutil.ignore_patterns(
            ".git",
            "__pycache__",
            "*.pyc",
            "venv",
            ".venv",
        ),
    )
    return Path(new_dir)


def loads_module(name: str, where: Path) -> ModuleType | None:
    """Loads a python module or package from the Path where."""
    source = where / name
    source = source / "__init__.py" if source.is_dir() else source.with_suffix(".py")

    logger.log(LOG_LEVEL, "loading module '%s' from '%s'", name, source)
    spec = spec_from_file_location(name=name, location=source)
    if spec is not None and (module := module_from_spec(spec)) and spec.loader:
        try:
            sys.modules[name] = module
            spec.loader.exec_module(module)
        except FileNotFoundError:
            return None
        return module
    return None


class CircularInheritanceException(CookiecutterException):
    """Exception raised with circular reference in inheritance resolution."""

    def __str__(self) -> str:
        """Text representation of CircularInheritanceException."""
        return "Circular reference found in template inheritance resolution."


class SharedEnvironment(Environment):
    """Class replacement for cookiecutter.StrictEnvironment."""

    _inits: ClassVar[set[int]] = set()

    def __new__(cls, *args: Any, **kwargs: Any) -> SharedEnvironment:  # noqa: PYI034, ARG003
        """SharedEnvironment are cached across cookiecutter session."""
        master = Master()
        if env := master._cached_jinja_environments.get(master.current):
            return env
        return super().__new__(cls)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if id(self) not in SharedEnvironment._inits:
            extensions: list[str | type[Extension]] = [
                "cookiecutter.extensions.JsonifyExtension",
                "cookiecutter.extensions.RandomStringExtension",
                "cookiecutter.extensions.SlugifyExtension",
                "cookiecutter.extensions.TimeExtension",
                "cookiecutter.extensions.UUIDExtension",
            ]
            master = Master()
            if m_ext := master.jinja_extensions.get(master.current):
                extensions.extend(m_ext)

            try:
                super().__init__(*args, extensions=extensions, undefined=StrictUndefined, **kwargs)
            except ImportError as err:
                msg = f"Unable to load extension: {err}"
                raise UnknownExtension(msg) from err
            else:
                SharedEnvironment._inits.add(id(self))
                master._cached_jinja_environments[master.current] = self


TName = NewType("TName", str)


class Template:
    """Template data."""

    __slots__ = ("_cc", "_name", "_repo", "_url")

    def __init__(self, *, repo: Path) -> None:
        self._repo: Path = repo
        self._name: TName = TName(repo.stem)
        self._url: str | None = None
        self._cc: NewOrderedDict[str, Any] = NewOrderedDict()

    @property
    def name(self) -> TName:  # noqa: D102
        return self._name

    @property
    def repo(self) -> Path:  # noqa: D102
        return self._repo

    @repo.setter
    def repo(self, value: Path) -> None:
        if value.stem != self._name:
            msg = f"value {value} does not fit template name {self._name}"
            raise ValueError(msg)
        self._repo = value

    @property
    def url(self) -> str | None:  # noqa: D102
        return self._url

    @property
    def cookiecutter(self) -> NewOrderedDict[str, Any]:  # noqa: D102
        return self._cc

    def import_cookiecutter(self) -> None:
        """Return cookiecutter.json content as a dictionary."""
        cc_json = self._repo / "cookiecutter.json"
        with cc_json.open("r") as stream:
            self._cc = NewOrderedDict(json.loads(stream.read()))

    def export_cookiercutter(self) -> None:
        """Export cookiecutter.json content from dictionary."""
        cc_json = self._repo / "cookiecutter.json"
        with cc_json.open("w") as stream:
            json.dump(self._cc, stream, indent=2)

    @staticmethod
    def from_url(url: str) -> Template:
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
        repo = Path(cast(str, repo))
        _t = Template(repo=repo)
        _t.import_cookiecutter()
        _t._url = url
        return _t


@final
class Master:
    """Singleton Template Master class."""

    _instance: ClassVar[Master | None] = None
    _init: ClassVar[bool] = False

    __slots__ = (
        "__tro__",
        "_bases_installed",
        "_cached_jinja_environments",
        "_inspected",
        "_tmp_repo",
        "current",
        "cwd",
        "jinja_extensions",
        "jinja_templates",
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
        self._tmp_repo: bool = work_dir != repo

        self.template = Template(repo=work_dir or repo)
        self.stage: str = "init"
        self.current: TName = TName("")
        self.cwd: Path = Path.cwd()

        self.__tro__: NewOrderedDict[TName, Template] = NewOrderedDict()
        self.jinja_templates: set[str] = set()
        self.jinja_extensions: dict[TName, set[type[Extension]]] = {}
        self._cached_jinja_environments: dict[TName, SharedEnvironment] = {}

        Master._init = True
        self._prepare()

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
                self.template.repo if self._tmp_repo else create_tmp_repo_dir(self.template.repo)
            )
            self.template.cookiecutter.setdefault("_copy_without_render", [])
            self.template.cookiecutter.setdefault("__prompts__", {})
            self.register_jinja_extensions(self.template)
            self.inspect_template(self.template)

            # export merged cookiecutter mapping to json in place of original
            self.template.export_cookiercutter()
            logger.log(LOG_LEVEL, "\n%s", json.dumps(self.template.cookiecutter, indent=2))

        self._inspected = True
        self.stage = "inspected"
        self.current = self.template.name

    def inspect_template(self, template: Template) -> None:
        """Inspect template and populate base templates."""
        if not (bases := cast(list[str], template.cookiecutter.get("_bases"))):
            return

        # template could have multiples inheritance
        for base_t in bases:
            base = self.register_template(url=base_t)
            cc_master = self.template.cookiecutter
            cc_base = base.cookiecutter

            # recursively inspect bases template hierarchy
            self.inspect_template(base)

            # Assure proper Templates Resolution Order
            self.__tro__.move_to_end(base.name, last=True)

            # Forward input fields if not defined in master template
            _curr: str = cc_master.first
            for k, v in self.get_public_keys(cc_base).items():
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

            # Register jinja environment
            self.register_jinja_extensions(base)

    def register_jinja_extensions(self, template: Template) -> None:
        """Registers Jinja templates directory and extensions."""
        # templates
        if (tmp := template.repo / "templates").is_dir():
            self.jinja_templates.add(str(tmp))

        # extensions
        self.jinja_extensions[template.name] = set()
        for ext in template.cookiecutter.get("_extensions", []):
            _p = ext.split(".")
            if (mod := loads_module(_p[0], template.repo)) and (
                _ext := getattr(mod, _p[-1], None)
            ):
                self.jinja_extensions[template.name].add(_ext)
        logger.log(LOG_LEVEL, "registering jinja extensions %s", self.jinja_extensions)

    def register_template(self, url: str) -> Template:
        """Register a template as a base template..

        Avoid circular inheritance in a very restrictive way.
        We check against template name instead of template repo
        because repo could be a tmp copy of a genuine repo
        (see: run_pre_prompt_hook()).
        """
        # NOTE: this implies the limation of forbid different template
        #       (eg: frm different authors and diifferent url) resolving
        #       to the same name
        tmpl = Template.from_url(url)
        if tmpl.name == self.template.name or (self.__tro__ and tmpl.name in self.__tro__):
            raise CircularInheritanceException
        self.__tro__[tmpl.name] = tmpl
        return tmpl

    @staticmethod
    def get_public_keys(context: dict[str, Any]) -> dict[str, Any]:
        """Filter out private keys from a context."""
        return {k: v for k, v in context.items() if not k.startswith("_")}

    def update_jinja_environment(self, env: Environment, context: dict[str, Any]) -> Environment:  # noqa: ARG002
        """Update the jinja environment with necessary inherited properties."""
        if env is self._cached_jinja_environments[self.template.name]:
            for n, exts in self.jinja_extensions.items():
                if n != self.template.name:
                    for e in exts:
                        env.add_extension(e)
            logger.log(
                LOG_LEVEL,
                "<%s>: Updating the jinja environment (%s) with %s and %s",
                self.stage,
                id(env),
                self.jinja_extensions,
                self.jinja_templates,
            )
        return env

    def install_inherited_templates(self, project_dir: str, context: dict[str, Any]) -> None:
        """Install inherited cookiecutter templates.

        This function is call as the pre_gen_project hook stage ut after
        any real pre_gen_project hook. It will be called for any template
        expansion, including base templates installation triggered by this
        function.
        """
        self.stage = "install"

        if self.current == self.template.name:
            logger.log(LOG_LEVEL, "will %s template %s", self.stage, self.current)

        # Safe guard preventing recursive expansion of base template
        if (not self.__tro__) or self.current != self.template.name:
            return

        # Get the user input from the master template provided by cookiecutter
        # logger.log(LOG_LEVEL, "DEBUG INSTALL: %s", context)
        cc_input: dict[str, Any] = context.get("cookiecutter", {})
        public_keys: dict[str, Any] = self.get_public_keys(cc_input)

        # Expands base templates using our Template Resolution Order
        for base_t in self.__tro__.values():
            # expands overwriting files if necessary
            self.current = base_t.name
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
