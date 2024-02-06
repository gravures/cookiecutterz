from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Generator

import pytest
from pytest import fixture


#
# UTILITIES
def run(*args: str, capture: bool = False, **kwargs) -> str:
    """Run a command and return stdout."""
    cmd = shutil.which(args[0], mode=os.X_OK)
    if not cmd:
        raise OSError(f"ERROR: could not find {args[0]} executable")

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


#
# FIXTURES
TEST_DIR_NAME: str = "test_template_creation"
TEST_TEMPLATE: Path = Path.home() / "DEV" / "REPOS" / "cookiecutter_pep_517"


@fixture(scope="session")
def tmp_dir() -> Generator:
    test_dir = Path.cwd() / TEST_DIR_NAME
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    shutil.rmtree(test_dir)


@fixture(scope="function")
def extra_context(request) -> dict[str, str]:
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
def test_cookiecutter_create(tmp_dir, extra_context):
    _xc = (f"{k}={v}" for k, v in extra_context.items())
    run("cookiecutter", "--no-input", str(TEST_TEMPLATE), *_xc, cwd=tmp_dir)


@pytest.mark.fix_data("Cruft")
def test_cruft_create(tmp_dir, extra_context):
    _xc = json.dumps(extra_context)
    run("cruft", "create", "--no-input", str(TEST_TEMPLATE), "--extra-context", _xc, cwd=tmp_dir)


@pytest.mark.fix_data("Pdm")
def test_pdm_create(tmp_dir, extra_context):
    _xc = json.dumps(extra_context)
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


# should forbid circular dependencies beetween templates
# template dont have to overload input field of ancestor
# template could overload input field of ancestor
# template do not need to redefined _copy_without_render dict of ancestor
# template could have multiples inheritance