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

CALLISTER_FIXED_RATE_HDF_FILENAMES = (
    "fixed_rate_uniform.hdf",
    "fixed_rate_SFR.hdf",
    "fixed_rate_delayedSFR.hdf",
    "fixed_rate_delayedSFR_HLO1.hdf",
    "fixed_rate_delayedSFR_HLO2.hdf",
    "fixed_rate_delayedSFR_HLO3.hdf",
    "fixed_rate_delayedSFR_HVO3.hdf",
    "fixed_rate_delayedSFR_LVO3.hdf",
)

CALLISTER_FIXED_RATE_HDF_KEYS = (
    "kappa_dcs_1D",
    "probability_kappa_dc_1D",
    "kappa_zs_1D",
    "probability_kappa_z_1D",
    "kappa_dcs_2D",
    "kappa_zs_2D",
    "probabilities",
)

CALLISTER_VARIABLE_EVOLUTION_HDF_FILENAME = "birefringence_variable_evolution.hdf"

CALLISTER_VARIABLE_EVOLUTION_HDF_KEYS = (
    "frequencies",
    "Omg_I_model",
    "Omg_V_model",
    "kappa_Dc",
    "kappa_z",
    "R0",
    "alpha",
    "beta",
    "zp",
    "zMax",
)

NG_GAUSSIAN_NPZ_FILENAME = "samples_Gaussian.npz"

NG_GAUSSIAN_NPZ_KEYS = (
    "chains",
    "log_prob",
    "local_accs",
    "global_accs",
)

NG_EVENT_LEVEL_FEATHER_FILENAME = "samples_posterior_birefringence.feather"

NG_EVENT_LEVEL_FEATHER_REQUIRED_COLUMNS = (
    "event",
    "kappa",
    "log_likelihood",
    "log_prior",
    "redshift",
    "comoving_distance",
)

GW_PARITY_PROJECTION_BLOCKERS = (
    "helicity_convention_not_harmonized_across_sources",
    "ppv_beta1_normalization_not_finalized",
    "engine_projection_out_of_scope",
)


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


def _array_from_dataset(value: Any) -> np.ndarray:
    try:
        value = value[()]
    except (AttributeError, TypeError, ValueError):
        pass
    return np.asarray(value, dtype=float)


def _prefixed_blockers(prefix: str, blockers: list[str]) -> list[str]:
    return [f"{prefix}_{blocker}" for blocker in blockers]


def _callister_result_group(datasets: dict[str, Any]) -> Any:
    if "result" in datasets and not all(
        key in datasets for key in CALLISTER_FIXED_RATE_HDF_KEYS
    ):
        return datasets["result"]
    return datasets


def normalize_callister_joint_posterior(
    kappa_d_coordinates: list[float] | np.ndarray,
    kappa_z_coordinates: list[float] | np.ndarray,
    density: list[list[float]] | np.ndarray,
) -> dict[str, Any]:
    """Normalize a Callister fixed-rate joint posterior grid.

    The public computation documents `probabilities[i,j]` as the posterior value
    at `kappa_dcs_2D[i]` and `kappa_zs_2D[j]`.
    """
    kappa_d = np.asarray(kappa_d_coordinates, dtype=float)
    kappa_z = np.asarray(kappa_z_coordinates, dtype=float)
    probability = np.asarray(density, dtype=float)
    blockers = []

    if kappa_d.ndim != 1 or kappa_z.ndim != 1:
        blockers.append("coordinates_not_one_dimensional")
    if probability.ndim != 2:
        blockers.append("probability_not_two_dimensional")
    expected_shape = (kappa_d.size, kappa_z.size)
    if probability.ndim == 2 and probability.shape != expected_shape:
        blockers.append("probability_shape_mismatch")
    if kappa_d.size < 2 or kappa_z.size < 2:
        blockers.append("grid_too_short")
    if (
        np.any(~np.isfinite(kappa_d))
        or np.any(~np.isfinite(kappa_z))
        or np.any(~np.isfinite(probability))
    ):
        blockers.append("grid_not_finite")
    if np.any(probability < 0):
        blockers.append("probability_negative")
    if not blockers and (
        np.any(np.diff(kappa_d) <= 0) or np.any(np.diff(kappa_z) <= 0)
    ):
        blockers.append("coordinates_not_strictly_increasing")

    norm = 0.0
    if not blockers:
        norm = float(np.trapezoid(np.trapezoid(probability, kappa_z, axis=1), kappa_d))
        if norm <= 0.0:
            blockers.append("norm_not_positive")

    normalized = probability / norm if not blockers else np.zeros_like(probability)
    normalized_norm = (
        float(np.trapezoid(np.trapezoid(normalized, kappa_z, axis=1), kappa_d))
        if not blockers
        else 0.0
    )
    return {
        "ready": not blockers,
        "norm": norm,
        "normalized_norm": normalized_norm,
        "kappa_d_coordinates": kappa_d.tolist(),
        "kappa_z_coordinates": kappa_z.tolist(),
        "density": normalized.tolist(),
        "shape": list(probability.shape),
        "blockers": sorted(set(blockers)),
    }


