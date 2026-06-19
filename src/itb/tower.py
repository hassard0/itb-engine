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


@dataclass(frozen=True)
class TowerEvidence:
    framework: str
    spectrum: TowerSpectrum
    adapter_kind: str
    source_url: str
    source_type: str
    derivation_kind: str
    uncertainty_kind: str
    normalization_reference: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "framework": self.framework,
            "spectrum": self.spectrum.to_dict(),
            "adapter_kind": self.adapter_kind,
            "source_url": self.source_url,
            "source_type": self.source_type,
            "derivation_kind": self.derivation_kind,
            "uncertainty_kind": self.uncertainty_kind,
            "normalization_reference": self.normalization_reference,
            "metadata": dict(self.metadata),
        }


REQUIRED_TOWER_EVIDENCE_FIELDS = (
    "framework",
    "adapter_kind",
    "source_url",
    "source_type",
    "derivation_kind",
    "uncertainty_kind",
    "normalization_reference",
)


def validate_tower_evidence(evidence: TowerEvidence | dict[str, Any]) -> dict[str, Any]:
    row = evidence.to_dict() if hasattr(evidence, "to_dict") else dict(evidence)
    missing = [
        field for field in REQUIRED_TOWER_EVIDENCE_FIELDS
        if row.get(field) in (None, "")
    ]
    spectrum = row.get("spectrum")
    if not isinstance(spectrum, dict):
        missing.append("spectrum")
    else:
        for field in ("tower_family", "phi_tower_mean", "phi_tower_sigma", "normalization", "source"):
            if spectrum.get(field) in (None, ""):
                missing.append(f"spectrum.{field}")

    source_url = row.get("source_url") or ""
    source_url_valid = source_url.startswith(("https://arxiv.org/", "https://doi.org/"))
    source_type = row.get("source_type")
    source_type_valid = source_type in {
        "primary_literature",
        "computed_compactification",
        "validated_measurement",
    }
    ready = not missing and source_url_valid and source_type_valid
    blockers = []
    if missing:
        blockers.append("missing_required_fields")
    if source_url and not source_url_valid:
        blockers.append("source_url_not_primary_allowed")
    if source_type and not source_type_valid:
        blockers.append("source_type_not_allowed")

    return {
        "ready_for_framework_claim": ready,
        "missing_fields": sorted(set(missing)),
        "source_url_valid": source_url_valid,
        "source_type_valid": source_type_valid,
        "blockers": blockers,
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
