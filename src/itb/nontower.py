"""Non-tower discriminator promotion evidence and guardrails.

This module mirrors the tower-evidence guard pattern for discriminator routes
that do not use a tower spectrum: birefringence, Weyl-sector observables, and
matter high-moment probes. Internal island cuts are useful for experiment
design, but a framework claim requires external numerical evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExternalMeasurementEvidence:
    axis: str
    route: str
    source_url: str
    source_type: str
    measurement_kind: str
    numerical_value: float | None
    uncertainty: float | None
    axis_mapping_kind: str
    systematics_status: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "axis": self.axis,
            "route": self.route,
            "source_url": self.source_url,
            "source_type": self.source_type,
            "measurement_kind": self.measurement_kind,
            "numerical_value": self.numerical_value,
            "uncertainty": self.uncertainty,
            "axis_mapping_kind": self.axis_mapping_kind,
            "systematics_status": self.systematics_status,
            "metadata": dict(self.metadata),
        }


REQUIRED_EXTERNAL_MEASUREMENT_FIELDS = (
    "axis",
    "route",
    "source_url",
    "source_type",
    "measurement_kind",
    "axis_mapping_kind",
    "systematics_status",
)

VALID_SOURCE_TYPES = {
    "primary_literature",
    "public_dataset",
    "validated_measurement",
}

VALID_MEASUREMENT_KINDS = {
    "external_detection",
    "external_numeric_measurement",
    "external_upper_bound",
}

VALID_AXIS_MAPPING_KINDS = {
    "source_backed_direct",
    "validated_framework_adapter",
}

CLOSED_SYSTEMATICS_STATUSES = {
    "bounded",
    "closed",
}


def _as_dict(evidence: ExternalMeasurementEvidence | dict[str, Any]) -> dict[str, Any]:
    return evidence.to_dict() if hasattr(evidence, "to_dict") else dict(evidence)


def validate_external_measurement_evidence(
    evidence: ExternalMeasurementEvidence | dict[str, Any],
) -> dict[str, Any]:
    row = _as_dict(evidence)
    missing = [
        field for field in REQUIRED_EXTERNAL_MEASUREMENT_FIELDS
        if row.get(field) in (None, "")
    ]
    source_url = row.get("source_url") or ""
    source_url_valid = source_url.startswith(("https://arxiv.org/", "https://doi.org/"))
    source_type_valid = row.get("source_type") in VALID_SOURCE_TYPES
    measurement_kind_valid = row.get("measurement_kind") in VALID_MEASUREMENT_KINDS
    axis_mapping_valid = row.get("axis_mapping_kind") in VALID_AXIS_MAPPING_KINDS
    systematics_closed = row.get("systematics_status") in CLOSED_SYSTEMATICS_STATUSES
    numerical_value_present = row.get("numerical_value") is not None
    uncertainty = row.get("uncertainty")
    uncertainty_valid = isinstance(uncertainty, int | float) and float(uncertainty) > 0.0

    blockers = []
    if missing:
        blockers.append("missing_required_fields")
    if source_url and not source_url_valid:
        blockers.append("source_url_not_primary_allowed")
    if row.get("source_type") and not source_type_valid:
        blockers.append("source_type_not_allowed")
    if row.get("measurement_kind") and not measurement_kind_valid:
        blockers.append("measurement_kind_not_external_numeric")
    if not numerical_value_present or not uncertainty_valid:
        blockers.append("missing_external_numeric_measurement")
    if row.get("axis_mapping_kind") and not axis_mapping_valid:
        blockers.append("axis_mapping_not_source_backed")
    if row.get("systematics_status") and not systematics_closed:
        blockers.append("systematics_not_closed")

    return {
        "ready_for_discriminator_claim": not blockers,
        "missing_fields": sorted(set(missing)),
        "source_url_valid": source_url_valid,
        "source_type_valid": source_type_valid,
        "measurement_kind_valid": measurement_kind_valid,
        "axis_mapping_valid": axis_mapping_valid,
        "systematics_closed": systematics_closed,
        "numerical_value_present": numerical_value_present,
        "uncertainty_valid": uncertainty_valid,
        "blockers": sorted(set(blockers)),
    }


def evaluate_nontower_promotion_guard(
    evidence: ExternalMeasurementEvidence | dict[str, Any],
    *,
    discriminator_claimable_by_math: bool,
) -> dict[str, Any]:
    validation = validate_external_measurement_evidence(evidence)
    row = _as_dict(evidence)
    metadata = row.get("metadata") or {}
    blockers = set(validation["blockers"])
    if not validation["ready_for_discriminator_claim"]:
        blockers.add("external_measurement_evidence_not_ready")
    if not discriminator_claimable_by_math:
        blockers.add("discriminator_math_not_excluding")
    if metadata.get("internal_cut_only"):
        blockers.add("internal_cut_not_external_measurement")

    return {
        "ready_for_promotion": not blockers,
        "discriminator_claimable_by_math": bool(discriminator_claimable_by_math),
        "evidence_ready": validation["ready_for_discriminator_claim"],
        "validation": validation,
        "blockers": sorted(blockers),
    }