def histogram_posterior_from_samples(
    samples: list[float] | np.ndarray,
    *,
    bins: int = 80,
    value_range: tuple[float, float] | None = None,
) -> dict[str, Any]:
    """Convert one-dimensional posterior samples to a normalized histogram."""
    values = np.asarray(samples, dtype=float)
    blockers = []
    if values.ndim != 1:
        blockers.append("samples_not_one_dimensional")
    if values.size < 2:
        blockers.append("sample_count_too_small")
    if bins < 2:
        blockers.append("histogram_bins_too_small")
    if np.any(~np.isfinite(values)):
        blockers.append("samples_not_finite")
    if value_range is not None and value_range[0] >= value_range[1]:
        blockers.append("histogram_range_not_increasing")

    if blockers:
        return {
            "ready": False,
            "sample_count": int(values.size),
            "bins": int(bins),
            "coordinates": [],
            "density": [],
            "density_norm": 0.0,
            "peak_coordinate": None,
            "blockers": sorted(set(blockers)),
        }

    density, edges = np.histogram(
        values,
        bins=int(bins),
        range=value_range,
        density=True,
    )
    widths = np.diff(edges)
    centers = edges[:-1] + 0.5 * widths
    norm = float(np.sum(density * widths))
    peak_index = int(np.argmax(density))
    return {
        "ready": True,
        "sample_count": int(values.size),
        "bins": int(bins),
        "coordinates": centers.tolist(),
        "density": density.tolist(),
        "density_norm": norm,
        "peak_coordinate": float(centers[peak_index]),
        "blockers": [],
    }


def joint_histogram_posterior_from_samples(
    x_samples: list[float] | np.ndarray,
    y_samples: list[float] | np.ndarray,
    *,
    bins: tuple[int, int] = (80, 80),
    value_range: tuple[tuple[float, float], tuple[float, float]] | None = None,
) -> dict[str, Any]:
    """Convert two-dimensional posterior samples to a normalized histogram."""
    x_values = np.asarray(x_samples, dtype=float)
    y_values = np.asarray(y_samples, dtype=float)
    blockers = []
    if x_values.ndim != 1 or y_values.ndim != 1:
        blockers.append("samples_not_one_dimensional")
    if x_values.shape != y_values.shape:
        blockers.append("sample_shape_mismatch")
    if x_values.size < 2:
        blockers.append("sample_count_too_small")
    if len(bins) != 2 or bins[0] < 2 or bins[1] < 2:
        blockers.append("histogram_bins_too_small")
    if np.any(~np.isfinite(x_values)) or np.any(~np.isfinite(y_values)):
        blockers.append("samples_not_finite")
    if value_range is not None:
        x_range, y_range = value_range
        if x_range[0] >= x_range[1] or y_range[0] >= y_range[1]:
            blockers.append("histogram_range_not_increasing")

    if blockers:
        return {
            "ready": False,
            "sample_count": int(x_values.size),
            "bins": list(bins),
            "x_coordinates": [],
            "y_coordinates": [],
            "density": [],
            "density_norm": 0.0,
            "peak_x": None,
            "peak_y": None,
            "blockers": sorted(set(blockers)),
        }

    density, x_edges, y_edges = np.histogram2d(
        x_values,
        y_values,
        bins=bins,
        range=value_range,
        density=True,
    )
    x_widths = np.diff(x_edges)
    y_widths = np.diff(y_edges)
    x_centers = x_edges[:-1] + 0.5 * x_widths
    y_centers = y_edges[:-1] + 0.5 * y_widths
    norm = float(np.sum(density * x_widths[:, None] * y_widths[None, :]))
    peak = np.unravel_index(int(np.argmax(density)), density.shape)
    return {
        "ready": True,
        "sample_count": int(x_values.size),
        "bins": [int(bins[0]), int(bins[1])],
        "x_coordinates": x_centers.tolist(),
        "y_coordinates": y_centers.tolist(),
        "density": density.tolist(),
        "density_norm": norm,
        "peak_x": float(x_centers[peak[0]]),
        "peak_y": float(y_centers[peak[1]]),
        "blockers": [],
    }


def compare_one_dimensional_posteriors(
    reference_coordinates: list[float] | np.ndarray,
    reference_density: list[float] | np.ndarray,
    candidate_coordinates: list[float] | np.ndarray,
    candidate_density: list[float] | np.ndarray,
    *,
    comparison_points: int = 512,
) -> dict[str, Any]:
    """Compare two source-native one-dimensional posterior densities."""
    ref_x = np.asarray(reference_coordinates, dtype=float)
    ref_y = np.asarray(reference_density, dtype=float)
    cand_x = np.asarray(candidate_coordinates, dtype=float)
    cand_y = np.asarray(candidate_density, dtype=float)
    blockers = []

    if ref_x.ndim != 1 or ref_y.ndim != 1 or ref_x.shape != ref_y.shape:
        blockers.append("reference_grid_shape_mismatch")
    if cand_x.ndim != 1 or cand_y.ndim != 1 or cand_x.shape != cand_y.shape:
        blockers.append("candidate_grid_shape_mismatch")
    if ref_x.size < 2 or cand_x.size < 2:
        blockers.append("comparison_grid_too_short")
    if comparison_points < 2:
        blockers.append("comparison_points_too_small")
    if (
        np.any(~np.isfinite(ref_x))
        or np.any(~np.isfinite(ref_y))
        or np.any(~np.isfinite(cand_x))
        or np.any(~np.isfinite(cand_y))
    ):
        blockers.append("comparison_grid_not_finite")
    if np.any(ref_y < 0) or np.any(cand_y < 0):
        blockers.append("comparison_density_negative")
    if not blockers and (
        np.any(np.diff(ref_x) <= 0) or np.any(np.diff(cand_x) <= 0)
    ):
        blockers.append("comparison_coordinates_not_strictly_increasing")

    overlap_min = float(max(ref_x[0], cand_x[0])) if ref_x.size and cand_x.size else 0.0
    overlap_max = float(min(ref_x[-1], cand_x[-1])) if ref_x.size and cand_x.size else 0.0
    if overlap_min >= overlap_max:
        blockers.append("comparison_supports_do_not_overlap")

    if blockers:
        return {
            "ready": False,
            "comparison_points": int(comparison_points),
            "overlap_min": overlap_min,
            "overlap_max": overlap_max,
            "reference_peak_coordinate": None,
            "candidate_peak_coordinate": None,
            "peak_offset_candidate_minus_reference": None,
            "total_variation_distance": None,
            "hellinger_distance": None,
            "blockers": sorted(set(blockers)),
        }

    common_x = np.linspace(overlap_min, overlap_max, int(comparison_points))
    ref_common = np.interp(common_x, ref_x, ref_y)
    cand_common = np.interp(common_x, cand_x, cand_y)
    ref_normalized = normalize_discrete_posterior(common_x, ref_common)
    cand_normalized = normalize_discrete_posterior(common_x, cand_common)
    norm_blockers = []
    norm_blockers.extend(
        _prefixed_blockers("reference", ref_normalized["blockers"])
    )
    norm_blockers.extend(
        _prefixed_blockers("candidate", cand_normalized["blockers"])
    )
    if norm_blockers:
        return {
            "ready": False,
            "comparison_points": int(comparison_points),
            "overlap_min": overlap_min,
            "overlap_max": overlap_max,
            "reference_peak_coordinate": None,
            "candidate_peak_coordinate": None,
            "peak_offset_candidate_minus_reference": None,
            "total_variation_distance": None,
            "hellinger_distance": None,
            "blockers": sorted(set(norm_blockers)),
        }

    ref_density = np.asarray(ref_normalized["density"], dtype=float)
    cand_density = np.asarray(cand_normalized["density"], dtype=float)
    ref_peak = float(common_x[int(np.argmax(ref_density))])
    cand_peak = float(common_x[int(np.argmax(cand_density))])
    tv = 0.5 * float(np.trapezoid(np.abs(ref_density - cand_density), common_x))
    hellinger = math.sqrt(
        0.5
        * float(
            np.trapezoid(
                (np.sqrt(ref_density) - np.sqrt(cand_density)) ** 2,
                common_x,
            )
        )
    )
    return {
        "ready": True,
        "comparison_points": int(comparison_points),
        "overlap_min": overlap_min,
        "overlap_max": overlap_max,
        "reference_peak_coordinate": ref_peak,
        "candidate_peak_coordinate": cand_peak,
        "peak_offset_candidate_minus_reference": cand_peak - ref_peak,
        "total_variation_distance": tv,
        "hellinger_distance": hellinger,
        "blockers": [],
    }


