"""
This type stub file was generated by pyright.
"""

from typing import Optional

class AltTemporaryDirectory:
    def __init__(self, directory: Optional[str] = ...) -> None:
        ...

    def __enter__(self): # -> str:
        ...

    def cleanup(self, cnt=...): # -> None:
        ...

    def __exit__(self, exc, value, tb): # -> None:
        ...
