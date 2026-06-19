"""g_8 high-moment external measurement specification (v2.54).

v2.53 ranked the matter high-moment route as the most actionable unsolved
discriminator path. This audit turns that route into an explicit measurement
contract: what an external spin-4, detector, or high-moment program would have
to publish before the engine may promote it into a framework discriminator.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, ".")
sys.path.insert(0, "src")
from experiments.explicit_tower_basis import _json_default
from experiments.fisher_multikinematic import (
    _fisher,
    design_forward,
    design_partial_waves,
)
from itb.nontower import ExternalMeasurementEvidence, evaluate_nontower_promotion_guard


MATTER = ["g_4", "g_6", "g_8"]
S_GRID = np.linspace(0.2, 1.0, 9)
G8_FREEDOM_RANGE = 0.471

PRIMARY_SOURCES = {
    "sharp_swampland": {
        "title": "Caron-Huot et al., Sharp Boundaries for the Swampland",
        "url": "https://arxiv.org/abs/2102.08951",
        "role": (
            "Dispersive sum-rule basis for higher-derivative gravitational "
            "couplings away from the naive forward-limit obstruction."
        ),
    },
    "detectors": {
        "title": "Caron-Huot et al., Detectors in weakly-coupled field theories",
        "url": "https://arxiv.org/abs/2209.00008",
        "role": (
            "Asymptotic detector/light-ray observable framework that motivates "
            "a published detector-moment route rather than an internal toy cut."
        ),
    },
    "partial_wave_unitarity": {
        "title": "Bresciani, Levati, and Paradisi, partial-wave unitarity bounds",
        "url": "https://arxiv.org/abs/2504.12855",
        "role": (
            "Source for modern partial-wave unitarity formalism relevant to "
            "higher-spin and gravitational EFT amplitude constraints."
        ),
    },
}


def _matrix_summary(rows: list[list[float]]) -> dict[str, Any]:
    cond, resolution = _fisher(rows)
    matrix = np.asarray(rows, dtype=float)
    g8_column = matrix[:, MATTER.index("g_8")]
    pure_g8_rows = [
        int(i)
        for i, row in enumerate(matrix)
        if abs(row[2]) > 1e-12 and abs(row[0]) <= 1e-12 and abs(row[1]) <= 1e-12
    ]
    mixed_norm = float(np.linalg.norm(matrix[:, :2]))
    g8_norm = float(np.linalg.norm(g8_column))
    column_purity = (
        float(g8_norm / (g8_norm + mixed_norm))
        if g8_norm + mixed_norm > 0.0
        else 0.0
    )
    return {
        "condition_number": float(cond),
        "resolution": resolution,
        "g8_resolution_fraction_of_frontier": (
            float(resolution["g_8"] / G8_FREEDOM_RANGE)
        ),
        "pure_g8_row_count": len(pure_g8_rows),
        "pure_g8_row_indices": pure_g8_rows,
        "column_purity": column_purity,
        "geometry_passes_isolation_gate": bool(
            len(pure_g8_rows) > 0
            and cond < 50.0
            and resolution["g_8"] < 0.2 * G8_FREEDOM_RANGE
        ),
    }


def _high_moment_design_rows(s_grid: np.ndarray) -> list[list[float]]:
    """Internal v1.88 high-moment proxy in the g4/g6/g8 basis."""
    return [[0.0, float(s**4), float(s**6)] for s in s_grid]


def _design_rows() -> dict[str, list[list[float]]]:
    return {
        "forward_only_narrow": design_forward(S_GRID),
        "forward_only_wide_energy": design_forward(np.linspace(0.2, 3.0, 9)),
        "high_moment_design_probe": _high_moment_design_rows(S_GRID),
        "spin_0_2_4_partial_waves": design_partial_waves(S_GRID),
    }


def _design_status(name: str, summary: dict[str, Any]) -> str:
    if name == "forward_only_narrow":
        return "rejected_forward_degeneracy"
    if name == "forward_only_wide_energy":
        return "rejected_energy_reach_artifact_without_eft_control"
    if name == "high_moment_design_probe":
        return "internal_design_probe_needs_external_mapping"
    if summary["geometry_passes_isolation_gate"]:
        return "geometry_satisfies_isolation_but_needs_external_measurement"
    return "geometry_not_sufficient"


def _design_summaries() -> dict[str, dict[str, Any]]:
    summaries = {}
    for name, rows in _design_rows().items():
        summary = _matrix_summary(rows)
        summary["status"] = _design_status(name, summary)
        summaries[name] = summary
    return summaries


def _requirement(
    requirement_id: str,
    description: str,
    current_status: str,
    blocker: str,
) -> dict[str, str]:
    return {
        "id": requirement_id,
        "description": description,
        "current_status": current_status,
        "blocker_if_missing": blocker,
    }


def measurement_contract() -> list[dict[str, str]]:
    return [
        _requirement(
            "external_numeric_observable",
            (
                "A published numerical value or upper/lower bound for a spin-4, "
                "detector, or high-moment observable with uncertainty."
            ),
            "missing",
            "missing_external_numeric_measurement",
        ),
        _requirement(
            "source_backed_g8_axis_mapping",
            (
                "A cited map from the published observable basis to the engine "
                "g_8 coordinate, including normalization and operator basis."
            ),
            "missing",
            "axis_mapping_not_source_backed",
        ),
        _requirement(
            "angular_or_partial_wave_isolation",
            (
                "Angular, spin-4, or detector-moment information that breaks "
                "the g_4/g_6/g_8 forward-amplitude degeneracy."
            ),
            "geometry_only_internal",
            "g8_not_isolated_from_lower_matter_moments",
        ),
        _requirement(
            "public_likelihood_or_covariance",
            (
                "A public covariance, likelihood, or reproducible error budget "
                "so the engine can compute exclusion rather than read a plot."
            ),
            "missing",
            "missing_public_likelihood_or_covariance",
        ),
        _requirement(
            "eft_valid_energy_window",
            (
                "A published energy/cutoff domain proving the observable is "
                "inside the EFT validity regime; wide-energy conditioning alone "
                "cannot count as g_8 isolation."
            ),
            "missing",
            "eft_validity_not_bounded",
        ),
        _requirement(
            "closed_systematics_budget",
            (
                "Calibration, angular acceptance, EFT-truncation, and background "
                "systematics bounded strongly enough for a framework cut."
            ),
            "open",
            "systematics_not_closed",
        ),
        _requirement(
            "framework_applicability_domain",
            (
                "A stated domain showing the measurement constrains the same "
                "low-energy EFT coefficient used by registered frameworks."
            ),
            "missing",
            "framework_domain_not_validated",
        ),
        _requirement(
            "excluding_discriminator_math",
            (
                "A source-backed numerical cut that excludes at least one "
                "registered framework or island branch beyond uncertainty."
            ),
            "missing",
            "discriminator_math_not_excluding",
        ),
    ]


def _current_design_probe_evidence() -> ExternalMeasurementEvidence:
    return ExternalMeasurementEvidence(
        axis="g_8",
        route="high_scattering_moment_design_probe",
        source_url=PRIMARY_SOURCES["detectors"]["url"],
        source_type="primary_literature",
        measurement_kind="internal_design_probe",
        numerical_value=None,
        uncertainty=None,
        axis_mapping_kind="toy_jacobian",
        systematics_status="open",
        metadata={
            "internal_cut_only": True,
            "implemented_design": "experiments/min_experiment_set.py:HighScatteringMoment",
            "required_external_route": (
                "published spin-4 partial-wave or detector-moment observable"
            ),
        },
    )


def _measurement_packet_template() -> dict[str, Any]:
    return {
        "axis": "g_8",
        "route": "spin_4_partial_wave_or_detector_high_moment",
        "required_source_url_prefixes": ["https://arxiv.org/", "https://doi.org/"],
        "required_source_type": "primary_literature_or_public_dataset",
        "required_measurement_kind": "external_numeric_measurement",
        "required_numerical_fields": [
            "central_value_or_bound",
            "statistical_uncertainty",
            "systematic_uncertainty",
            "covariance_or_likelihood",
        ],
        "required_mapping_fields": [
            "observable_basis",
            "wilson_coefficient_normalization",
            "cutoff_or_energy_domain",
            "jacobian_or_projection_to_g_8",
            "mixing_with_g_4_g_6",
        ],
        "required_systematics_fields": [
            "angular_acceptance",
            "calibration",
            "background_model",
            "eft_truncation",
            "renormalization_or_running",
        ],
    }


def diagnose_g8_high_moment_measurement_specification() -> dict[str, Any]:
    designs = _design_summaries()
    current_evidence = _current_design_probe_evidence()
    guard = evaluate_nontower_promotion_guard(
        current_evidence,
        discriminator_claimable_by_math=False,
    )
    contract = measurement_contract()
    missing_or_open = [
        req["id"]
        for req in contract
        if req["current_status"] in {"missing", "open", "geometry_only_internal"}
    ]
    claim_blockers = sorted({
        req["blocker_if_missing"] for req in contract
    } | set(guard["blockers"]))

    return {
        "basis": [
            "v1.36_partial_wave_identifiability",
            "v1.88_high_moment_design_probe",
            "v2.51_g8_sourceability_audit",
            "v2.52_nontower_promotion_guard",
            "v2.53_unified_route_frontier",
        ],
        "axis": "g_8",
        "route": "matter_high_moment_g_8",
        "primary_sources": list(PRIMARY_SOURCES.values()),
        "design_summaries": designs,
        "measurement_contract": contract,
        "measurement_packet_template": _measurement_packet_template(),
        "current_design_probe_evidence": current_evidence.to_dict(),
        "current_design_probe_guard": guard,
        "missing_or_open_contract_requirements": missing_or_open,
        "claim_ready_routes": [],
        "claimable_discriminator_now": False,
        "claim_blockers": claim_blockers,
        "route_status": "measurement_spec_defined_not_satisfied",
        "best_next_artifact": (
            "A public spin-4 partial-wave or asymptotic-detector-moment "
            "measurement packet satisfying the contract and yielding excluding "
            "math against a registered framework branch."
        ),
        "interpretation": (
            "The spin-0/2/4 design has the right internal geometry to isolate "
            "g_8, unlike a forward-only amplitude. That is still not a quantum "
            "gravity solution: the current route has no external numerical "
            "measurement, no source-backed engine-axis normalization, no public "
            "likelihood, no closed systematics budget, and no excluding math."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.54/"
            "g8_high_moment_measurement_specification.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_g8_high_moment_measurement_specification()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(result, indent=2, default=_json_default),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