def parse_callister_fixed_rate_hdf_datasets(
    datasets: dict[str, Any],
    *,
    source_file: str | None = None,
) -> dict[str, Any]:
    """Parse Callister fixed-rate posterior datasets from an HDF-like mapping."""
    result_group = _callister_result_group(datasets)
    missing_keys = [
        key for key in CALLISTER_FIXED_RATE_HDF_KEYS
        if key not in result_group
    ]
    if missing_keys:
        parser_blockers = ["missing_callister_fixed_rate_hdf_keys"]
        return {
            "schema": "callister_fixed_rate_hdf_v1",
            "source_file": source_file,
            "required_keys": list(CALLISTER_FIXED_RATE_HDF_KEYS),
            "missing_keys": missing_keys,
            "parser_ready": False,
            "parser_blockers": parser_blockers,
            "projection_blockers": list(GW_PARITY_PROJECTION_BLOCKERS),
            "blockers": sorted(
                set(parser_blockers + list(GW_PARITY_PROJECTION_BLOCKERS))
            ),
            "engine_projection_ready": False,
            "claimable_discriminator_now": False,
        }

    arrays = {
        key: _array_from_dataset(result_group[key])
        for key in CALLISTER_FIXED_RATE_HDF_KEYS
    }
    kappa_d_1d = normalize_discrete_posterior(
        arrays["kappa_dcs_1D"],
        arrays["probability_kappa_dc_1D"],
    )
    kappa_z_1d = normalize_discrete_posterior(
        arrays["kappa_zs_1D"],
        arrays["probability_kappa_z_1D"],
    )
    joint = normalize_callister_joint_posterior(
        arrays["kappa_dcs_2D"],
        arrays["kappa_zs_2D"],
        arrays["probabilities"],
    )
    parser_blockers = []
    parser_blockers.extend(_prefixed_blockers("kappa_d_1d", kappa_d_1d["blockers"]))
    parser_blockers.extend(_prefixed_blockers("kappa_z_1d", kappa_z_1d["blockers"]))
    parser_blockers.extend(_prefixed_blockers("joint", joint["blockers"]))

    parser_ready = not parser_blockers
    projection_blockers = list(GW_PARITY_PROJECTION_BLOCKERS)
    return {
        "schema": "callister_fixed_rate_hdf_v1",
        "source_file": source_file,
        "required_keys": list(CALLISTER_FIXED_RATE_HDF_KEYS),
        "missing_keys": [],
        "parser_ready": parser_ready,
        "parser_blockers": sorted(set(parser_blockers)),
        "projection_blockers": projection_blockers,
        "blockers": sorted(set(parser_blockers + projection_blockers)),
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
        "one_dimensional": {
            "kappa_D": kappa_d_1d,
            "kappa_z": kappa_z_1d,
        },
        "joint": joint,
    }


def load_callister_fixed_rate_hdf(path: str) -> dict[str, Any]:
    """Load a Callister fixed-rate HDF file when optional h5py is installed."""
    try:
        import h5py
    except ImportError:
        parser_blockers = ["h5py_not_installed"]
        return {
            "schema": "callister_fixed_rate_hdf_v1",
            "source_file": path,
            "required_keys": list(CALLISTER_FIXED_RATE_HDF_KEYS),
            "missing_keys": [],
            "parser_ready": False,
            "parser_blockers": parser_blockers,
            "projection_blockers": list(GW_PARITY_PROJECTION_BLOCKERS),
            "blockers": sorted(
                set(parser_blockers + list(GW_PARITY_PROJECTION_BLOCKERS))
            ),
            "engine_projection_ready": False,
            "claimable_discriminator_now": False,
        }

    with h5py.File(path, "r") as hdf:
        return parse_callister_fixed_rate_hdf_datasets(hdf, source_file=path)


