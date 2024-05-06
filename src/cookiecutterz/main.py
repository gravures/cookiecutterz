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
"""Allow cookiecutter to be executable through `python -m cookiecutter`."""

from __future__ import annotations

from click.utils import echo
from cookiecutter.cli import main as _main


def main():  # noqa: D103
    echo("This the cookiecutter(z) program version with template extension feature.")
    echo("")
    _main()


if __name__ == "__main__":
    main()
