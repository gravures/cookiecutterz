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
"""Environment module for Jinja2 templates."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, cast, final

from cookiecutter.environment import ExtensionLoaderMixin
from jinja2 import Environment, StrictUndefined

from cookiecutterz.creators import Multiton
from cookiecutterz.importer import loads_module
from cookiecutterz.main import LOG_LEVEL


if TYPE_CHECKING:
    from jinja2.ext import Extension

    from cookiecutterz.types import Context, Repo, Template

logger = logging.getLogger(f"cookiecutter.{__name__}")


@final
class SharedEnvironment(Multiton, ExtensionLoaderMixin, Environment, weakref=False):
    """Class replacement for cookiecutter.StrictEnvironment.

    SharedEnvironment are cached across a cookiecutter session.
    """

    _cached_extensions: ClassVar[dict[Repo, set[type[Extension]]]] = {}
    _global_template_dirs: ClassVar[set[str]] = set()

    def __init__(self, *, template: Template) -> None:
        self.repo: Repo = template.repo
        env_vars = template.context.cookiecutter.get("_jinja2_env_vars", {})
        super().__init__(  # pyright: ignore[reportUnknownMemberType]
            undefined=StrictUndefined,
            context=template.context,
            keep_trailing_newline=True,
            **env_vars,
        )

    @classmethod
    def __id__(cls, template: Template) -> int:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Return the repository ID."""
        return hash(template.repo)

    @classmethod
    def get(cls, repo: Repo) -> SharedEnvironment | None:
        """Return the environment for the given Repo."""
        return super()._get(hash(repo))

    def _read_extensions(self, context: Context) -> list[type[Extension]]:
        extensions = cast(list[str], super()._read_extensions(context))  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
        repo: Path = Path(context["cookiecutter"]["_repo_dir"])
        self._register(repo, extensions)
        return list(SharedEnvironment._cached_extensions[self.repo])

    def _register(self, repo: Path, extensions: list[str]) -> None:
        """Registers Jinja templates directory and extensions."""
        # register jinja template directory globally
        if (tmp := repo / "templates").is_dir():
            self._global_template_dirs.add(str(tmp))

        # register extensions for each template
        SharedEnvironment._cached_extensions[self.repo] = set()
        for ext in extensions:
            _p = ext.split(".")
            if (mod := loads_module(_p[0], repo)) and (_ext := getattr(mod, _p[-1], None)):
                SharedEnvironment._cached_extensions[self.repo].add(_ext)
        logger.log(
            LOG_LEVEL, "registered jinja extensions %s", SharedEnvironment._cached_extensions
        )
