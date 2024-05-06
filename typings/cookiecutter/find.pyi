"""
This type stub file was generated by pyright.
"""

import os
from pathlib import Path
from jinja2 import Environment

"""Functions for finding Cookiecutter templates and other components."""
logger = ...

def find_template(repo_dir: os.PathLike[str], env: Environment) -> Path:
    """Determine which child directory of ``repo_dir`` is the project template.

    :param repo_dir: Local directory of newly cloned repo.
    :return: Relative path to project template.
    """
    ...
