"""Framework encoder protocol. A framework produces a Theory."""

from abc import ABC, abstractmethod

from itb.theory import Theory


class Framework(ABC):
    name: str = ""
    citation: str = ""
    # Scope flags (v1.59): the engine's amplitude-positivity bounds are derived
    # assuming a LOCAL, LORENTZ-INVARIANT, unitary S-matrix; the swampland program
    # assumes locality. A framework that violates these is OUTSIDE the engine's
    # validity scope and its feasibility verdict is not meaningful. Defaults assume
    # in-scope; frameworks that break an assumption override these.
    local: bool = True
    lorentz_invariant: bool = True

    @abstractmethod
    def encode(self) -> Theory:
        ...
