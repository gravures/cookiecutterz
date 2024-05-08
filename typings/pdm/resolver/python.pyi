"""
This type stub file was generated by pyright.
"""

from typing import Iterable, Iterator, Mapping
from pdm.models.candidates import Candidate
from pdm.models.requirements import NamedRequirement, Requirement
from pdm.models.specifiers import PySpecSet

"""
Special requirement and candidate classes to describe a requires-python constraint
"""
class PythonCandidate(Candidate):
    def format(self) -> str:
        ...



class PythonRequirement(NamedRequirement):
    @classmethod
    def from_pyspec_set(cls, spec: PySpecSet) -> PythonRequirement:
        ...

    def as_candidate(self) -> PythonCandidate:
        ...



def find_python_matches(identifier: str, requirements: Mapping[str, Iterator[Requirement]]) -> Iterable[Candidate]:
    """All requires-python except for the first one(must come from the project)
    must be superset of the first one.
    """
    ...

def is_python_satisfied_by(requirement: Requirement, candidate: Candidate) -> bool:
    ...
