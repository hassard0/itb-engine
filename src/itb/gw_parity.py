"""Native GW parity packet schemas and guards.

These packets are intentionally not `g_R2_parity/g_R3_parity` evidence. They
hold published GW parity parameters in their native basis until a source-backed
operator and frequency-normalization adapter exists.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


VALID_NATIVE_BASES = {
    "ng_kappa_at_100hz",
    "sgwb_kappaD_kappaz",
    "parameterized_parity_ppv",
}

REQUIRED_NATIVE_PARAMETERS = {
    "ng_kappa_at_100hz": ("kappa_Gpc_inv", "f_ref_hz"),
    "sgwb_kappaD_kappaz": ("kappa_D_scale", "kappa_z_scale", "f_ref_hz"),
    "parameterized_parity_ppv": ("branch",),
}


@dataclass(frozen=True)
class GWParityNativePacket:
    label: str
    source_url: str
    parameter_basis: str
    measurement_kind: str
    parameters: dict[str, Any]
    public_code_url: str | None = None
    public_data_url: str | None = None
    public_docs_url: str | None = None
    public_likelihood_url: str | None = None
    source_backed_operator_map: bool = False
    frequency_normalization_ready: bool = False
    dimensional_conversion_ready: bool = False
    framework_exclusion_math_ready: bool = False
    engine_projection_status: str = "blocked_missing_engine_axis_adapter"
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "source_url": self.source_url,
            "parameter_basis": self.parameter_basis,
            "measurement_kind": self.measurement_kind,
            "parameters": dict(self.parameters),
            "public_code_url": self.public_code_url,
            "public_data_url": self.public_data_url,
            "public_docs_url": self.public_docs_url,
            "public_likelihood_url": self.public_likelihood_url,
            "source_backed_operator_map": self.source_backed_operator_map,
            "frequency_normalization_ready": self.frequency_normalization_ready,
            "dimensional_conversion_ready": self.dimensional_conversion_ready,
            "framework_exclusion_math_ready": self.framework_exclusion_math_ready,
            "engine_projection_status": self.engine_projection_status,
            "notes": list(self.notes),
        }


def validate_gw_parity_native_packet(
    packet: GWParityNativePacket | dict[str, Any],
) -> dict[str, Any]:
    row = packet.to_dict() if hasattr(packet, "to_dict") else dict(packet)
    parameter_basis = row.get("parameter_basis")
    parameters = row.get("parameters") or {}
    required = REQUIRED_NATIVE_PARAMETERS.get(str(parameter_basis), ())
    missing_parameters = [
        key for key in required
        if parameters.get(key) in (None, "")
    ]
    source_url = row.get("source_url") or ""
    source_url_valid = source_url.startswith(("https://arxiv.org/", "https://doi.org/"))
    measurement_kind_valid = row.get("measurement_kind") in {
        "external_native_posterior",
        "external_native_upper_bound",
        "theory_formalism",
    }
    public_material_ready = bool(
        row.get("public_code_url")
        and row.get("public_data_url")
        and row.get("public_likelihood_url")
    )
    native_basis_valid = parameter_basis in VALID_NATIVE_BASES
    native_packet_ready = (
        source_url_valid
        and native_basis_valid
        and measurement_kind_valid
        and not missing_parameters
        and public_material_ready
    )

    projection_blockers = []
    if not row.get("source_backed_operator_map"):
        projection_blockers.append("missing_source_backed_operator_map")
    if not row.get("frequency_normalization_ready"):
        projection_blockers.append("missing_frequency_normalization")
    if not row.get("dimensional_conversion_ready"):
        projection_blockers.append("missing_dimensionful_to_engine_normalization")
    if not row.get("framework_exclusion_math_ready"):
        projection_blockers.append("missing_framework_exclusion_math")
    if row.get("engine_projection_status") != "engine_projection_ready":
        projection_blockers.append("engine_projection_not_ready")

    native_blockers = []
    if not source_url_valid:
        native_blockers.append("source_url_not_primary_allowed")
    if not native_basis_valid:
        native_blockers.append("native_basis_not_allowed")
    if not measurement_kind_valid:
        native_blockers.append("measurement_kind_not_native_allowed")
    if missing_parameters:
        native_blockers.append("missing_required_native_parameters")
    if not public_material_ready:
        native_blockers.append("missing_public_code_data_or_likelihood")

    return {
        "native_packet_ready": native_packet_ready,
        "engine_projection_ready": native_packet_ready and not projection_blockers,
        "source_url_valid": source_url_valid,
        "native_basis_valid": native_basis_valid,
        "measurement_kind_valid": measurement_kind_valid,
        "public_material_ready": public_material_ready,
        "missing_parameters": missing_parameters,
        "native_blockers": sorted(set(native_blockers)),
        "projection_blockers": sorted(set(projection_blockers)),
        "blockers": sorted(set(native_blockers + projection_blockers)),
    }
