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
"""Cookiecutterz CLI entrypoint."""

from __future__ import annotations

import click
from click import command, secho
from cookiecutter.cli import main as _main


class ModGroup(click.Group):  # noqa: D101
    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:  # noqa: D102
        if (rv := super().get_command(ctx, cmd_name)) is not None:
            return rv
        return super().get_command(ctx, "create")

    def resolve_command(  # noqa: D102
        self, ctx: click.Context, args: list[str]
    ) -> tuple[str | None, click.Command | None, list[str]]:
        # always return the full command name
        name, cmd, args = super().resolve_command(ctx, args)

        if name != "create" and cmd and cmd.name == "main":
            args.insert(0, name or "")
            name = "create"
            cmd = self.get_command(ctx, "create")
        if name == "create":
            args.append("--overwrite-if-exists")  # FIXME: fix this dirty hack
        # print(name, cmd, args)
        return name, cmd, args


@command(cls=ModGroup, invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """You can omit the 'create' subcommand.

    Cookiecutter is free and open source software, developed and managed by
    volunteers. If you would like to help out or fund the project, please get
    in touch at https://github.com/cookiecutter/cookiecutter.
    """
    secho(
        "This a cookiecutter(z) program version with template extension feature.",
        fg="green",
    )
    if ctx.invoked_subcommand is None:
        if ctx.params:
            ctx.invoke(_main)
        else:
            click.echo(ctx.get_help())


cli.add_command(_main, "create")


@cli.command()
@click.argument(
    "project",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=False,
)
def update(project: str = "."):
    """Update an existing cookiecutter generated project."""
    click.echo(f"Updating cookiecutter {project} project...")
    # _update(project)


if __name__ == "__main__":
    cli()