def _sample_summary(values: np.ndarray) -> dict[str, float]:
    return {
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
    }


def _sample_quantile_summary(values: np.ndarray) -> dict[str, float]:
    return {
        **_sample_summary(values),
        "p05": float(np.percentile(values, 5)),
        "p50": float(np.percentile(values, 50)),
        "p95": float(np.percentile(values, 95)),
    }


def parse_callister_variable_evolution_hdf_datasets(
    datasets: dict[str, Any],
    *,
    source_file: str | None = None,
) -> dict[str, Any]:
    """Parse Callister variable-rate posterior samples from an HDF-like mapping."""
    result_group = _callister_result_group(datasets)
    missing_keys = [
        key for key in CALLISTER_VARIABLE_EVOLUTION_HDF_KEYS
        if key not in result_group
    ]
    if missing_keys:
        parser_blockers = ["missing_callister_variable_evolution_hdf_keys"]
        return {
            "schema": "callister_variable_evolution_hdf_v1",
            "source_file": source_file,
            "required_keys": list(CALLISTER_VARIABLE_EVOLUTION_HDF_KEYS),
            "missing_keys": missing_keys,
            "parser_ready": False,
            "parser_blockers": parser_blockers,
            "projection_blockers": list(GW_PARITY_PROJECTION_BLOCKERS),
            "blockers": sorted(
                set(parser_blockers + list(GW_PARITY_PROJECTION_BLOCKERS))
            ),
            "engine_projection_ready": False,
            "claimable_discriminator_now": False,
        }

    arrays = {
        key: _array_from_dataset(result_group[key])
        for key in CALLISTER_VARIABLE_EVOLUTION_HDF_KEYS
    }
    frequencies = arrays["frequencies"]
    omg_i = arrays["Omg_I_model"]
    omg_v = arrays["Omg_V_model"]
    sample_keys = ("kappa_Dc", "kappa_z", "R0", "alpha", "beta", "zp", "zMax")
    sample_arrays = {key: arrays[key] for key in sample_keys}
    blockers = []

    if frequencies.ndim != 1:
        blockers.append("frequencies_not_one_dimensional")
    elif frequencies.size < 2:
        blockers.append("frequency_grid_too_short")
    elif np.any(np.diff(frequencies) <= 0):
        blockers.append("frequencies_not_strictly_increasing")
    if omg_i.ndim != 2 or omg_v.ndim != 2:
        blockers.append("spectra_not_two_dimensional")

    sample_lengths = {}
    for key, values in sample_arrays.items():
        if values.ndim != 1:
            blockers.append(f"{key}_not_one_dimensional")
        sample_lengths[key] = int(values.size)
    unique_sample_lengths = set(sample_lengths.values())
    sample_count = unique_sample_lengths.pop() if len(unique_sample_lengths) == 1 else 0
    if sample_count < 1:
        blockers.append("sample_count_not_positive_or_consistent")

    expected_shape = (frequencies.size, sample_count)
    if omg_i.ndim == 2 and sample_count and omg_i.shape != expected_shape:
        blockers.append("Omg_I_model_shape_mismatch")
    if omg_v.ndim == 2 and sample_count and omg_v.shape != expected_shape:
        blockers.append("Omg_V_model_shape_mismatch")
    if np.any(~np.isfinite(frequencies)):
        blockers.append("frequencies_not_finite")
    if np.any(~np.isfinite(omg_i)) or np.any(~np.isfinite(omg_v)):
        blockers.append("spectra_not_finite")
    for key, values in sample_arrays.items():
        if np.any(~np.isfinite(values)):
            blockers.append(f"{key}_not_finite")
    if not blockers and np.any(frequencies <= 0):
        blockers.append("frequencies_not_positive")
    for key in ("R0", "zp", "zMax"):
        values = sample_arrays[key]
        if values.ndim == 1 and np.any(values <= 0):
            blockers.append(f"{key}_not_positive")

    parser_ready = not blockers
    projection_blockers = list(GW_PARITY_PROJECTION_BLOCKERS)
    parameter_summaries = (
        {
            key: _sample_summary(values)
            for key, values in sample_arrays.items()
        }
        if parser_ready
        else {}
    )
    spectra_summary = (
        {
            "frequencies": {
                "count": int(frequencies.size),
                "min_hz": float(frequencies[0]),
                "max_hz": float(frequencies[-1]),
            },
            "Omg_I_model": {
                "shape": list(omg_i.shape),
                **_sample_summary(omg_i),
            },
            "Omg_V_model": {
                "shape": list(omg_v.shape),
                **_sample_summary(omg_v),
            },
        }
        if parser_ready
        else {}
    )
    return {
        "schema": "callister_variable_evolution_hdf_v1",
        "source_file": source_file,
        "required_keys": list(CALLISTER_VARIABLE_EVOLUTION_HDF_KEYS),
        "missing_keys": [],
        "parser_ready": parser_ready,
        "parser_blockers": sorted(set(blockers)),
        "projection_blockers": projection_blockers,
        "blockers": sorted(set(blockers + projection_blockers)),
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
        "sample_count": int(sample_count),
        "sample_lengths": sample_lengths,
        "parameter_summaries": parameter_summaries,
        "spectra_summary": spectra_summary,
    }


