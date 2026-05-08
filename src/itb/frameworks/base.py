"""Framework encoder protocol. A framework produces a Theory."""

from abc import ABC, abstractmethod

from itb.theory import Theory


class Framework(ABC):
    name: str = ""
    citation: str = ""

    @abstractmethod
    def encode(self) -> Theory:
        ...
