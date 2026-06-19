"""Tower-spectrum prediction contract.

Frameworks may optionally expose a normalized tower spectrum through this
dataclass. The tower coordinate is intentionally separate from
`Theory.coefficients` so legacy Wilson-coefficient constraints remain
unchanged unless an experiment explicitly consumes the tower axis.
"""

from dataclasses import dataclass, field
import math
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


def sdc_tower_spectrum(
    *,
    tower_family: str,
    delta_moduli_mean: float,
    delta_moduli_sigma: float,
    lambda_sdc: float,
    normalization: str,
    source: str,
    metadata: dict[str, Any] | None = None,
) -> TowerSpectrum:
    """Convert an SDC exponential tower relation into a TowerSpectrum.

    The convention matches the v2.20 diagnostic tower coordinate:
    m_tower / m0 = exp(-phi_tower), with phi_tower = lambda_sdc * Delta.
    """
    if lambda_sdc <= 0.0:
        raise ValueError("lambda_sdc must be positive")
    if delta_moduli_mean < 0.0:
        raise ValueError("delta_moduli_mean must be non-negative")
    if delta_moduli_sigma < 0.0:
        raise ValueError("delta_moduli_sigma must be non-negative")

    phi_mean = lambda_sdc * delta_moduli_mean
    phi_sigma = lambda_sdc * delta_moduli_sigma
    adapter_metadata = {
        "delta_moduli_mean": delta_moduli_mean,
        "delta_moduli_sigma": delta_moduli_sigma,
        "lambda_sdc": lambda_sdc,
        "relation": "m_tower/m0 = exp(-lambda_sdc * Delta_moduli)",
    }
    if metadata:
        adapter_metadata.update(metadata)

    return TowerSpectrum(
        tower_family=tower_family,
        phi_tower_mean=phi_mean,
        phi_tower_sigma=phi_sigma,
        tower_mass_gap=math.exp(-phi_mean),
        normalization=normalization,
        source=source,
        metadata=adapter_metadata,
    )


def kk_radius_tower_spectrum(
    *,
    tower_family: str,
    radius_ratio_mean: float,
    log_radius_sigma: float,
    normalization: str,
    source: str,
    metadata: dict[str, Any] | None = None,
) -> TowerSpectrum:
    """Convert a KK radius ratio into a TowerSpectrum.

    The convention is m_KK/m0 = R0/R, hence phi_tower = log(R/R0).
    The uncertainty is supplied directly as one-sigma uncertainty in log(R/R0).
    """
    if radius_ratio_mean <= 0.0:
        raise ValueError("radius_ratio_mean must be positive")
    if log_radius_sigma < 0.0:
        raise ValueError("log_radius_sigma must be non-negative")

    phi_mean = math.log(radius_ratio_mean)
    adapter_metadata = {
        "radius_ratio_mean": radius_ratio_mean,
        "log_radius_sigma": log_radius_sigma,
        "relation": "m_KK/m0 = R0/R = exp(-log(R/R0))",
    }
    if metadata:
        adapter_metadata.update(metadata)

    return TowerSpectrum(
        tower_family=tower_family,
        phi_tower_mean=phi_mean,
        phi_tower_sigma=log_radius_sigma,
        tower_mass_gap=1.0 / radius_ratio_mean,
        normalization=normalization,
        source=source,
        metadata=adapter_metadata,
    )
