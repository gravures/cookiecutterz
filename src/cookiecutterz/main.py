# Copyright (c) 2023 - Gilles Coissac
# See end of file for extended copyright information
"""Allow cookiecutter to be executable through `python -m cookiecutter`."""
from __future__ import annotations

import click
from cookiecutter.cli import main as _main

from cookiecutterz.extensions import update as _update


# FIXME: call cookiecutterz with a dot


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context):
    """Cookiecutterz wrapper command.

    To use cookiecutter as usual insert a dot as a subcommand:

        ex: cookiecutter . -f https://github.com/repo/cookiecutter-template.git

    Cookiecutter is free and open source software, developed and managed by
    volunteers. If you would like to help out or fund the project, please get
    in touch at https://github.com/cookiecutter/cookiecutter.
    """
    if ctx.invoked_subcommand is None:
        if ctx.params:
            ctx.invoke(_main)
        else:
            click.echo(ctx.get_help())


@main.command()
@click.argument(
    "project",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=False,
)
def update(project: str = "."):
    """Update an existing cookiecutter generated project."""
    click.echo(f"Updating cookiecutter {project} project...")
    _update(project)


main.add_command(_main, ".")


if __name__ == "__main__":
    main()


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
