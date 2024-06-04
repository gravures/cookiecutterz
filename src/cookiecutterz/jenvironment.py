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
from typing import TYPE_CHECKING, Any, ClassVar, cast, final

from cookiecutter.environment import ExtensionLoaderMixin
from jinja2 import Environment, StrictUndefined

from cookiecutterz.helpers import loads_module
from cookiecutterz.main import LOG_LEVEL
from cookiecutterz.types import Context, RepoID, Unique


if TYPE_CHECKING:
    from jinja2.ext import Extension

logger = logging.getLogger(f"cookiecutter.{__name__}")


@final
class SharedEnvironment(Unique, ExtensionLoaderMixin, Environment):
    """Class replacement for cookiecutter.StrictEnvironment."""

    _cached_environments: ClassVar[dict[RepoID, SharedEnvironment]] = {}
    _cached_extensions: ClassVar[dict[RepoID, set[type[Extension]]]] = {}
    _global_template_dirs: ClassVar[set[str]] = set()
    _tmp_id: ClassVar[RepoID | None] = None

    def __new__(cls, **kwargs: Any) -> SharedEnvironment:
        """SharedEnvironment are cached across cookiecutter session."""
        if not (context := kwargs.get("context")):
            msg = "Missing context named argument"
            raise ValueError(msg)

        _id = RepoID(Path(context["cookiecutter"]["_repo_dir"]))
        if env := cls._cached_environments.get(_id):
            return env
        cls._tmp_id = _id
        return super().__new__(cls)

    def __init__(self, **kwargs: Any) -> None:
        if SharedEnvironment._tmp_id:
            Unique.__init__(self, SharedEnvironment._tmp_id)
            ExtensionLoaderMixin.__init__(self, undefined=StrictUndefined, **kwargs)  # pyright: ignore[reportUnknownMemberType]
            SharedEnvironment._cached_environments[self.repo_id] = self
            SharedEnvironment._tmp_id = None

    def _read_extensions(self, context: Context) -> list[type[Extension]]:
        extensions = cast(list[str], super()._read_extensions(context))  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
        repo: Path = Path(context["cookiecutter"]["_repo_dir"])
        self._register(repo, extensions)
        return list(SharedEnvironment._cached_extensions[self.repo_id])

    def _register(self, repo: Path, extensions: list[str]) -> None:
        """Registers Jinja templates directory and extensions."""
        # register jinja template directory globally
        if (tmp := repo / "templates").is_dir():
            self._global_template_dirs.add(str(tmp))

        # register extensions for each template
        SharedEnvironment._cached_extensions[self.repo_id] = set()
        for ext in extensions:
            _p = ext.split(".")
            if (mod := loads_module(_p[0], repo)) and (_ext := getattr(mod, _p[-1], None)):
                SharedEnvironment._cached_extensions[self.repo_id].add(_ext)
        logger.log(
            LOG_LEVEL, "registered jinja extensions %s", SharedEnvironment._cached_extensions
        )