def load_callister_variable_evolution_hdf(path: str) -> dict[str, Any]:
    """Load the Callister variable-evolution HDF file when h5py is installed."""
    try:
        import h5py
    except ImportError:
        parser_blockers = ["h5py_not_installed"]
        return {
            "schema": "callister_variable_evolution_hdf_v1",
            "source_file": path,
            "required_keys": list(CALLISTER_VARIABLE_EVOLUTION_HDF_KEYS),
            "missing_keys": [],
            "parser_ready": False,
            "parser_blockers": parser_blockers,
            "projection_blockers": list(GW_PARITY_PROJECTION_BLOCKERS),
            "blockers": sorted(
                set(parser_blockers + list(GW_PARITY_PROJECTION_BLOCKERS))
            ),
            "engine_projection_ready": False,
            "claimable_discriminator_now": False,
        }

    with h5py.File(path, "r") as hdf:
        return parse_callister_variable_evolution_hdf_datasets(hdf, source_file=path)


def parse_ng_gaussian_hyperposterior_npz_datasets(
    datasets: dict[str, Any],
    *,
    source_file: str | None = None,
) -> dict[str, Any]:
    """Parse Ng et al. Gaussian hyperposterior samples from an NPZ-like mapping."""
    missing_keys = [key for key in NG_GAUSSIAN_NPZ_KEYS if key not in datasets]
    if missing_keys:
        parser_blockers = ["missing_ng_gaussian_npz_keys"]
        return {
            "schema": "ng_gaussian_hyperposterior_npz_v1",
            "source_file": source_file,
            "required_keys": list(NG_GAUSSIAN_NPZ_KEYS),
            "missing_keys": missing_keys,
            "parser_ready": False,
            "parser_blockers": parser_blockers,
            "projection_blockers": list(GW_PARITY_PROJECTION_BLOCKERS),
            "blockers": sorted(
                set(parser_blockers + list(GW_PARITY_PROJECTION_BLOCKERS))
            ),
            "engine_projection_ready": False,
            "claimable_discriminator_now": False,
        }

    arrays = {key: _array_from_dataset(datasets[key]) for key in NG_GAUSSIAN_NPZ_KEYS}
    chains = arrays["chains"]
    log_prob = arrays["log_prob"]
    local_accs = arrays["local_accs"]
    global_accs = arrays["global_accs"]
    blockers = []

    if chains.ndim != 3:
        blockers.append("chains_not_three_dimensional")
        step_count = 0
        walker_count = 0
        parameter_count = 0
    else:
        step_count = int(chains.shape[0])
        walker_count = int(chains.shape[1])
        parameter_count = int(chains.shape[2])
        if parameter_count != 2:
            blockers.append("chains_last_dimension_not_mu_sigma")
        if step_count < 1 or walker_count < 1:
            blockers.append("chains_empty")

    if log_prob.ndim != 2:
        blockers.append("log_prob_not_two_dimensional")
    elif chains.ndim == 3 and log_prob.shape != chains.shape[:2]:
        blockers.append("log_prob_shape_mismatch")

    for key, values in (("local_accs", local_accs), ("global_accs", global_accs)):
        if values.ndim != 2:
            blockers.append(f"{key}_not_two_dimensional")
        elif chains.ndim == 3 and values.shape[0] != step_count:
            blockers.append(f"{key}_step_count_mismatch")

    for key, values in arrays.items():
        if np.any(~np.isfinite(values)):
            blockers.append(f"{key}_not_finite")
    if chains.ndim == 3 and parameter_count == 2:
        sigma = chains[:, :, 1]
        if np.any(sigma < 0):
            blockers.append("sigma_samples_negative")

    parser_ready = not blockers
    projection_blockers = list(GW_PARITY_PROJECTION_BLOCKERS)
    parameter_summaries = {}
    if parser_ready:
        flat = chains.reshape(-1, 2)
        parameter_summaries = {
            "mu": _sample_quantile_summary(flat[:, 0]),
            "sigma": _sample_quantile_summary(flat[:, 1]),
        }

    return {
        "schema": "ng_gaussian_hyperposterior_npz_v1",
        "source_file": source_file,
        "required_keys": list(NG_GAUSSIAN_NPZ_KEYS),
        "missing_keys": [],
        "parser_ready": parser_ready,
        "parser_blockers": sorted(set(blockers)),
        "projection_blockers": projection_blockers,
        "blockers": sorted(set(blockers + projection_blockers)),
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
        "chain_shape": list(chains.shape),
        "log_prob_shape": list(log_prob.shape),
        "local_accs_shape": list(local_accs.shape),
        "global_accs_shape": list(global_accs.shape),
        "step_count": step_count,
        "walker_count": walker_count,
        "parameter_count": parameter_count,
        "sample_count": int(step_count * walker_count),
        "parameter_names": ["mu", "sigma"],
        "parameter_summaries": parameter_summaries,
        "log_prob_summary": _sample_summary(log_prob) if parser_ready else {},
        "acceptance_summary": (
            {
                "local_accs": _sample_summary(local_accs),
                "global_accs": _sample_summary(global_accs),
            }
            if parser_ready
            else {}
        ),
    }


def load_ng_gaussian_hyperposterior_npz(path: str) -> dict[str, Any]:
    """Load the Ng et al. Gaussian hyperposterior NPZ file."""
    with np.load(path) as data:
        return parse_ng_gaussian_hyperposterior_npz_datasets(
            data,
            source_file=path,
        )


def _table_column_to_float_array(table: Any, column: str) -> np.ndarray:
    return np.asarray(table[column].to_numpy(zero_copy_only=False), dtype=float)


