"""Birefringence parity-axis adapter requirements (v2.56).

v2.49 kept cosmic birefringence empirically alive, while v2.52/v2.53 blocked it
on systematics and source-backed axis mapping. This audit makes that mapping
blocker explicit: an observed CMB polarization rotation beta is not yet a
source-backed engine value for g_R2_parity or g_R3_parity.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
sys.path.insert(0, "src")
from experiments.birefringence_evidence_freshness import (
    DATASETS,
    diagnose_birefringence_evidence_freshness,
)
from experiments.explicit_tower_basis import _json_default
from itb.constraints.cosmic_birefringence import CosmicBirefringenceData, KAPPA_BETA
from itb.nontower import ExternalMeasurementEvidence, evaluate_nontower_promotion_guard


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


def adapter_requirements() -> list[dict[str, str]]:
    return [
        _requirement(
            "source_backed_operator_identity",
            (
                "A cited operator-level statement identifying which parity-odd "
                "term rotates CMB polarization and which engine coefficient it maps to."
            ),
            "missing",
            "operator_identity_not_source_backed",
        ),
        _requirement(
            "beta_to_engine_axis_normalization",
            (
                "A source-backed normalization replacing the current toy "
                "KAPPA_BETA value."
            ),
            "toy_only",
            "beta_axis_normalization_toy",
        ),
        _requirement(
            "em_vs_gravitational_parity_separation",
            (
                "A separation between electromagnetic cosmic rotation and "
                "gravitational parity coefficients such as g_R2_parity/g_R3_parity."
            ),
            "missing",
            "em_gravity_parity_map_not_separated",
        ),
        _requirement(
            "frequency_and_redshift_transfer_model",
            (
                "A transfer model for whether beta is achromatic, frequency-dependent, "
                "redshift-dependent, or sourced by a late-time field."
            ),
            "missing",
            "missing_frequency_redshift_transfer",
        ),
        _requirement(
            "public_likelihood_or_covariance",
            (
                "A public beta likelihood/covariance usable by the engine rather "
                "than a single copied central value."
            ),
            "missing",
            "missing_public_beta_likelihood",
        ),
        _requirement(
            "absolute_angle_calibration_closure",
            (
                "Instrument polarization-angle calibration closed without using "
                "the sought cosmic signal as the calibrator."
            ),
            "open",
            "instrument_angle_miscalibration_degeneracy",
        ),
        _requirement(
            "foreground_systematics_closure",
            (
                "Foreground EB and map-making systematics bounded across independent "
                "pipeline choices."
            ),
            "open",
            "foreground_systematics_not_closed",
        ),
        _requirement(
            "five_sigma_or_preregistered_subclaim",
            (
                "A discovery-grade detection or a strictly labelled sub-discovery "
                "evidence row that cannot be used as a framework exclusion."
            ),
            "sub_discovery",
            "no_5sigma_single_dataset_detection",
        ),
        _requirement(
            "non_circular_framework_predictions",
            (
                "Framework beta/parity predictions computed without using the same "
                "beta measurement as both construction input and validation target."
            ),
            "open",
            "data_driven_eft_reuses_birefringence",
        ),
        _requirement(
            "excluding_discriminator_math",
            (
                "A source-backed mapped parity value that excludes at least one "
                "registered framework beyond uncertainty."
            ),
            "missing",
            "discriminator_math_not_excluding",
        ),
    ]


def _current_evidence() -> ExternalMeasurementEvidence:
    baseline = DATASETS[0]
    return ExternalMeasurementEvidence(
        axis="g_R2_parity",
        route="cosmic_birefringence_beta_hint",
        source_url=baseline["source"]["url"],
        source_type="primary_literature",
        measurement_kind="external_numeric_measurement",
        numerical_value=baseline["beta_deg"],
        uncertainty=baseline["sigma_deg"],
        axis_mapping_kind="toy_linear_beta_map",
        systematics_status="open",
        metadata={
            "kappa_beta_deg_per_unit_g_R2_parity": KAPPA_BETA,
            "kappa_status": "order_of_magnitude_toy_normalization",
            "internal_cut_only": False,
            "source_title": baseline["source"]["title"],
        },
    )


def diagnose_birefringence_parity_adapter_requirements() -> dict[str, Any]:
    freshness = diagnose_birefringence_evidence_freshness()
    constraint = CosmicBirefringenceData(mode="hint", n_sigma=2.0)
    evidence = _current_evidence()
    guard = evaluate_nontower_promotion_guard(
        evidence,
        discriminator_claimable_by_math=False,
    )
    requirements = adapter_requirements()
    open_requirements = [
        row["id"]
        for row in requirements
        if row["current_status"] in {"missing", "open", "toy_only", "sub_discovery"}
    ]

    blocker_set = set(freshness["claim_blockers"])
    blocker_set.update(guard["blockers"])
    blocker_set.update(row["blocker_if_missing"] for row in requirements)

    return {
        "basis": [
            "v2.49_birefringence_evidence_freshness",
            "v2.52_nontower_promotion_guard",
            "engine_cosmic_birefringence_constraint",
        ],
        "route": "cosmic_birefringence",
        "axis_candidates": ["g_R2_parity", "g_R3_parity"],
        "engine_current_mapping": {
            "formula": "beta_pred_deg = KAPPA_BETA * g_R2_parity",
            "kappa_beta_deg_per_unit_g_R2_parity": KAPPA_BETA,
            "mapping_status": "toy_order_of_magnitude_not_source_backed",
            "preferred_g_R2_parity_band_2sigma": list(constraint.preferred_band),
            "zero_exclusion_sigma_engine_constraint": constraint.excludes_zero_at_sigma,
        },
        "evidence_freshness_snapshot": {
            "route_status": freshness["route_status"],
            "dataset_count": freshness["dataset_count"],
            "positive_sign_dataset_count": freshness["positive_sign_dataset_count"],
            "independent_pair_zero_exclusion_sigma": freshness[
                "independent_instrument_pair_fixed_effect"
            ]["zero_exclusion_sigma"],
            "systematic_dominated_datasets": freshness[
                "systematic_dominated_datasets"
            ],
        },
        "adapter_requirements": requirements,
        "open_adapter_requirements": open_requirements,
        "current_evidence": evidence.to_dict(),
        "current_guard": guard,
        "claim_ready_routes": [],
        "claimable_discriminator_now": False,
        "claim_blockers": sorted(blocker_set),
        "route_status": "parity_adapter_required_not_satisfied",
        "best_next_artifact": (
            "A source-backed beta-to-parity adapter with public likelihood, "
            "closed calibration/foreground systematics, and non-circular "
            "framework predictions."
        ),
        "interpretation": (
            "Cosmic birefringence remains empirically alive, but the engine's "
            "current beta-to-g_R2_parity map is a toy normalization. A framework "
            "claim needs a source-backed operator identity, EM-versus-gravity "
            "parity separation, public likelihood, closed systematics, and "
            "non-circular predictions."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.56/"
            "birefringence_parity_adapter_requirements.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_birefringence_parity_adapter_requirements()
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
