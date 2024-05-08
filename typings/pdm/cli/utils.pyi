"""
This type stub file was generated by pyright.
"""

import argparse
import dataclasses as dc
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, TYPE_CHECKING, no_type_check
from resolvelib.structs import DirectedGraph
from rich.tree import Tree
from pdm.models.requirements import Requirement
from resolvelib.resolvers import ResolutionImpossible
from pdm.compat import Distribution, importlib_metadata as im
from pdm.models.candidates import Candidate
from pdm.models.repositories import BaseRepository
from pdm.project import Project

if TYPE_CHECKING:
    ...
class PdmFormatter(argparse.RawDescriptionHelpFormatter):
    def start_section(self, heading: str | None) -> None:
        ...



class ArgumentParser(argparse.ArgumentParser):
    """A standard argument parser but with title-cased help."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def parse_known_args(self, args: Any = ..., namespace: Any = ...) -> Any:
        ...



class ErrorArgumentParser(ArgumentParser):
    """A subclass of argparse.ArgumentParser that raises
    parsing error rather than exiting.

    This does the same as passing exit_on_error=False on Python 3.9+
    """
    ...


@dc.dataclass(frozen=True)
class Package:
    """An internal class for the convenience of dependency graph building."""
    name: str = ...
    version: str | None = ...
    requirements: dict[str, Requirement] = ...
    def __repr__(self) -> str:
        ...



def build_dependency_graph(working_set: Mapping[str, im.Distribution], marker_env: dict[str, str] | None = ..., selected: set[str] | None = ..., include_sub: bool = ...) -> DirectedGraph:
    """Build a dependency graph from locked result."""
    ...

def specifier_from_requirement(requirement: Requirement) -> str:
    ...

def add_package_to_tree(root: Tree, graph: DirectedGraph, package: Package, required: list[str], visited: frozenset[str] = ...) -> None:
    """Format one package.

    :param graph: the dependency graph
    :param package: the package instance
    :param required: the version required by its parent
    :param visited: the visited package collection
    """
    ...

def add_package_to_reverse_tree(root: Tree, graph: DirectedGraph, package: Package, child: Package | None = ..., requires: str = ..., visited: frozenset[str] = ...) -> None:
    """Format one package for output reverse dependency graph."""
    ...

def package_is_project(package: Package, project: Project) -> bool:
    ...

def build_forward_dependency_json_subtree(root: Package, project: Project, graph: DirectedGraph[Package | None], required_by: Package | None = ..., visited: frozenset[str] = ...) -> dict:
    ...

def build_reverse_dependency_json_subtree(root: Package, project: Project, graph: DirectedGraph[Package | None], requires: Package | None = ..., visited: frozenset[str] = ...) -> dict:
    ...

def package_match_patterns(package: Package, patterns: list[str]) -> bool:
    ...

def build_dependency_json_tree(project: Project, graph: DirectedGraph[Package | None], reverse: bool, patterns: list[str]) -> list[dict]:
    ...

def show_dependency_graph(project: Project, graph: DirectedGraph[Package | None], reverse: bool = ..., json: bool = ..., patterns: list[str] | None = ...) -> None:
    ...

def format_lockfile(project: Project, mapping: dict[str, Candidate], fetched_dependencies: dict[tuple[str, str | None], list[Requirement]], groups: list[str] | None, strategy: set[str]) -> dict:
    """Format lock file from a dict of resolved candidates, a mapping of dependencies
    and a collection of package summaries.
    """
    ...

def save_version_specifiers(requirements: dict[str, dict[str, Requirement]], resolved: dict[str, Candidate], save_strategy: str) -> None:
    """Rewrite the version specifiers according to the resolved result and save strategy

    :param requirements: the requirements to be updated
    :param resolved: the resolved mapping
    :param save_strategy: compatible/wildcard/exact
    """
    ...

def check_project_file(project: Project) -> None:
    """Check the existence of the project file and throws an error on failure."""
    ...

def find_importable_files(project: Project) -> Iterable[tuple[str, Path]]:
    """Find all possible files that can be imported"""
    ...

@no_type_check
def set_env_in_reg(env_name: str, value: str) -> None:
    """Manipulate the WinReg, and add value to the
    environment variable if exists or create new.
    """
    ...

def format_resolution_impossible(err: ResolutionImpossible) -> str:
    ...

def merge_dictionary(target: MutableMapping[Any, Any], input: Mapping[Any, Any], append_array: bool = ...) -> None:
    """Merge the input dict with the target while preserving the existing values
    properly. This will update the target dictionary in place.
    List values will be extended, but only if the value is not already in the list.
    """
    ...

def fetch_hashes(repository: BaseRepository, mapping: Mapping[str, Candidate]) -> None:
    """Fetch hashes for candidates in parallel"""
    ...

def is_pipx_installation() -> bool:
    ...

def is_homebrew_installation() -> bool:
    ...

def is_scoop_installation() -> bool:
    ...

def get_dist_location(dist: Distribution) -> str:
    ...

def get_pep582_path(project: Project) -> str:
    ...

def use_venv(project: Project, name: str) -> None:
    ...

def populate_requirement_names(req_mapping: dict[str, Requirement]) -> None:
    ...

def normalize_pattern(pattern: str) -> str:
    """Normalize a pattern to a valid name for a package."""
    ...