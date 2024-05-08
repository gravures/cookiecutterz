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
"""Pdm plugin adding cruft to init option."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pdm import termui
from pdm.cli.commands.init import Command
from pdm.cli.hooks import HookManager
from pdm.exceptions import PdmUsageError
from pdm.utils import package_installed


if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace, _MutuallyExclusiveGroup

    from pdm.core import Core
    from pdm.project import Project


class Plugin(Command):
    """Initialize a pyproject.toml for PDM."""

    def do_init(self, project: Project, options: Namespace) -> None:
        """Bootstrap the project and create a pyproject.toml."""
        if options.generator == "cruft":
            hooks = HookManager(project, options.skip)
            self._init_cruft(project, options)
            hooks.try_emit("post_init")
        else:
            super().do_init(project, options)

    @staticmethod
    def _init_cruft(project: Project, options: Namespace) -> None:
        if not package_installed("cruft"):
            msg = (
                "--cruft is passed but cruft is not installed. Install it by `pdm self add cruft`"
            )
            raise PdmUsageError(msg) from None

        from cruft._cli import app  # noqa: PLC0415

        if not options.template:
            msg = "template argument is required when --cruft is passed"
            raise PdmUsageError(msg)

        if "--output-dir" in options.generator_args:
            msg = "specify output directory with --project option not with --output-dir."
            raise PdmUsageError(msg)

        try:
            app([
                "create",
                options.template,
                "--output-dir",
                str(project.root),  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownArgumentType]
                *options.generator_args,
            ])
        except SystemExit as e:
            if e.code:
                msg = "Cruft exited with non-zero status code"
                raise RuntimeError(msg) from e

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Adds --cruft option to init command."""
        # NOTE: This will leave us with '--cruft' output after '--overwrite'
        #       in <pdm init --help> output, it's not ideal but argparse is
        #       a nightmare to introspect and find how it order things.
        super().add_arguments(parser)
        status = {
            False: termui.style("\\[not installed]", style="error"),
            True: termui.style("\\[installed]", style="success"),
        }
        generator: _MutuallyExclusiveGroup = parser._mutually_exclusive_groups[-1]
        generator.add_argument(
            "--cruft",
            action="store_const",
            dest="generator",
            const="cruft",
            help=f"Use Cruft to generate project {status[package_installed('cruft')]}",
        )


def main(core: Core) -> None:
    """Plugin entrry point."""
    core.register_command(Plugin, "init")
