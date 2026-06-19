"""Native GW parity packet schemas and guards.

These packets are intentionally not `g_R2_parity/g_R3_parity` evidence. They
hold published GW parity parameters in their native basis until a source-backed
operator and frequency-normalization adapter exists.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any

import numpy as np


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


@dataclass(frozen=True)
class GWParityAmplitudeLogGain:
    """Dimensionless source-native amplitude-birefringence exponent.

    This is the `v(f)` / log-gain layer used by source papers. It is not an
    engine Wilson coefficient and deliberately carries projection blockers.
    """

    source: str
    value: float
    frequency_hz: float
    f_ref_hz: float
    distance_gpc: float | None = None
    redshift: float | None = None
    native_parameters: dict[str, float] = field(default_factory=dict)
    helicity_convention: str = "source_native_unharmonized"
    target_basis: str = "ppv_amplitude_log_gain"
    engine_projection_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "value": self.value,
            "frequency_hz": self.frequency_hz,
            "f_ref_hz": self.f_ref_hz,
            "distance_gpc": self.distance_gpc,
            "redshift": self.redshift,
            "native_parameters": dict(self.native_parameters),
            "helicity_convention": self.helicity_convention,
            "target_basis": self.target_basis,
            "engine_projection_allowed": self.engine_projection_allowed,
        }


def ng_kappa_amplitude_log_gain(
    *,
    kappa_gpc_inv: float,
    distance_gpc: float,
    frequency_hz: float,
    f_ref_hz: float = 100.0,
) -> GWParityAmplitudeLogGain:
    """Ng et al. native exponent: kappa * D_C * f / 100 Hz."""
    value = float(kappa_gpc_inv) * float(distance_gpc) * (
        float(frequency_hz) / float(f_ref_hz)
    )
    return GWParityAmplitudeLogGain(
        source="ng_gwtc3_kappa_at_100hz",
        value=value,
        frequency_hz=float(frequency_hz),
        f_ref_hz=float(f_ref_hz),
        distance_gpc=float(distance_gpc),
        native_parameters={"kappa_Gpc_inv": float(kappa_gpc_inv)},
        helicity_convention="positive_kappa_enhances_left_in_ng_convention",
    )


def callister_sgwb_amplitude_log_gain(
    *,
    kappa_d: float,
    kappa_z: float,
    distance_gpc: float,
    redshift: float,
    frequency_hz: float,
    f_ref_hz: float = 100.0,
) -> GWParityAmplitudeLogGain:
    """Callister et al. native exponent: pi*f/100Hz*(kappa_z*z+kappa_D*D_C/Gpc)."""
    bracket = float(kappa_z) * float(redshift) + float(kappa_d) * float(distance_gpc)
    value = math.pi * (float(frequency_hz) / float(f_ref_hz)) * bracket
    return GWParityAmplitudeLogGain(
        source="callister_sgwb_kappaD_kappaz",
        value=value,
        frequency_hz=float(frequency_hz),
        f_ref_hz=float(f_ref_hz),
        distance_gpc=float(distance_gpc),
        redshift=float(redshift),
        native_parameters={
            "kappa_D": float(kappa_d),
            "kappa_z": float(kappa_z),
        },
        helicity_convention="positive_vp_right_enhanced_in_callister_convention",
    )


def callister_sgwb_energy_hyperbolic_argument(
    *,
    kappa_d: float,
    kappa_z: float,
    distance_gpc: float,
    redshift: float,
    frequency_hz: float,
    f_ref_hz: float = 100.0,
) -> GWParityAmplitudeLogGain:
    """Callister public-code convention for SGWB energy density: A = 2 v_p."""
    log_gain = callister_sgwb_amplitude_log_gain(
        kappa_d=kappa_d,
        kappa_z=kappa_z,
        distance_gpc=distance_gpc,
        redshift=redshift,
        frequency_hz=frequency_hz,
        f_ref_hz=f_ref_hz,
    )
    return GWParityAmplitudeLogGain(
        source="callister_sgwb_kappaD_kappaz_energy_density",
        value=2.0 * log_gain.value,
        frequency_hz=log_gain.frequency_hz,
        f_ref_hz=log_gain.f_ref_hz,
        distance_gpc=log_gain.distance_gpc,
        redshift=log_gain.redshift,
        native_parameters=log_gain.native_parameters,
        helicity_convention=(
            "positive_argument_gives_positive_stokes_v_in_callister_code"
        ),
        target_basis="sgwb_energy_density_hyperbolic_argument",
    )


def normalize_discrete_posterior(
    coordinates: list[float] | np.ndarray,
    density: list[float] | np.ndarray,
) -> dict[str, Any]:
    """Normalize a one-dimensional posterior grid by trapezoidal integration."""
    x = np.asarray(coordinates, dtype=float)
    y = np.asarray(density, dtype=float)
    blockers = []
    if x.ndim != 1 or y.ndim != 1 or x.shape != y.shape:
        blockers.append("posterior_grid_shape_mismatch")
    if x.size < 2:
        blockers.append("posterior_grid_too_short")
    if np.any(~np.isfinite(x)) or np.any(~np.isfinite(y)):
        blockers.append("posterior_grid_not_finite")
    if np.any(y < 0):
        blockers.append("posterior_density_negative")
    if not blockers and np.any(np.diff(x) <= 0):
        blockers.append("posterior_coordinates_not_strictly_increasing")
    norm = float(np.trapezoid(y, x)) if not blockers else 0.0
    if norm <= 0.0:
        blockers.append("posterior_norm_not_positive")
    normalized = y / norm if not blockers else np.zeros_like(y)
    normalized_norm = float(np.trapezoid(normalized, x)) if not blockers else 0.0
    return {
        "ready": not blockers,
        "norm": norm,
        "normalized_norm": normalized_norm,
        "coordinates": x.tolist(),
        "density": normalized.tolist(),
        "blockers": sorted(set(blockers)),
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
