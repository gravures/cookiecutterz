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

# from cookiecutter.repository import is_zip_file
# from git import Repo
from cookiecutterz.creators import Multiton
from cookiecutterz.importer import monkey
from cookiecutterz.mapping import FilteredDictView, OrderableDict


if TYPE_CHECKING:
    from collections.abc import MutableMapping

    from cookiecutter.repository import determine_repo_dir
else:
    determine_repo_dir = monkey.target("cookiecutter.repository.determine_repo_dir")


class CircularInheritanceException(CookiecutterException):
    """Exception raised with circular reference in inheritance resolution."""

    def __str__(self) -> str:
        """Text representation of CircularInheritanceException."""
        return "Circular reference found in template inheritance resolution."


@final
class Url(Multiton, str, weakref=True):
    """Cookiecutter repository Url."""

    SCHEMES: ClassVar[set[str]] = {"file", "ssh", "git", "https", "http"}
    __slots__ = ("_path", "_scheme")

    def __new__(cls, value: str, abbreviations: dict[str, str] | None = None) -> Url:  # noqa: D102
        if abbreviations:
            value = cast(str, expand_abbreviations(value, abbreviations))
        return super().__new__(cls, value)

    @classmethod
    def __id__(cls, *args: Any, **_: Any) -> int:
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


@final
class Repo(Multiton, weakref=True):
    """Cookiecutter repository."""

    __slots__ = ("_checkout", "_directory", "_location", "_url", "_working_location")

    def __init__(self, *, url: Url, directory: str) -> None:
        self._url: Url = url
        self._directory: str = directory
        self._location: Path | None = None
        self._working_location: Path | None = None
        self._checkout: str | None = None

    @classmethod
    def __id__(cls, *_args: Any, **kwargs: Any) -> int:
        """Repo instances are id by their template name and directory.

        NOTE: this have the limation of not handling different
              templates resolving to the same name.
        """
        return hash((kwargs["url"].path.stem, kwargs["directory"]))

    def __hash__(self) -> int:
        return Repo.__id__(url=self.url, directory=self.directory)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Repo) and hash(self) == hash(other)

    @property
    def url(self) -> Url:
        """Url of this Repo."""
        return self.url

    @property
    def directory(self) -> str:
        """Directory within repo where cookiecutter.json lives."""
        return self._directory

    @property
    def checkout(self) -> str | None:
        """Branch, tag or commit ID checked out."""
        return self._checkout

    @property
    def location(self) -> Path:
        """The directory where this Repo was cloned.

        Returns: Path to the initial directory or to a tmp
                 directory if a pre_prompt_hook was called.

        Raises: RuntimeError if this Repo is not yet cloned.
        """
        if self._location is None:
            msg = f"{self!r} is not yet cloned, directory does not exists."
            raise RuntimeError(msg)
        return self._working_location or self._location

    def clone(
        self,
        *,
        location: Path,
        checkout: str | None,
        no_input: bool,
        password: str | None,
    ) -> tuple[str, bool]:
        """Clone this repository to directory.

        If the template refers to a repository URL, clone it.
        If the template is a path to a local repository, use it.
        """
        self._checkout = checkout
        _dir, cleanup = determine_repo_dir(
            template=self.url,
            abbreviations={},  # we already resolved abbreviations with Url()
            clone_to_dir=location,
            checkout=checkout,
            no_input=no_input,
            password=password,
            directory=self.directory,
        )
        _dir = cast(str, _dir)
        cleanup = cast(bool, cleanup)
        self._location = Path(_dir)
        return _dir, cleanup

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._url},{self._directory})"

    def __str__(self) -> str:
        return self.__fspath__()

    def __fspath__(self) -> str:
        return str(self.location)


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


class Template:
    """Cookiecutter Template composed with a cloned Repo and a Context."""

    __slots__ = ("_context", "_repo")

    def __init__(self, *, repo: Repo) -> None:
        self._repo: Repo = repo
        self._context: Context = Context.generate(directory=repo.location)

    @property
    def repo(self) -> Repo:
        """The repository associated to this template."""
        return self._repo

    @property
    def context(self) -> Context:
        """The Context attached to this Template."""
        return self._context


# class CruftState(Context):
#     """A class to represent the state of a Cruft project."""

#     FILE_NAME = ".cruft.json"

#     def __init__(self, last_commit: bytes | None = None, *args: Any, **kwargs: Any) -> None:
#         super().__init__(*args, **kwargs)
#         if last_commit and self.commit is None:
#             self.commit = last_commit
#         self["skipped"] = []

#     @property
#     def commit(self) -> bytes | None:
#         """The repo commit."""
#         return self.get("commit")

#     @commit.setter
#     def commit(self, value: bytes) -> None:
#         self["commit"] = value

#     def is_uptodate(self, repo: Repo, latest_commit: bytes) -> bool:
#         """Return False if the template needs an update.

#         If the latest commit exactly matches the current commit,
#         or if there have been no changes to the cookiecutter,
#         or if the strict flag is off, we allow for newer
#         commits to count as up to date.
#         """
#         return any(
#             latest_commit == self.commit,
#             not repo.index.diff(self.commit),
#             (
#                 repo.is_ancestor(repo.commit(latest_commit), repo.commit(current_commit))
#                 and not strict
#             ),
#         )
