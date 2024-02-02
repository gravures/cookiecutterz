# Copyright (c) 2023 - Gilles Coissac
# See end of file for extended copyright information
"""Module utility for merging files trees."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Self

from binaryornot.check import is_binary


if TYPE_CHECKING:
    from os import PathLike


class File:
    """A virtual file type."""

    __slots__ = ("_path", "_depth")

    def __new__(cls, path: PathLike, depth: int = 0) -> Self:
        path = Path(path)
        if cls is File:
            if not path.exists():
                pass
            elif path.is_dir():
                cls = Directory
            elif path.is_file():
                cls = BinaryFile if is_binary(str(path)) else TextFile
            else:
                raise AttributeError(
                    f"{path} is of an unsupported type (eg: symlink, block device, ...).",
                )
            return super().__new__(cls)
        raise TypeError(f"{cls} is not directly instantiable.")

    def __init__(self, path: PathLike, depth: int = 0):
        self._path: Path = Path(path)
        self._depth: int = depth

    @property
    def name(self) -> str:
        """The final path component."""
        return self._path.name

    def __str__(self) -> str:
        return str(self.name)

    def __fspath__(self) -> str:
        return str(self._path)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._path}, depth={self._depth})"


class TextFile(File):
    """A text file."""


class BinaryFile(File):
    """A binary file."""


class Diff:
    """A diff between two files."""

    def __init__(
        self,
        a_file: File,
        b_file: File | None = None,
        dest: Directory | None = None,
        backup: bool = False,  # noqa: FBT001
    ) -> None:
        if b_file is None:
            self.diff = f"copy {a_file} into {dest.__repr__()}"
        else:
            self.diff = f"ndiff {a_file} | {b_file} into {b_file._path}"
        if backup and b_file is not None:
            self.diff += f" and backup {b_file} into {dest.__repr__()}"

        self.a_file = a_file
        self.b_file = b_file
        self.dest = dest

    def __str__(self) -> str:
        return self.diff


class Directory(File):
    """A directory."""

    __slots__ = ("children",)

    def __init__(self, path: PathLike, depth: int = 0) -> None:
        super().__init__(path, depth)
        if not self._path.is_dir():
            raise FileNotFoundError(f"Directory {self._path} not found.")
        self.children = [File(tmp, self._depth + 1) for tmp in self._path.glob("*")]

    def diff(self, other: Directory) -> list[Diff]:
        """Compute the difference with another Directory."""
        if not isinstance(other, Directory):
            raise TypeError(f"Expected Directory, got {type(other)}")
        if self._path.is_relative_to(other._path) or other._path.is_relative_to(self._path):
            raise AttributeError("One directory is relative to the other.")

        diffs = []
        for a_file in self:
            if a_file in other:
                b_file: File = other[a_file.name]
                if isinstance(a_file, Directory) and isinstance(b_file, Directory):
                    diffs.extend(a_file.diff(b_file))
                elif isinstance(a_file, TextFile) and isinstance(b_file, TextFile):
                    diffs.append(Diff(a_file, b_file, None))
                else:
                    diffs.append(Diff(a_file, None, other, backup=True))
            else:
                diffs.append(Diff(a_file, None, other))
        return diffs

    def _typestr(self, file: File) -> str:
        """The type of this File."""
        return "" if isinstance(file, Directory) else f" ({file.__class__.__name__})"

    def __str__(self) -> str:
        indent = "|   " * (self._depth) + "|__ "
        contents = "\n".join(
            [
                f"{indent}{tmp}{self._typestr(tmp)}"
                for tmp in sorted(self.children, key=lambda x: x.name)
            ],
        )
        name = self.name if self._depth else self._path
        return f"{name}/\n{contents}"

    def __iter__(self):
        return iter(self.children)

    def __contains__(self, item: File) -> bool:
        if not isinstance(item, File):
            raise TypeError(f"{item} is not a File.")
        return any(tmp.name == item.name for tmp in self.children)

    def __getitem__(self, name: str) -> File:
        for tmp in self.children:
            if tmp.name == name:
                return tmp
        raise KeyError(f"{name} not found in {self._path}.")


def merge(project_dir: str, update_dir: str) -> None:
    """Merge an existing cookiecutter generated project with an updated one."""
    print("Merging update...")


# def merge_fles(a: str, b: str):
#     """Merge two files."""
#     with Path(a).open("r") as file_a, Path(b).open("r") as file_b:
#         txt_a = file_a.readlines()
#         txt_b = file_b.readlines()
#     diffs = difflib.ndiff(txt_a, txt_b)

#     with Path("0.toml").open("w") as out:
#         for diff in diffs:
#             if diff[:1] not in ("-", "+", "?"):
#                 out.write(diff[2:])

#     try:
#         cp = subprocess.run(
#             ["git", "merge-file", "-p", a, "0.toml", b],
#             shell=False,
#             check=True,
#             capture_output=True,
#             text=True,
#         )
#     except CalledProcessError:
#         print(cp.stderr)
#     else:
#         with Path("merged.toml").open("w") as out:
#             out.write(cp.stdout)


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
