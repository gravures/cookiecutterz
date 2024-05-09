from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from tempfile import mkdtemp
from typing import TYPE_CHECKING, Any

import pytest
from pytest import fixture


if TYPE_CHECKING:
    from collections.abc import Generator


#
# UTILITIES
def run(*args: str, capture: bool = False, **kwargs: Any) -> str:
    """Run a command and return stdout."""
    cmd = shutil.which(args[0], mode=os.X_OK)
    if not cmd:
        msg = f"ERROR: could not find {args[0]} executable"
        raise OSError(msg)

    _args = list(args)
    _args[0] = cmd
    cp = subprocess.run(
        _args,
        capture_output=capture,
        shell=False,  # noqa: S603
        encoding="UTF-8",
        check=True,
        text=True,
        **kwargs,
    )
    return cp.stdout or ""


# TEST_TEMPLATE = "https://github.com/testdrivenio/cookiecutter-flask-skeleton"
# TEST_TEMPLATE = "https://github.com/audreyfeldroy/cookiecutter-pypackage"
TEST_TEMPLATE = Path.home() / "DEV/REPOS/cookiecutter_pep_517"


#
# FIXTURES
@fixture(scope="session")
def tmp_dir() -> Generator[Path, None, None]:
    test_dir = Path(mkdtemp())
    yield test_dir
    shutil.rmtree(test_dir)


@fixture()
def extra_context(request: Any) -> dict[str, str]:
    name = request.node.get_closest_marker("fix_data").args[0]
    return {
        "project_name": f"Pep{name}",
        "package_name": "what",
        "author_name": "John Doe",
        "author_email": "john.doe@example.com",
        "short_description": "A Short description.",
        "git_account": "johndoe",
    }


#
# PROPERTIES AND TEST CASES
@pytest.mark.fix_data("Cookiecutter")
def test_cookiecutter_create(tmp_dir: Path, extra_context: dict[str, str]) -> None:
    _xc = (f"{k}={v}" for k, v in extra_context.items())
    run("cookiecutter", "--no-input", str(TEST_TEMPLATE), *_xc, cwd=tmp_dir)


@pytest.mark.fix_data("Cruft")
def test_cruft_create(tmp_dir: Path, extra_context: dict[str, str]):
    _xc: str = json.dumps(extra_context)
    run("cruft", "create", "--no-input", str(TEST_TEMPLATE), "--extra-context", _xc, cwd=tmp_dir)


@pytest.mark.fix_data("Pdm")
def test_pdm_create(tmp_dir: Path, extra_context: dict[str, str]) -> None:
    _xc: str = json.dumps(extra_context)
    run(
        "pdm",
        "init",
        "--cruft",
        str(TEST_TEMPLATE),
        "--no-input",
        "--extra-context",
        _xc,
        cwd=tmp_dir,
    )


# should run on template with missing pre_gen_hook
# should forbid circular dependencies between templates
# template dont have to overload input field of ancestor
# template could overload input field of ancestor
# template do not need to redefined _copy_without_render dict of ancestor
# template could have multiples inheritance
# template could inherite from an unaware cookicutterz template