def parse_ng_event_level_feather_table(
    table: Any,
    *,
    source_file: str | None = None,
) -> dict[str, Any]:
    """Parse Ng et al. event-level birefringence posterior Feather data."""
    column_names = list(table.column_names)
    missing_columns = [
        column
        for column in NG_EVENT_LEVEL_FEATHER_REQUIRED_COLUMNS
        if column not in column_names
    ]
    row_count = int(table.num_rows)
    column_count = int(table.num_columns)
    projection_blockers = list(GW_PARITY_PROJECTION_BLOCKERS)

    if missing_columns:
        parser_blockers = ["missing_ng_event_level_feather_columns"]
        return {
            "schema": "ng_event_level_feather_v1",
            "source_file": source_file,
            "required_columns": list(NG_EVENT_LEVEL_FEATHER_REQUIRED_COLUMNS),
            "missing_columns": missing_columns,
            "parser_ready": False,
            "parser_blockers": parser_blockers,
            "projection_blockers": projection_blockers,
            "blockers": sorted(set(parser_blockers + projection_blockers)),
            "engine_projection_ready": False,
            "claimable_discriminator_now": False,
            "row_count": row_count,
            "column_count": column_count,
        }

    blockers = []
    if row_count < 1:
        blockers.append("event_level_table_empty")

    null_counts = {
        column: int(table[column].null_count)
        for column in NG_EVENT_LEVEL_FEATHER_REQUIRED_COLUMNS
    }
    for column, null_count in null_counts.items():
        if null_count:
            blockers.append(f"{column}_contains_nulls")

    numeric_arrays = {}
    if not blockers:
        for column in (
            "kappa",
            "log_likelihood",
            "log_prior",
            "redshift",
            "comoving_distance",
        ):
            values = _table_column_to_float_array(table, column)
            numeric_arrays[column] = values
            if values.ndim != 1:
                blockers.append(f"{column}_not_one_dimensional")
            elif values.size != row_count:
                blockers.append(f"{column}_row_count_mismatch")
            if np.any(~np.isfinite(values)):
                blockers.append(f"{column}_not_finite")

    events = np.asarray([], dtype=str)
    if not blockers:
        events = np.asarray(table["event"].to_pylist(), dtype=str)
        if events.ndim != 1 or events.size != row_count:
            blockers.append("event_row_count_mismatch")
        if np.any(events == ""):
            blockers.append("event_empty")
        if np.any(numeric_arrays["redshift"] < 0.0):
            blockers.append("redshift_negative")
        if np.any(numeric_arrays["comoving_distance"] < 0.0):
            blockers.append("comoving_distance_negative")

    parser_ready = not blockers
    event_count = 0
    event_sample_count_min = 0
    event_sample_count_max = 0
    event_counts_preview: list[dict[str, Any]] = []
    numeric_summaries: dict[str, dict[str, float]] = {}
    if parser_ready:
        event_names, event_counts = np.unique(events, return_counts=True)
        event_count = int(event_names.size)
        event_sample_count_min = int(np.min(event_counts))
        event_sample_count_max = int(np.max(event_counts))
        event_counts_preview = [
            {"event": str(event), "sample_count": int(count)}
            for event, count in zip(event_names[:5], event_counts[:5], strict=True)
        ]
        numeric_summaries = {
            column: _sample_quantile_summary(values)
            for column, values in numeric_arrays.items()
        }

    parser_blockers = sorted(set(blockers))
    return {
        "schema": "ng_event_level_feather_v1",
        "source_file": source_file,
        "required_columns": list(NG_EVENT_LEVEL_FEATHER_REQUIRED_COLUMNS),
        "missing_columns": [],
        "parser_ready": parser_ready,
        "parser_blockers": parser_blockers,
        "projection_blockers": projection_blockers,
        "blockers": sorted(set(parser_blockers + projection_blockers)),
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
        "row_count": row_count,
        "column_count": column_count,
        "null_counts": null_counts,
        "event_count": event_count,
        "event_sample_count_min": event_sample_count_min,
        "event_sample_count_max": event_sample_count_max,
        "event_counts_preview": event_counts_preview,
        "numeric_summaries": numeric_summaries,
        "restricted_global_kappa_likelihood_ready": False,
    }


def load_ng_event_level_feather(path: str) -> dict[str, Any]:
    """Load the Ng et al. event-level posterior Feather file."""
    try:
        import pyarrow.feather as feather
    except ImportError:
        parser_blockers = ["pyarrow_not_installed"]
        projection_blockers = list(GW_PARITY_PROJECTION_BLOCKERS)
        return {
            "schema": "ng_event_level_feather_v1",
            "source_file": path,
            "required_columns": list(NG_EVENT_LEVEL_FEATHER_REQUIRED_COLUMNS),
            "missing_columns": [],
            "parser_ready": False,
            "parser_blockers": parser_blockers,
            "projection_blockers": projection_blockers,
            "blockers": sorted(set(parser_blockers + projection_blockers)),
            "engine_projection_ready": False,
            "claimable_discriminator_now": False,
        }

    table = feather.read_table(path, memory_map=True)
    return parse_ng_event_level_feather_table(table, source_file=path)


