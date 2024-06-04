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
"""Types module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, NewType

from cookiecutter.exceptions import CookiecutterException


if TYPE_CHECKING:
    from pathlib import Path


class CircularInheritanceException(CookiecutterException):
    """Exception raised with circular reference in inheritance resolution."""

    def __str__(self) -> str:
        """Text representation of CircularInheritanceException."""
        return "Circular reference found in template inheritance resolution."


Context = NewType("Context", dict[str, Any])
Url = NewType("Url", str)


class RepoID:
    """RepoID allow to uniqly identify a repo directory.

    We check against template Path stem instead of plain Path
    because repo could be a temporary copy of the initial repo,
    (see: run_pre_prompt_hook()).

    NOTE: this have the limation of not handling different
          templates resolving to the same name.
    """

    __slots__ = ("_id",)

    def __init__(self, repo: Path) -> None:
        self._id: str = repo.stem

    def __str__(self) -> str:
        return self._id

    def __repr__(self) -> str:
        return f"RepoID({self._id})"

    def __hash__(self) -> int:
        return hash(self._id)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, RepoID) and self._id == other._id


class Unique:
    """Protocol for classes that are related to a repo."""

    __slots__ = ("_id",)

    def __init__(self, repo_id: RepoID) -> None:
        self._id = repo_id

    @property
    def repo_id(self) -> RepoID:
        """Returns the Unique RepoID attached to self."""
        return self._id

    @repo_id.setter
    def repo_id(self, value: RepoID) -> None:
        """Returns the Unique RepoID attached to self."""
        self._id = value
