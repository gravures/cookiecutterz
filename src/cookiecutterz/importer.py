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
"""Importer module."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import logging
import sys
from typing import TYPE_CHECKING, Any, Callable, ClassVar, final

from cookiecutterz.main import LOG_LEVEL


if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType


logger = logging.getLogger(f"cookiecutter.{__name__}")


def uncache(*excludes: str) -> None:
    """Remove package modules from cache except excluded ones.

    On next import they will be reloaded.
    """
    pkgs: list[str] = []
    for mod in excludes:
        pkg = mod.split(".", 1)[0]
        pkgs.append(pkg)

    to_uncache: list[str] = []
    for mod in sys.modules:
        if mod in excludes:
            continue
        if mod in pkgs:
            to_uncache.append(mod)
            continue
        for pkg in pkgs:
            if mod.startswith(f"{pkg}."):
                to_uncache.append(mod)
                break
    for mod in to_uncache:
        del sys.modules[mod]


class Module:
    """Utility class for dynamic loading of python module."""

    __slots__ = ("_is_pkg", "_name", "_pkg", "_spec")

    def __init__(self, name: str, *, package: str = "", where: Path | None = None) -> None:
        abs_name = importlib.util.resolve_name(name, package)

        self._spec: importlib.machinery.ModuleSpec = self._find_spec(abs_name, where)
        self._is_pkg: bool = self._spec.submodule_search_locations is not None
        self._pkg, _, self._name = abs_name.rpartition(".")

    @staticmethod
    def _find_spec(name: str, where: Path | None) -> importlib.machinery.ModuleSpec:
        if where is None:
            spec = importlib.util.find_spec(name=name)
        else:
            loader_details = [
                (importlib.machinery.SourceFileLoader, importlib.machinery.SOURCE_SUFFIXES),
                (importlib.machinery.SourcelessFileLoader, importlib.machinery.BYTECODE_SUFFIXES),
                (importlib.machinery.ExtensionFileLoader, importlib.machinery.EXTENSION_SUFFIXES),
            ]
            finder = importlib.machinery.FileFinder(str(where), *loader_details)
            spec = finder.find_spec(name)
            logger.log(LOG_LEVEL, "loading module '%s' from '%s'", name, where)

        if not spec:
            raise ModuleNotFoundError
        return spec

    def load(self) -> None:
        """Loads this module if not already loaded.

        Raises ModuleNotFoundError: if module.name cannot be found.
        Raises ImportError: if loading goes wrong.
        """
        if self.module:
            return
        if (module := importlib.util.module_from_spec(self._spec)) and self._spec.loader:
            try:
                sys.modules[str(self)] = module
                self._spec.loader.exec_module(module)
                if self._spec.parent:
                    setattr(sys.modules[self._spec.parent], self._name, module)
            except FileNotFoundError as e:
                raise ModuleNotFoundError from e
        raise ImportError

    @property
    def pkg(self) -> str:
        """Returns the package name this module belongs to."""
        return self._pkg

    @property
    def root(self) -> str:
        """Returns the top package name this module belongs to."""
        return self._pkg.split(".")[0]

    @property
    def name(self) -> str:
        """Returns the name of this module without any prefixes."""
        return self._name

    @property
    def module(self) -> ModuleType | None:
        """Return the actual Module if loaded or None otherwise."""
        return sys.modules.get(str(self), None)

    @property
    def is_package(self) -> bool:
        """Returns True if this module is also a package."""
        return self._is_pkg

    def prefix_of(self, other: str) -> bool:
        """Returns True if self is a package and is a prefix of other name."""
        prefix = f"{self!s}."
        return other != prefix and other.startswith(prefix) if self._is_pkg else False

    def share_root(self, other: str) -> bool:
        """Returns True if self and other name have a common root prefix that is not ''."""
        return other.split(".")[0] == self.root if self.root else False

    def __str__(self) -> str:
        return f"{self.pkg}.{self.name}" if self.pkg else self.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self!s})"

    def __hash__(self) -> int:
        return hash((self.pkg, self.name))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and hash(other) == hash(self)


_NULL: type[None] = type(None)  # an undefined value that is not None
Patchable = Any
Patch = Callable[..., Any]


@final
class monkey:  # noqa: N801
    """Monkey patcher decorator.

    Patch the target attribute of module with decorated function.
    """

    _protected: ClassVar[set[str]] = {"sys", "builtins", "importlib", "importlib.util", "__main__"}
    _to_reload: ClassVar[set[str]] = set()
    _patches: ClassVar[dict[str, monkey]] = {}

    __slots__ = ("_module", "_origin", "_patch", "_target")

    def __init__(self, *, module: str, target: str):
        self._module: Module = Module(module)
        self._target: str = target
        self._patch: Patch = monkey._null_patch
        self._origin: Patchable = _NULL
        monkey._patches[str(self)] = self

    @staticmethod
    def _null_patch(*_a: Any, **_k: Any) -> Any:
        raise NotImplementedError

    def _apply(self) -> None:
        """Substitute target with patch."""
        self._module.load()
        self._origin = getattr(self._module.module, self._target)
        setattr(self._module.module, self._target, self._patch)

    @classmethod
    def apply_all(cls) -> None:
        """Apply all registered patches."""
        for patch in monkey._patches.values():
            if patch._origin is _NULL:
                patch._apply()
        monkey._reload_modules()

    @classmethod
    def _reload_modules(cls) -> None:
        """Reload all marked modules."""
        while monkey._to_reload:
            module = monkey._to_reload.pop()
            if module in monkey._protected:
                monkey._to_reload.clear()
                raise RuntimeError
            importlib.reload(sys.modules[module])

    @classmethod
    def target(cls, name: str) -> Patchable:
        """Returns the original unpatched target of a registered patch."""
        try:
            patch = monkey._patches[name]
        except KeyError as e:
            msg = f"{name} is not a known monkey patch."
            raise KeyError(msg) from e
        else:
            if patch._origin is _NULL:
                msg = f"target for {patch!r} is not yet available, call monkey.apply_all() before."
                raise RuntimeError(msg)
            return patch._origin

    def __call__(self, patch: Patch) -> Patch:
        """Decorator method."""
        # def wrapper(*args: Any, **kwargs: Any) -> Any:
        #     return patch(*args, **kwargs)
        self._patch = patch

        return patch

    def __str__(self) -> str:
        return f"{self._module}.{self._target}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self!s})"

    def __hash__(self) -> int:
        return hash((self._module, self._target))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and hash(other) == hash(self)

    @classmethod
    def patches(cls) -> list[str]:
        """Returns a list of patched targets name."""
        return [str(k) for k in monkey._patches]
