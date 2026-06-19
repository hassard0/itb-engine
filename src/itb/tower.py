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

POSITIVE_CONTROL_FAMILY_MARKERS = (
    "known_qg_positive_control",
    "large_volume_calabi_yau_sdc",
    "large_volume_calabi_yau_sdc_lambda_table3",
    "one_planck_large_volume_displacement",
    "analytic_kk_decompactification_vector",
    "string_compatible_decompactification",
    "kk_decompactification",
)

FINITE_RANGE_MARKERS = (
    "finite_range",
    "quintic_scalar_laplacian_kk",
    "scalar_laplacian_subtower",
    "one-parameter quintic",
)

ASYMPTOTIC_RANGE_MARKERS = (
    "asymptotic",
    "large_volume",
    "decompactification",
)

SINGLE_COMPACTIFICATION_MARKERS = (
    "single_compactification",
    "one-parameter quintic",
    "quintic calabi-yau",
)

NATIVE_OWNERSHIP_MARKERS = {
    "endpoint": (
        "native_framework_endpoint",
        "framework_owned_endpoint",
        "endpoint_owned_by_framework",
    ),
    "displacement": (
        "native_framework_displacement",
        "framework_owned_displacement",
        "displacement_owned_by_framework",
    ),
}


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


def _metadata_tokens(value: Any) -> list[str]:
    if isinstance(value, dict):
        tokens = []
        for key, item in value.items():
            tokens.append(str(key).lower())
            tokens.extend(_metadata_tokens(item))
        return tokens
    if isinstance(value, (list, tuple, set)):
        tokens = []
        for item in value:
            tokens.extend(_metadata_tokens(item))
        return tokens
    if isinstance(value, str):
        return [value.lower()]
    if isinstance(value, bool) and value:
        return ["true"]
    return []


def tower_positive_control_matches(evidence: TowerEvidence | dict[str, Any]) -> list[str]:
    """Return known string-compatible positive-control markers in evidence.

    Positive controls are not bad data. They are cases that should not be promoted
    to framework exclusions merely because the diagnostic tower gate rejects them.
    """
    row = evidence.to_dict() if hasattr(evidence, "to_dict") else dict(evidence)
    tokens = _metadata_tokens(row)
    matches = [
        marker for marker in POSITIVE_CONTROL_FAMILY_MARKERS
        if any(marker in token for token in tokens)
    ]
    return sorted(set(matches))


def _tokens_match(tokens: list[str], markers: tuple[str, ...]) -> bool:
    return any(marker in token for marker in markers for token in tokens)


def _truthy_marker_present(value: Any, markers: tuple[str, ...]) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key).lower()
            if any(marker in key_text for marker in markers) and item not in (
                False,
                None,
                "",
                [],
                {},
                (),
            ):
                return True
            if _truthy_marker_present(item, markers):
                return True
    if isinstance(value, (list, tuple, set)):
        return any(_truthy_marker_present(item, markers) for item in value)
    return False


