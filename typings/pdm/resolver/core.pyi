"""
This type stub file was generated by pyright.
"""

from typing import TYPE_CHECKING
from pdm.models.candidates import Candidate
from pdm.models.requirements import Requirement
from resolvelib.resolvers import Resolver
from pdm.models.specifiers import PySpecSet

if TYPE_CHECKING:
    ...
def resolve(resolver: Resolver, requirements: list[Requirement], requires_python: PySpecSet, max_rounds: int = ..., keep_self: bool = ..., inherit_metadata: bool = ...) -> tuple[dict[str, Candidate], dict[tuple[str, str | None], list[Requirement]]]:
    """Core function to perform the actual resolve process.
    Return a tuple containing 2 items:

        1. A map of pinned candidates
        2. A map of resolved dependencies for each dependency group
    """
    ...
