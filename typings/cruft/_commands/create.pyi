"""
This type stub file was generated by pyright.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from .utils import example

@example("https://github.com/timothycrosley/cookiecutter-python/")
def create(template_git_url: str, output_dir: Path = ..., config_file: Optional[Path] = ..., default_config: bool = ..., extra_context: Optional[Dict[str, Any]] = ..., no_input: bool = ..., directory: Optional[str] = ..., checkout: Optional[str] = ..., overwrite_if_exists: bool = ..., skip: Optional[List[str]] = ...) -> Path:
    """Expand a Git based Cookiecutter template into a new project on disk."""
    ...
