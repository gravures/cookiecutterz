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
"""Mapping module."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterator, Mapping
from test.support.import_helper import import_fresh_module
from typing import TYPE_CHECKING, Any, Callable, Protocol, TypeVar, cast


if TYPE_CHECKING:
    from types import ModuleType

# TODO: make a c implementation of OrderableDict
# TODO: expands docs of after and before method
# TODO: make a generic function for loading a python module instead its c verrsion

_VT = TypeVar("_VT")
_KT = TypeVar("_KT")
_collections: ModuleType = import_fresh_module("collections", blocked=["_collections"])
_OrderedDict = cast(type[OrderedDict[Any, Any]], _collections.OrderedDict)  # pyright: ignore[reportUnknownMemberType]


class _Link(Protocol[_KT]):
    __slots__ = "__weakref__", "key", "next", "prev"

    def __init__(self) -> None:
        self.key: _KT
        self.next: _Link[_KT]
        self.prev: _Link[_KT]


# FIXME: OrderableDict.values() iters on undefined type (Any)


class OrderableDict(_OrderedDict, dict[_KT, _VT]):
    """RordeableDict is a more capable OrderedDict."""

    def __init__(self, other: Any = (), /, **kwargs: _VT) -> None:
        super().__init__(other, **kwargs)
        self.__map: dict[_KT, _Link[_KT]] = getattr(self, "_OrderedDict__map")  # noqa: B009
        self.__root: _Link[_KT] = getattr(self, "_OrderedDict__root")  # noqa: B009

    @property
    def first(self) -> _KT:
        """Return the first key."""
        return self.__root.next.key

    @property
    def last(self) -> _KT:
        """Return the first key."""
        return self.__root.prev.key

    def _insert(self, *, key: _KT, value: _VT, _from: _KT) -> bool:
        if _from not in self:
            msg = f"{_from} not in OrderedDict"
            raise KeyError(msg)
        exist: bool = key in self
        super().__setitem__(key, value)
        return not exist

    def _move_key(self, key: _KT, other: _KT, before: bool = False) -> None:
        ref = self.__map[other]
        link = self.__map[key]
        link_prev = link.prev
        link_next = link.next
        soft_link = link_next.prev

        # remove ref
        link_prev.next = link_next
        link_next.prev = link_prev

        # insert ref
        if before:
            ref_prev = ref.prev
            link.prev = ref_prev
            link.next = ref_prev.next
            ref.prev = soft_link
            ref_prev.next = link
        else:
            ref_next = ref.next
            link.prev = ref_next.prev
            link.next = ref_next
            ref.next = link
            ref_next.prev = soft_link

    def _insert_after(self, key: _KT, value: _VT, other: _KT) -> None:
        """Insert a (key, value) after <after>."""
        if self._insert(key=key, value=value, _from=other):
            self._move_key(key=key, other=other)

    def after(self, key: _KT, other: _KT | None = None, value: _VT | None = None) -> None:
        """Inserts, moves or returns value after other key."""
        if other is None:
            raise NotImplementedError
        if value is None:
            if key not in self or other not in self:
                msg = f"{key} or {other} not in OrderedDict"
                raise KeyError(msg)
            self._move_key(key=key, other=other)
        elif self._insert(key=key, value=value, _from=other):
            self._move_key(key=key, other=other)

    def _insert_before(self, key: _KT, value: _VT, other: _KT) -> None:
        """Insert a (key, value) after <after>."""
        if self._insert(key=key, value=value, _from=other):
            self._move_key(key=key, other=other, before=True)

    def before(self, key: _KT, other: _KT | None = None, value: _VT | None = None) -> None:
        """Inserts, moves or returns value before other key."""
        if other is None:
            raise NotImplementedError
        if value is None:
            if key not in self or other not in self:
                msg = f"{key} or {other} not in OrderedDict"
                raise KeyError(msg)
            self._move_key(key=key, other=other, before=True)
        elif self._insert(key=key, value=value, _from=other):
            self._move_key(key=key, other=other, before=True)

    def _debug(self) -> str:
        return "\n".join([
            (
                f"key:{v.key}, prev:{getattr(v.prev, 'key', 'root')}"
                f", next:{getattr(v.next, 'key', 'root')}"
            )
            for v in self.__map.values()
        ])


class FilteredDictView(Mapping[_KT, _VT]):
    """Dictionary Filtered View."""

    # __contains__, keys, items, values, get, __eq__, and __ne__
    # are inherited from Mapping's mixin methods

    __slots__ = ("_keys", "_source")

    def __init__(self, source: Mapping[_KT, _VT], func: Callable[[_KT, _VT], bool]) -> None:
        self._source: Mapping[_KT, _VT] = source
        self._keys: set[_KT] = {k for k, v in source.items() if func(k, v)}

    def __getitem__(self, key: _KT) -> _VT:
        if key in self._keys:
            return self._source[key]
        raise KeyError(key)

    def __len__(self) -> int:
        return len(self._keys)

    def __iter__(self) -> Iterator[_KT]:
        yield from self._keys
