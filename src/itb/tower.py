"""Tower-spectrum prediction contract.

Frameworks may optionally expose a normalized tower spectrum through this
dataclass. The tower coordinate is intentionally separate from
`Theory.coefficients` so legacy Wilson-coefficient constraints remain
unchanged unless an experiment explicitly consumes the tower axis.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TowerSpectrum:
    tower_family: str
    phi_tower_mean: float | None
    phi_tower_sigma: float | None
    normalization: str
    source: str
    tower_mass_gap: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tower_family": self.tower_family,
            "phi_tower_mean": self.phi_tower_mean,
            "phi_tower_sigma": self.phi_tower_sigma,
            "normalization": self.normalization,
            "source": self.source,
            "tower_mass_gap": self.tower_mass_gap,
            "metadata": dict(self.metadata),
        }