def restricted_global_kappa_likelihood_from_event_samples(
    events: list[str] | np.ndarray,
    kappa_samples: list[float] | np.ndarray,
    *,
    grid_min: float = -0.1,
    grid_max: float = 0.1,
    grid_size: int = 1000,
    source_file: str | None = None,
) -> dict[str, Any]:
    """Reproduce Ng et al. restricted global-kappa KDE product."""
    event_values = np.asarray(events, dtype=str)
    kappa_values = np.asarray(kappa_samples, dtype=float)
    blockers = []
    projection_blockers = list(GW_PARITY_PROJECTION_BLOCKERS)

    if event_values.ndim != 1 or kappa_values.ndim != 1:
        blockers.append("samples_not_one_dimensional")
    elif event_values.shape != kappa_values.shape:
        blockers.append("event_kappa_shape_mismatch")
    if kappa_values.size < 2:
        blockers.append("sample_count_too_small")
    if np.any(event_values == ""):
        blockers.append("event_empty")
    if np.any(~np.isfinite(kappa_values)):
        blockers.append("kappa_not_finite")
    if grid_size < 10:
        blockers.append("grid_size_too_small")
    if not np.isfinite(grid_min) or not np.isfinite(grid_max):
        blockers.append("grid_bounds_not_finite")
    elif grid_min >= grid_max:
        blockers.append("grid_bounds_not_increasing")

    event_names = np.array([], dtype=str)
    event_counts = np.array([], dtype=int)
    if not blockers:
        event_names, event_counts = np.unique(event_values, return_counts=True)
        if event_names.size < 2:
            blockers.append("event_count_too_small")
        if np.any(event_counts < 2):
            blockers.append("event_sample_count_too_small")

    if blockers:
        parser_blockers = sorted(set(blockers))
        return {
            "schema": "ng_restricted_global_kappa_likelihood_v1",
            "source_file": source_file,
            "ready": False,
            "parser_ready": False,
            "parser_blockers": parser_blockers,
            "projection_blockers": projection_blockers,
            "blockers": sorted(set(parser_blockers + projection_blockers)),
            "engine_projection_ready": False,
            "claimable_discriminator_now": False,
        }

    try:
        from scipy.stats import gaussian_kde
    except ImportError:
        parser_blockers = ["scipy_not_installed"]
        return {
            "schema": "ng_restricted_global_kappa_likelihood_v1",
            "source_file": source_file,
            "ready": False,
            "parser_ready": False,
            "parser_blockers": parser_blockers,
            "projection_blockers": projection_blockers,
            "blockers": sorted(set(parser_blockers + projection_blockers)),
            "engine_projection_ready": False,
            "claimable_discriminator_now": False,
        }

    grid = np.linspace(float(grid_min), float(grid_max), int(grid_size))
    log_likelihood = np.zeros_like(grid)
    kde_blockers = []
    for event in event_names:
        samples = kappa_values[event_values == event]
        try:
            density = gaussian_kde(samples)(grid)
        except (ValueError, np.linalg.LinAlgError):
            kde_blockers.append(f"{event}_kde_failed")
            continue
        if np.any(~np.isfinite(density)) or np.any(density <= 0.0):
            kde_blockers.append(f"{event}_kde_density_invalid")
            continue
        log_likelihood += np.log(density)

    if kde_blockers:
        parser_blockers = sorted(set(kde_blockers))
        return {
            "schema": "ng_restricted_global_kappa_likelihood_v1",
            "source_file": source_file,
            "ready": False,
            "parser_ready": False,
            "parser_blockers": parser_blockers,
            "projection_blockers": projection_blockers,
            "blockers": sorted(set(parser_blockers + projection_blockers)),
            "engine_projection_ready": False,
            "claimable_discriminator_now": False,
        }

    log_likelihood = log_likelihood - float(np.max(log_likelihood))
    likelihood = np.exp(log_likelihood)
    density_norm = float(np.trapezoid(likelihood, x=grid))
    if density_norm <= 0.0 or not np.isfinite(density_norm):
        parser_blockers = ["restricted_likelihood_norm_invalid"]
        return {
            "schema": "ng_restricted_global_kappa_likelihood_v1",
            "source_file": source_file,
            "ready": False,
            "parser_ready": False,
            "parser_blockers": parser_blockers,
            "projection_blockers": projection_blockers,
            "blockers": sorted(set(parser_blockers + projection_blockers)),
            "engine_projection_ready": False,
            "claimable_discriminator_now": False,
        }
    likelihood = likelihood / density_norm

    restricted_cdf = np.array(
        [
            np.trapezoid(likelihood[0:index], x=grid[0:index])
            for index in range(len(grid))
        ]
    )
    kappa_5 = float(np.interp(0.05, restricted_cdf, grid))
    kappa_50 = float(np.interp(0.50, restricted_cdf, grid))
    kappa_95 = float(np.interp(0.95, restricted_cdf, grid))
    zero_density = float(np.interp(0.0, grid, likelihood))
    credible_level_at_zero = float(np.mean(likelihood > zero_density))

    midpoint = len(grid) // 2
    absolute_grid = grid[midpoint:]
    absolute_likelihood = likelihood[midpoint:].copy()
    if len(grid) % 2 == 0:
        absolute_likelihood = absolute_likelihood + likelihood[:midpoint][::-1]
    else:
        absolute_likelihood[1:] = (
            absolute_likelihood[1:] + likelihood[:midpoint][::-1]
        )
    absolute_cdf = np.array(
        [
            np.trapezoid(absolute_likelihood[0:index], x=absolute_grid[0:index])
            for index in range(len(absolute_grid))
        ]
    )
    absolute_kappa_68 = float(np.interp(0.68, absolute_cdf, absolute_grid))
    absolute_kappa_90 = float(np.interp(0.90, absolute_cdf, absolute_grid))

    return {
        "schema": "ng_restricted_global_kappa_likelihood_v1",
        "source_file": source_file,
        "ready": True,
        "parser_ready": True,
        "parser_blockers": [],
        "projection_blockers": projection_blockers,
        "blockers": projection_blockers,
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
        "sample_count": int(kappa_values.size),
        "event_count": int(event_names.size),
        "event_sample_count_min": int(np.min(event_counts)),
        "event_sample_count_max": int(np.max(event_counts)),
        "event_counts_preview": [
            {"event": str(event), "sample_count": int(count)}
            for event, count in zip(event_names[:5], event_counts[:5], strict=True)
        ],
        "grid_min": float(grid[0]),
        "grid_max": float(grid[-1]),
        "grid_size": int(grid.size),
        "density_norm": float(np.trapezoid(likelihood, x=grid)),
        "maximum_likelihood_kappa": float(grid[int(np.argmax(likelihood))]),
        "restricted_kappa_5": kappa_5,
        "restricted_kappa_median": kappa_50,
        "restricted_kappa_95": kappa_95,
        "restricted_kappa_plus_90": float(kappa_95 - kappa_50),
        "restricted_kappa_minus_90": float(kappa_50 - kappa_5),
        "credible_level_at_zero": credible_level_at_zero,
        "absolute_kappa_68": absolute_kappa_68,
        "absolute_kappa_90": absolute_kappa_90,
        "source_algorithm": (
            "Gaussian KDE per event, sum log densities on a uniform kappa grid, "
            "normalize by trapezoidal integration, then interpolate source-style "
            "CDF quantiles."
        ),
    }


