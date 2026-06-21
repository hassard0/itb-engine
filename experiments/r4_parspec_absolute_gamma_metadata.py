"""Absolute ParSpec gamma metadata for the qEFT source events."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_parspec_published_bound_surrogate import (
    DEFAULT_OUT as DEFAULT_V2196_PATH,
)
from experiments.r4_parspec_qeft_source_asset_audit import QEFT_POWER
from experiments.r4_parspec_qnm_deformation_jacobian import (
    DEFAULT_OUT as DEFAULT_V2197_PATH,
)
from experiments.r4_parspec_ringdown_source_bridge import SOURCE_EVENTS, load_json


VERSION = "v2.199"
DEFAULT_OUT = Path(
    "experiments/results/v2.199/r4_parspec_absolute_gamma_metadata.json"
)
SOLAR_MASS_GEOMETRIC_RADIUS_KM = 1.4766250385
SOURCE_AXIS = "ell_qEFT_km"

GWOSC_PARAMETER_SNAPSHOT: dict[str, dict[str, Any]] = {
    "GW150914": {
        "event_version": "GW150914-v3",
        "parameter_endpoint": (
            "https://gwosc.org/api/v2/event-versions/GW150914-v3/parameters"
        ),
        "selected_pe_record": "gwtc1_pe_GW150914",
        "pipeline": "lalinference",
        "waveform_family": "Overall_posterior",
        "is_preferred": True,
        "data_url": (
            "https://dcc.ligo.org/public/0157/P1800370/005/"
            "GW150914_GWTC-1.hdf5"
        ),
        "posterior_sample_reference": "https://dcc.ligo.org/LIGO-P1800370/public",
        "parameters": {
            "final_mass_source": {
                "unit": "M_sun",
                "best": 63.1,
                "upper_error": 3.4,
                "lower_error": -3.0,
            },
            "redshift": {
                "unit": "",
                "best": 0.09,
                "upper_error": 0.03,
                "lower_error": -0.03,
            },
            "luminosity_distance": {
                "unit": "Mpc",
                "best": 440.0,
                "upper_error": 150.0,
                "lower_error": -170.0,
            },
        },
    },
    "GW200129": {
        "event_version": "GW200129_065458-v1",
        "parameter_endpoint": (
            "https://gwosc.org/api/v2/event-versions/"
            "GW200129_065458-v1/parameters"
        ),
        "selected_pe_record": "GWTC-3-confident_GW200129_065458_R2_pe_combined",
        "pipeline": "bilby",
        "waveform_family": "C01:Mixed",
        "is_preferred": True,
        "data_url": (
            "https://zenodo.org/api/records/8177023/files/"
            "IGWN-GWTC3p0-v2-GW200129_065458_PEDataRelease_mixed_cosmo.h5/"
            "content"
        ),
        "posterior_sample_reference": "https://doi.org/10.5281/zenodo.5546662",
        "parameters": {
            "final_mass_source": {
                "unit": "M_sun",
                "best": 60.2,
                "upper_error": 4.1,
                "lower_error": -3.2,
            },
            "redshift": {
                "unit": "",
                "best": 0.18,
                "upper_error": 0.05,
                "lower_error": -0.07,
            },
            "luminosity_distance": {
                "unit": "Mpc",
                "best": 890.0,
                "upper_error": 260.0,
                "lower_error": -370.0,
            },
            "final_spin": {
                "unit": "",
                "best": 0.73,
                "upper_error": 0.06,
                "lower_error": -0.05,
            },
            "total_mass_source": {
                "unit": "M_sun",
                "best": 63.3,
                "upper_error": 4.5,
                "lower_error": -3.4,
            },
        },
    },
}


def _parameter_value(
    snapshot: dict[str, Any],
    name: str,
) -> dict[str, float | str]:
    params = snapshot["parameters"]
    if name not in params:
        raise KeyError(f"{name} missing from parameter snapshot")
    return params[name]


def _value_with_bounds(parameter: dict[str, float | str]) -> dict[str, float]:
    best = float(parameter["best"])
    lower = best + float(parameter["lower_error"])
    upper = best + float(parameter["upper_error"])
    return {"best": best, "lower": lower, "upper": upper}


def absolute_gamma_ratio(
    ell_qeft_km: float,
    *,
    final_mass_source_solar: float,
    redshift: float,
) -> float:
    if ell_qeft_km <= 0.0:
        raise ValueError("ell_qeft_km must be positive")
    if final_mass_source_solar <= 0.0:
        raise ValueError("final_mass_source_solar must be positive")
    if redshift < 0.0:
        raise ValueError("redshift must be nonnegative")
    denominator_km = final_mass_source_solar * SOLAR_MASS_GEOMETRIC_RADIUS_KM
    return ell_qeft_km * (1.0 + redshift) / denominator_km


def absolute_gamma(
    ell_qeft_km: float,
    *,
    final_mass_source_solar: float,
    redshift: float,
) -> float:
    return absolute_gamma_ratio(
        ell_qeft_km,
        final_mass_source_solar=final_mass_source_solar,
        redshift=redshift,
    ) ** QEFT_POWER


def absolute_gamma_metadata_range(
    ell_qeft_km: float,
    *,
    final_mass_source: dict[str, float],
    redshift: dict[str, float],
) -> dict[str, float]:
    lower_ratio = absolute_gamma_ratio(
        ell_qeft_km,
        final_mass_source_solar=final_mass_source["upper"],
        redshift=redshift["lower"],
    )
    upper_ratio = absolute_gamma_ratio(
        ell_qeft_km,
        final_mass_source_solar=final_mass_source["lower"],
        redshift=redshift["upper"],
    )
    return {
        "lower": lower_ratio**QEFT_POWER,
        "upper": upper_ratio**QEFT_POWER,
    }


def _surrogate_by_label(v2196: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        row["label"]: row
        for row in v2196["published_bound_surrogate"]["surrogates"]
    }


def _qnm_coefficients(v2197: dict[str, Any]) -> dict[str, float]:
    return v2197["qnm_deformation_jacobian"]["qnm_coefficient_vector"]


def absolute_gamma_row(
    label: str,
    *,
    ell_qeft_km: float,
    snapshot: dict[str, Any],
    qnm_coefficients: dict[str, float],
) -> dict[str, Any]:
    final_mass = _value_with_bounds(
        _parameter_value(snapshot, "final_mass_source")
    )
    redshift = _value_with_bounds(_parameter_value(snapshot, "redshift"))
    gamma = absolute_gamma(
        ell_qeft_km,
        final_mass_source_solar=final_mass["best"],
        redshift=redshift["best"],
    )
    ratio = absolute_gamma_ratio(
        ell_qeft_km,
        final_mass_source_solar=final_mass["best"],
        redshift=redshift["best"],
    )
    gamma_range = absolute_gamma_metadata_range(
        ell_qeft_km,
        final_mass_source=final_mass,
        redshift=redshift,
    )
    return canonicalize_json_floats({
        "label": label,
        "event_version": snapshot["event_version"],
        "selected_pe_record": snapshot["selected_pe_record"],
        "parameter_endpoint": snapshot["parameter_endpoint"],
        "source_axis": SOURCE_AXIS,
        "ell_qEFT_km": ell_qeft_km,
        "final_mass_source_solar": final_mass,
        "redshift": redshift,
        "luminosity_distance_mpc": _value_with_bounds(
            _parameter_value(snapshot, "luminosity_distance")
        ),
        "solar_mass_geometric_radius_km": SOLAR_MASS_GEOMETRIC_RADIUS_KM,
        "absolute_gamma_relation": (
            "gamma=(ell_qEFT_km*(1+z)/(M_f_source_solar*"
            "GMsun_cminus2_km))^6"
        ),
        "absolute_gamma_ratio_central": ratio,
        "absolute_gamma_central": gamma,
        "d_absolute_gamma_d_ell_km": QEFT_POWER * gamma / ell_qeft_km,
        "absolute_gamma_metadata_range": gamma_range,
        "qnm_deformation_at_absolute_gamma": {
            axis: coefficient * gamma
            for axis, coefficient in qnm_coefficients.items()
        },
        "metadata_only_not_public_likelihood": True,
    })


def absolute_gamma_metadata_packet(
    *,
    v2196_path: Path = DEFAULT_V2196_PATH,
    v2197_path: Path = DEFAULT_V2197_PATH,
) -> dict[str, Any]:
    v2196 = load_json(v2196_path)
    v2197 = load_json(v2197_path)
    surrogates = _surrogate_by_label(v2196)
    qnm_coefficients = _qnm_coefficients(v2197)
    event_rows = [
        absolute_gamma_row(
            label,
            ell_qeft_km=float(surrogates[label]["upper_bound_km_90"]),
            snapshot=GWOSC_PARAMETER_SNAPSHOT[label],
            qnm_coefficients=qnm_coefficients,
        )
        for label in SOURCE_EVENTS
    ]
    combined_bound = float(surrogates["combined"]["upper_bound_km_90"])
    combined_bound_event_rows = [
        absolute_gamma_row(
            label,
            ell_qeft_km=combined_bound,
            snapshot=GWOSC_PARAMETER_SNAPSHOT[label],
            qnm_coefficients=qnm_coefficients,
        )
        for label in SOURCE_EVENTS
    ]
    return canonicalize_json_floats({
        "packet_id": "parspec_qeft_absolute_gamma_metadata_v1",
        "basis_versions": {
            "published_bound_surrogate": v2196["version"],
            "qnm_deformation_jacobian": v2197["version"],
        },
        "source_events": list(SOURCE_EVENTS),
        "source_axis": SOURCE_AXIS,
        "qeft_power": QEFT_POWER,
        "metadata_sources": GWOSC_PARAMETER_SNAPSHOT,
        "normalization_constants": {
            "solar_mass_geometric_radius_km": SOLAR_MASS_GEOMETRIC_RADIUS_KM
        },
        "event_bound_absolute_gamma_rows": event_rows,
        "combined_bound_km_90": combined_bound,
        "combined_bound_projected_per_event": combined_bound_event_rows,
        "combined_bound_single_remnant_metadata_ready": False,
        "combined_bound_single_remnant_metadata_note": (
            "The published combined ell_qEFT bound is a joint event result; "
            "there is no single remnant mass/redshift pair for the combined "
            "row, so v2.199 projects the combined bound through each source "
            "event's own GWOSC metadata instead."
        ),
        "absolute_gamma_metadata_ready": True,
        "public_likelihood_ready": False,
        "engine_axis_map_ready": False,
        "claim_use_allowed": False,
    })


def evaluate_absolute_gamma_metadata(
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = result or diagnose_r4_parspec_absolute_gamma_metadata()
    packet = result["absolute_gamma_metadata_packet"]
    blockers: set[str] = set()

    if packet.get("absolute_gamma_metadata_ready") is not True:
        blockers.add("absolute_gamma_metadata_not_ready")
    if packet.get("public_likelihood_ready") is not False:
        blockers.add("public_likelihood_unexpectedly_ready")
    if packet.get("engine_axis_map_ready") is not False:
        blockers.add("engine_axis_map_unexpectedly_ready")
    if packet.get("claim_use_allowed") is not False:
        blockers.add("claim_use_not_disabled")

    rows = packet.get("event_bound_absolute_gamma_rows", [])
    if tuple(row.get("label") for row in rows) != SOURCE_EVENTS:
        blockers.add("source_event_rows_mismatch")
    for row in rows:
        label = row.get("label", "unknown")
        if float(row.get("absolute_gamma_central", 0.0)) <= 0.0:
            blockers.add(f"{label}_absolute_gamma_not_positive")
        if row.get("metadata_only_not_public_likelihood") is not True:
            blockers.add(f"{label}_metadata_likelihood_boundary_missing")
        if row.get("selected_pe_record") != GWOSC_PARAMETER_SNAPSHOT[label][
            "selected_pe_record"
        ]:
            blockers.add(f"{label}_selected_pe_record_mismatch")

    claim_blockers = {
        "qnm_deformation_to_bresciani_engine_r4_operator_basis_map_missing",
        "engine_axis_orientation_missing",
        "engine_axis_normalization_missing",
        "public_parspec_qeft_likelihood_or_posterior_samples_missing",
        "claim_grade_systematics_export_missing",
        "external_adversarial_review_missing",
    }
    if blockers:
        claim_blockers.add("absolute_gamma_metadata_not_ready")

    return canonicalize_json_floats({
        "absolute_gamma_metadata_ready": not blockers,
        "public_likelihood_ready": False,
        "engine_axis_map_ready": False,
        "ready_for_framework_claim": False,
        "metadata_blockers": sorted(blockers),
        "resolved_v2197_subpiece": (
            "source_event_absolute_gamma_metadata"
            if not blockers else None
        ),
        "remaining_claim_blockers": sorted(claim_blockers),
        "claim_blockers": sorted(claim_blockers),
        "claimable_framework_exclusions_now": [],
        "route_status": (
            "parspec_absolute_gamma_metadata_ready_engine_axis_map_missing"
            if not blockers
            else "parspec_absolute_gamma_metadata_blocked"
        ),
    })


def malformed_absolute_gamma_metadata() -> dict[str, Any]:
    result = base_absolute_gamma_metadata_result()
    packet = result["absolute_gamma_metadata_packet"]
    packet["claim_use_allowed"] = True
    packet["event_bound_absolute_gamma_rows"][0]["absolute_gamma_central"] = 0.0
    return result


def base_absolute_gamma_metadata_result(
    *,
    v2196_path: Path = DEFAULT_V2196_PATH,
    v2197_path: Path = DEFAULT_V2197_PATH,
) -> dict[str, Any]:
    v2196 = load_json(v2196_path)
    v2197 = load_json(v2197_path)
    return {
        "version": VERSION,
        "basis": [
            "v2.196_published_bound_surrogate",
            "v2.197_qnm_deformation_jacobian",
            "GWOSC_preferred_parameter_api_snapshots",
        ],
        "v2196_route_status": v2196["route_status"],
        "v2197_route_status": v2197["route_status"],
        "absolute_gamma_metadata_packet": absolute_gamma_metadata_packet(
            v2196_path=v2196_path,
            v2197_path=v2197_path,
        ),
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "selected_next_build_action": (
            "derive_qnm_deformation_to_bresciani_engine_r4_operator_basis_map"
        ),
        "interpretation": (
            "The ParSpec qEFT source-axis route now has event-level final "
            "remnant mass and redshift metadata from GWOSC preferred PE rows, "
            "so absolute gamma can be computed for the source events. This is "
            "still not a public qEFT likelihood or an engine-axis map."
        ),
    }


def diagnose_r4_parspec_absolute_gamma_metadata(
    *,
    v2196_path: Path = DEFAULT_V2196_PATH,
    v2197_path: Path = DEFAULT_V2197_PATH,
) -> dict[str, Any]:
    result = base_absolute_gamma_metadata_result(
        v2196_path=v2196_path,
        v2197_path=v2197_path,
    )
    evaluation = evaluate_absolute_gamma_metadata(result)
    malformed = evaluate_absolute_gamma_metadata(malformed_absolute_gamma_metadata())
    result["evaluation"] = evaluation
    result["malformed_control_evaluation"] = malformed
    result["absolute_gamma_metadata_ready"] = evaluation[
        "absolute_gamma_metadata_ready"
    ]
    result["route_status"] = evaluation["route_status"]
    return canonicalize_json_floats(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2196", default=str(DEFAULT_V2196_PATH))
    parser.add_argument("--v2197", default=str(DEFAULT_V2197_PATH))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_absolute_gamma_metadata(
        v2196_path=Path(args.v2196),
        v2197_path=Path(args.v2197),
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(result, indent=2, default=_json_default),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
