"""
This type stub file was generated by pyright.
"""

import os
from pathlib import Path

"""Functions for discovering and executing various cookiecutter hooks."""
logger = ...
_HOOKS = ...
EXIT_SUCCESS = ...
def valid_hook(hook_file, hook_name): # -> bool:
    """Determine if a hook file is valid.

    :param hook_file: The hook file to consider for validity
    :param hook_name: The hook to find
    :return: The hook file validity
    """
    ...

def find_hook(hook_name, hooks_dir=...): # -> list[Any] | None:
    """Return a dict of all hook scripts provided.

    Must be called with the project template as the current working directory.
    Dict's key will be the hook/script's name, without extension, while values
    will be the absolute path to the script. Missing scripts will not be
    included in the returned dict.

    :param hook_name: The hook to find
    :param hooks_dir: The hook directory in the template
    :return: The absolute path to the hook script or None
    """
    ...

def run_script(script_path, cwd=...): # -> None:
    """Execute a script from a working directory.

    :param script_path: Absolute path to the script to run.
    :param cwd: The directory to run the script from.
    """
    ...

def run_script_with_context(script_path, cwd, context): # -> None:
    """Execute a script after rendering it with Jinja.

    :param script_path: Absolute path to the script to run.
    :param cwd: The directory to run the script from.
    :param context: Cookiecutter project template context.
    """
    ...

def run_hook(hook_name, project_dir, context): # -> None:
    """
    Try to find and execute a hook from the specified project directory.

    :param hook_name: The hook to execute.
    :param project_dir: The directory to execute the script from.
    :param context: Cookiecutter project context.
    """
    ...

def run_hook_from_repo_dir(repo_dir, hook_name, project_dir, context, delete_project_on_failure): # -> None:
    """Run hook from repo directory, clean project directory if hook fails.

    :param repo_dir: Project template input directory.
    :param hook_name: The hook to execute.
    :param project_dir: The directory to execute the script from.
    :param context: Cookiecutter project context.
    :param delete_project_on_failure: Delete the project directory on hook
        failure?
    """
    ...

def run_pre_prompt_hook(repo_dir: os.PathLike[str]) -> Path:
    """Run pre_prompt hook from repo directory.

    :param repo_dir: Project template input directory.
    """
    ...