def classify_tower_source_scope(evidence: TowerEvidence | dict[str, Any]) -> dict[str, Any]:
    """Classify source scope for claim-readiness promotion.

    This classifier is conservative: unknown ownership is treated as not ready.
    It does not decide tower math, only whether the source looks like something
    that could be promoted to a generic framework claim.
    """
    row = evidence.to_dict() if hasattr(evidence, "to_dict") else dict(evidence)
    tokens = _metadata_tokens(row)
    positive_matches = tower_positive_control_matches(row)
    finite_range = _tokens_match(tokens, FINITE_RANGE_MARKERS)
    asymptotic = _tokens_match(tokens, ASYMPTOTIC_RANGE_MARKERS)
    single_compactification = _tokens_match(tokens, SINGLE_COMPACTIFICATION_MARKERS)
    endpoint_owned = _truthy_marker_present(
        row,
        NATIVE_OWNERSHIP_MARKERS["endpoint"],
    )
    displacement_owned = _truthy_marker_present(
        row,
        NATIVE_OWNERSHIP_MARKERS["displacement"],
    )

    if finite_range and not asymptotic:
        range_scope = "finite_range"
    elif asymptotic:
        range_scope = "asymptotic"
    else:
        range_scope = "unspecified"

    if single_compactification:
        compactification_scope = "single_compactification"
    elif positive_matches:
        compactification_scope = "decompactification_or_large_volume_benchmark"
    else:
        compactification_scope = "unspecified"

    if _tokens_match(tokens, ("scalar_laplacian", "laplacian_subtower")):
        tower_scope = "scalar_laplacian_subtower"
    elif _tokens_match(tokens, ("kk", "kaluza-klein")):
        tower_scope = "kk_or_decompactification_tower"
    else:
        tower_scope = "unspecified"

    scope_blockers = []
    if positive_matches:
        scope_blockers.append("known_qg_positive_control_family")
    if range_scope == "finite_range":
        scope_blockers.append("finite_range_not_asymptotic")
    elif range_scope != "asymptotic":
        scope_blockers.append("missing_asymptotic_range_scope")
    if single_compactification:
        scope_blockers.append("single_compactification_not_generic_framework")
    if not endpoint_owned:
        scope_blockers.append("missing_framework_owned_endpoint")
    if not displacement_owned:
        scope_blockers.append("missing_framework_owned_displacement")

    generic_framework_claim_ready = not scope_blockers
    return {
        "compactification_scope": compactification_scope,
        "tower_scope": tower_scope,
        "range_scope": range_scope,
        "endpoint_owned_by_framework": endpoint_owned,
        "displacement_owned_by_framework": displacement_owned,
        "positive_control_matches": positive_matches,
        "generic_framework_claim_ready": generic_framework_claim_ready,
        "scope_blockers": sorted(set(scope_blockers)),
    }


def evaluate_tower_promotion_guard(
    evidence: TowerEvidence | dict[str, Any],
    *,
    tower_claimable_by_math: bool,
) -> dict[str, Any]:
    """Gate a tower row against narrow known-positive-control promotion."""
    validation = validate_tower_evidence(evidence)
    source_scope = classify_tower_source_scope(evidence)
    positive_control_matches = source_scope["positive_control_matches"]
    blockers = []
    if not validation["ready_for_framework_claim"]:
        blockers.append("tower_evidence_not_ready")
    if not tower_claimable_by_math:
        blockers.append("tower_math_not_excluding")
    if positive_control_matches:
        blockers.append("known_qg_positive_control_family")

    return {
        "ready_for_promotion": not blockers,
        "tower_claimable_by_math": bool(tower_claimable_by_math),
        "evidence_ready": validation["ready_for_framework_claim"],
        "source_scope": source_scope,
        "positive_control_matches": positive_control_matches,
        "blockers": sorted(set(blockers)),
    }


def evaluate_generic_framework_claim_guard(
    evidence: TowerEvidence | dict[str, Any],
    *,
    tower_claimable_by_math: bool,
) -> dict[str, Any]:
    """Gate a tower row before a generic framework exclusion claim.

    This is stricter than the positive-control promotion guard. A row can pass
    promotion while still failing here because the endpoint or displacement is
    not owned by the framework under test.
    """
    promotion_guard = evaluate_tower_promotion_guard(
        evidence,
        tower_claimable_by_math=tower_claimable_by_math,
    )
    source_scope = promotion_guard["source_scope"]
    blockers = set(promotion_guard["blockers"])
    blockers.update(source_scope["scope_blockers"])

    return {
        "ready_for_generic_framework_claim": (
            promotion_guard["ready_for_promotion"]
            and source_scope["generic_framework_claim_ready"]
        ),
        "tower_claimable_by_math": bool(tower_claimable_by_math),
        "evidence_ready": promotion_guard["evidence_ready"],
        "source_scope": source_scope,
        "promotion_guard": promotion_guard,
        "positive_control_matches": promotion_guard["positive_control_matches"],
        "blockers": sorted(blockers),
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
