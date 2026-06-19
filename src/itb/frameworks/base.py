"""Framework encoder protocol. A framework produces a Theory."""

from abc import ABC, abstractmethod

from itb.theory import Theory
from itb.tower import TowerEvidence, TowerSpectrum


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
    # `fundamental`: is gravity a fundamental dynamical field with a UV EFT /
    # Wilson-coefficient expansion? Emergent/entropic gravity sets this False —
    # its physics is an IR/thermodynamic phenomenon, so a UV positivity verdict is
    # meaningless (v1.65).
    fundamental: bool = True

    @abstractmethod
    def encode(self) -> Theory:
        ...

    def tower_spectrum(self) -> TowerSpectrum | None:
        return None

    def tower_evidence(self) -> TowerEvidence | None:
        return None
