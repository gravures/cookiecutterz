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
        if options.generator == "cruft":  # noqa: PLR2004
            hooks = HookManager(project, options.skip)
            self._init_cruft(project, options)
            hooks.try_emit("post_init")
        else:
            super().do_init(project, options)

    def _init_cruft(self, project: Project, options: Namespace) -> None:
        if not package_installed("cruft"):
            raise PdmUsageError(
                "--cruft is passed but cruft is not installed. Install it by `pdm self add cruft`"
            ) from None

        from cruft._cli import app

        if not options.template:
            raise PdmUsageError("template argument is required when --cruft is passed")

        if "--output-dir" in options.generator_args:  # noqa: PLR2004
            raise PdmUsageError(
                "specify output directory with --project option not with --output-dir."
            )

        try:
            app(
                [
                    "create",
                    options.template,
                    "--output-dir",
                    str(project.root),
                    *options.generator_args,
                ]
            )
        except SystemExit as e:
            if e.code:
                raise RuntimeError("Cruft exited with non-zero status code") from e

    def add_arguments(self, parser: ArgumentParser) -> None:
        # NOTE: This will leave us with '--cruft' output after '--overwrite'
        #       in <pdm init --help> output, it's not ideal but argparse is
        #       a nigthmare to introspect and find how it order things.
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
    core.register_command(Plugin, "init")
