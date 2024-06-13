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

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, cast, final
from urllib.parse import urlparse

from cookiecutter.exceptions import ContextDecodingException, CookiecutterException
from cookiecutter.generate import generate_context
from cookiecutter.repository import expand_abbreviations

from cookiecutterz.creators import Multiton

# from cookiecutter.repository import is_zip_file
# from git import Repo
from cookiecutterz.mapping import FilteredDictView, OrderableDict


if TYPE_CHECKING:
    from collections.abc import MutableMapping


class CircularInheritanceException(CookiecutterException):
    """Exception raised with circular reference in inheritance resolution."""

    def __str__(self) -> str:
        """Text representation of CircularInheritanceException."""
        return "Circular reference found in template inheritance resolution."


@final
class Url(Multiton, str):
    """Cookiecutter repository Url."""

    SCHEMES: ClassVar[set[str]] = {"file", "ssh", "git", "https", "http"}
    __slots__ = ("_path", "_scheme")

    def __new__(cls, value: str, abbreviations: dict[str, str] | None = None) -> Url:  # noqa: D102
        if abbreviations:
            value = cast(str, expand_abbreviations(value, abbreviations))
        return super().__new__(cls, value)

    @classmethod
    def __id__(cls, *args: Any, **_: Any) -> int:  # noqa: PLW3201
        return hash(args[0])

    def __init__(self, value: str, abbreviations: dict[str, str] | None = None) -> None:  # noqa: ARG002
        _u = urlparse(value, scheme="file")
        self._path: Path = Path(_u.path)

        if not _u.scheme:
            self._path = (Path(_u.netloc) / self._path).absolute()
        elif _u.scheme not in Url.SCHEMES:
            msg = f"Unsupported ulr scheme: {_u.scheme}"
            raise ValueError(msg)
        self._scheme: str = _u.scheme

    @property
    def path(self) -> Path:  # noqa: D102
        return self._path

    @property
    def scheme(self) -> str:  # noqa: D102
        return self._scheme

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self}')"


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


class Context(OrderableDict[str, Any]):
    """An Orderable Cookiecutter context mapping.

    There are two forms of serialized context in cookiecutter,
    the template definition file named 'cookiecutter.json'
    and those kinds of replay files which include the former
    filled with user inputs in a 'cookiecutter' key and
    an original unfilled version saved in a '_cookiecutter' key.

    A Context object have an unfilled 'cookiecutter' entry
    in first stage and becomes an in memory replay after user prompt.
    """

    FILE_NAME: ClassVar[str] = "cookiecutter.json"
    ENTRY_NAME: ClassVar[str] = "cookiecutter"

    def __init__(
        self, *args: Any, context: MutableMapping[str, Any] | None = None, **kwargs: Any
    ) -> None:
        if context:
            if self.validate(context):
                super().__init__(context)
            else:
                msg = "Invalid supplied mapping"
                raise ValueError(msg)
        else:
            super().__init__({Context.ENTRY_NAME: OrderableDict(*args, **kwargs)})

    @staticmethod
    def validate(context: MutableMapping[str, Any]) -> bool:
        """Check validity of a context.

        A valid context is a mapping with at least a main entry
        key who's value is itself another mapping. Also ensure this
        main entry is an OrderableDict.
        """
        main = context.get(Context.ENTRY_NAME)
        if main and not isinstance(main, OrderableDict):
            context[Context.ENTRY_NAME] = OrderableDict(main)
        return main is not None

    @property
    def cookiecutter(self) -> OrderableDict[str, Any]:
        """Return the main entry of this Context."""
        return self.get(self.__class__.ENTRY_NAME, OrderableDict())

    @property
    def public_keys(self) -> FilteredDictView[str, Any]:
        """Return a View of this Context main entry with only unmangled keys."""

        def _filter(k: str, _: Any) -> bool:
            return not k.startswith("_")

        return FilteredDictView(self.cookiecutter, _filter)

    @classmethod
    def load(cls, *, directory: Path, file_name: str | None = None) -> Context:
        """Loads a serialized Context (a 'replay') from disk."""
        if (path := (directory / (file_name or cls.FILE_NAME))).exists():
            with path.open("r") as stream:
                try:
                    context = json.load(stream, object_pairs_hook=OrderableDict)
                except ValueError as e:
                    json_exc_message = str(e)
                    our_exc_message = (
                        f"JSON decoding error while loading '{path}'. "
                        f"Decoding error details: '{json_exc_message}'"
                    )
                    raise ContextDecodingException(our_exc_message) from e
            return cls.__new__(cls, context)
        msg = f"{file_name or cls.FILE_NAME} not found in {directory}"
        raise FileNotFoundError(msg)

    def save(self, *, directory: Path, file_name: str | None = None) -> None:
        """Save a json string representation of this Context on disk."""
        with (directory / (file_name or self.__class__.FILE_NAME)).open("w") as stream:
            stream.write(self.dump() + "\n")

    @final
    @staticmethod
    def generate(
        *,
        directory: Path,
        default_context: dict[str, Any] | None = None,
        extra_context: dict[str, Any] | None = None,
    ) -> Context:
        """Generate a Context from a Cookiecutter template definition."""
        return Context(
            context=cast(
                dict[str, Any],
                generate_context(
                    context_file=str(directory / Context.FILE_NAME),
                    default_context=default_context,
                    extra_context=extra_context,
                ),
            )
        )

    @final
    def export(self, *, directory: Path, file_name: str | None = None) -> None:
        """Export this Context as a cookiecutter.json template definition."""
        entry = self.__class__.ENTRY_NAME
        main = self.get(f"_{entry}") or self.get(entry, {})
        with (directory / (file_name or Context.FILE_NAME)).open("w") as stream:
            json.dump(main, stream, indent=2)

    def dump(self) -> str:
        """Return a json representation of this Context."""
        return json.dumps(
            self,
            ensure_ascii=False,
            indent=2,
            separators=(",", ": "),
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.dump()})"

    def __str__(self) -> str:
        return self.dump()