def load_ng_restricted_global_kappa_likelihood_from_feather(
    path: str,
    *,
    grid_min: float = -0.1,
    grid_max: float = 0.1,
    grid_size: int = 1000,
) -> dict[str, Any]:
    """Load Ng event-level samples and reproduce the restricted kappa likelihood."""
    try:
        import pyarrow.feather as feather
    except ImportError:
        parser_blockers = ["pyarrow_not_installed"]
        projection_blockers = list(GW_PARITY_PROJECTION_BLOCKERS)
        return {
            "schema": "ng_restricted_global_kappa_likelihood_v1",
            "source_file": path,
            "ready": False,
            "parser_ready": False,
            "parser_blockers": parser_blockers,
            "projection_blockers": projection_blockers,
            "blockers": sorted(set(parser_blockers + projection_blockers)),
            "engine_projection_ready": False,
            "claimable_discriminator_now": False,
        }

    table = feather.read_table(path, columns=["event", "kappa"], memory_map=True)
    return restricted_global_kappa_likelihood_from_event_samples(
        table["event"].to_pylist(),
        table["kappa"].to_numpy(zero_copy_only=False),
        grid_min=grid_min,
        grid_max=grid_max,
        grid_size=grid_size,
        source_file=path,
    )


def build_ng_ppv_beta10_candidate_packet(
    restricted_likelihood: dict[str, Any],
) -> dict[str, Any]:
    """Wrap a reproduced Ng kappa likelihood as a non-promoting PPV candidate."""
    projection_blockers = list(GW_PARITY_PROJECTION_BLOCKERS)
    required_fields = (
        "schema",
        "ready",
        "restricted_kappa_5",
        "restricted_kappa_median",
        "restricted_kappa_95",
        "restricted_kappa_plus_90",
        "restricted_kappa_minus_90",
    )
    missing_fields = [
        field
        for field in required_fields
        if field not in restricted_likelihood
    ]
    blockers = []
    if missing_fields:
        blockers.append("missing_restricted_likelihood_fields")
    if restricted_likelihood.get("schema") != "ng_restricted_global_kappa_likelihood_v1":
        blockers.append("restricted_likelihood_schema_mismatch")
    if restricted_likelihood.get("ready") is not True:
        blockers.append("restricted_likelihood_not_ready")

    if blockers:
        parser_blockers = sorted(set(blockers))
        return {
            "schema": "ng_ppv_beta10_candidate_packet_v1",
            "candidate_ready": False,
            "parser_ready": False,
            "parser_blockers": parser_blockers,
            "missing_fields": missing_fields,
            "projection_blockers": projection_blockers,
            "blockers": sorted(set(parser_blockers + projection_blockers)),
            "engine_projection_ready": False,
            "claimable_discriminator_now": False,
        }

    source_to_ppv_blockers = [
        "engine_canonical_helicity_sign_missing",
        "source_declared_beta10_not_engine_axis",
        "dimensionless_ppv_beta10_normalization_missing",
        *projection_blockers,
    ]
    return {
        "schema": "ng_ppv_beta10_candidate_packet_v1",
        "candidate_ready": True,
        "parser_ready": True,
        "parser_blockers": [],
        "source_parameter": "ng_kappa_Gpc_inv_at_100Hz",
        "target_ppv_parameter": "beta_1_0_amplitude_branch",
        "source_declared_mapping_ready": True,
        "source_native_likelihood_ready": True,
        "ppv_beta10_candidate_likelihood_ready": True,
        "canonical_engine_beta10_ready": False,
        "frequency_reference_hz": 100.0,
        "distance_factor": "D_C_Gpc",
        "candidate_formula": (
            "delta_phi_A = kappa_Gpc_inv * D_C_Gpc * (f_hz / 100)"
        ),
        "candidate_coefficient_units": "Gpc^-1",
        "candidate_coefficient_basis": (
            "source_native_attenuation_coefficient_not_dimensionless_engine_beta"
        ),
        "source_native_constraint": {
            "kappa_Gpc_inv_5": restricted_likelihood["restricted_kappa_5"],
            "kappa_Gpc_inv_median": (
                restricted_likelihood["restricted_kappa_median"]
            ),
            "kappa_Gpc_inv_95": restricted_likelihood["restricted_kappa_95"],
            "kappa_Gpc_inv_plus_90": (
                restricted_likelihood["restricted_kappa_plus_90"]
            ),
            "kappa_Gpc_inv_minus_90": (
                restricted_likelihood["restricted_kappa_minus_90"]
            ),
        },
        "sign_conventions": {
            "ng": "positive_kappa_enhances_left_handed_polarization",
            "jenks_ppv": "lambda_R_plus_1_lambda_L_minus_1",
            "candidate_sign_status": "source_declared_noncanonical",
            "engine_canonical_sign": None,
        },
        "readiness": {
            "source_declared_ppv_mapping_ready": True,
            "source_native_likelihood_ready": True,
            "helicity_harmonization_ready": False,
            "dimensionless_ppv_normalization_ready": False,
            "engine_projection_ready": False,
            "claim_ready": False,
        },
        "projection_blockers": projection_blockers,
        "blockers": sorted(set(source_to_ppv_blockers)),
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
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
