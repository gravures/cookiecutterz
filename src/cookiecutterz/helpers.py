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
"""Helpers module."""

from __future__ import annotations

import logging
import sys
from importlib.util import module_from_spec, spec_from_file_location
from typing import TYPE_CHECKING

from cookiecutterz.main import LOG_LEVEL


if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType

logger = logging.getLogger(f"cookiecutter.{__name__}")


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
