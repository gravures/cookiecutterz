"""
This type stub file was generated by pyright.
"""

import sys
from pathlib import Path
from typing import Optional, Set
from git import Repo
from .cookiecutter import CookiecutterContext
from .cruft import CruftState

if not sys.version_info >= (3, 11):
    ...
else:
    ...
def cookiecutter_template(output_dir: Path, repo: Repo, cruft_state: CruftState, project_dir: Path = ..., cookiecutter_input: bool = ..., checkout: Optional[str] = ..., deleted_paths: Optional[Set[Path]] = ..., update_deleted_paths: bool = ...) -> CookiecutterContext:
    """Generate a clean cookiecutter template in output_dir."""
    ...
