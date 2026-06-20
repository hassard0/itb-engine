"""Search public evidence for an R4 shape likelihood packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.159"

LIKELIHOOD_ACCEPTANCE_FIELDS = (
    "public_likelihood_or_covariance",
    "maps_to_bresciani_r4_axes",
    "axis_normalization_declared",
    "reproducible_data_or_code",
    "systematics_or_domain_declared",
    "excluding_discriminator_math",
)


def r4_shape_likelihood_acceptance_contract() -> dict[str, Any]:
    return {
        "target_axes": [
            "g_R4_c1",
            "g_R4_c2",
            "g_R4_c3",
            "g_R4_plus",
            "g_R4_minus_abs",
        ],
        "required_fields": list(LIKELIHOOD_ACCEPTANCE_FIELDS),
        "claim_rule": (
            "A candidate may become claim evidence only if all required "
            "fields are true and the R4 query row remains source-provenance "
            "clean."
        ),
    }


def public_r4_likelihood_candidates() -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": "gwtc_public_catalog_data",
            "url": "https://gwosc.org/eventapi/html/GWTC/",
            "evidence_family": "public_gravitational_wave_catalog",
            "public_likelihood_or_covariance": False,
            "maps_to_bresciani_r4_axes": False,
            "axis_normalization_declared": False,
            "reproducible_data_or_code": True,
            "systematics_or_domain_declared": True,
            "excluding_discriminator_math": False,
            "interpretation": (
                "GWOSC provides public event data/catalogs, but not a ready "
                "R4-shape likelihood over Bresciani axes."
            ),
        },
        {
            "candidate_id": "higher_curvature_gw_constraints_prd_111_084049",
            "url": "https://journals.aps.org/prd/abstract/10.1103/PhysRevD.111.084049",
            "evidence_family": "higher_curvature_gw_bounds",
            "public_likelihood_or_covariance": False,
            "maps_to_bresciani_r4_axes": False,
            "axis_normalization_declared": False,
            "reproducible_data_or_code": False,
            "systematics_or_domain_declared": True,
            "excluding_discriminator_math": False,
            "interpretation": (
                "Relevant higher-curvature GW constraints, but not a public "
                "machine-usable likelihood mapped to the engine R4 axes."
            ),
        },
        {
            "candidate_id": "greft_qnm_causality_observability",
            "url": "https://arxiv.org/abs/2401.05524",
            "evidence_family": "GREFT_QNM_observability_and_causality",
            "public_likelihood_or_covariance": False,
            "maps_to_bresciani_r4_axes": False,
            "axis_normalization_declared": False,
            "reproducible_data_or_code": False,
            "systematics_or_domain_declared": True,
            "excluding_discriminator_math": False,
            "interpretation": (
                "Useful for prospective observability and causality, but not "
                "a released R4 shape likelihood packet."
            ),
        },
        {
            "candidate_id": "generic_eft_beyond_gr_gw_dictionary",
            "url": "https://link.aps.org/doi/10.1103/bl9q-1q3r",
            "evidence_family": "EFT_waveform_scaling_dictionary",
            "public_likelihood_or_covariance": False,
            "maps_to_bresciani_r4_axes": False,
            "axis_normalization_declared": False,
            "reproducible_data_or_code": False,
            "systematics_or_domain_declared": True,
            "excluding_discriminator_math": False,
            "interpretation": (
                "Provides a waveform-scaling dictionary, but not a public "
                "likelihood or direct Bresciani R4-axis projection."
            ),
        },
        {
            "candidate_id": "improved_higher_order_curvature_gw_constraints",
            "url": "https://pure.mpg.de/rest/items/item_3318951_3/component/file_3318952/content",
            "evidence_family": "higher_order_curvature_gw_constraints",
            "public_likelihood_or_covariance": False,
            "maps_to_bresciani_r4_axes": False,
            "axis_normalization_declared": False,
            "reproducible_data_or_code": False,
            "systematics_or_domain_declared": True,
            "excluding_discriminator_math": False,
            "interpretation": (
                "Relevant constraints on higher-curvature models, but not a "
                "public covariance packet over the engine R4 shape coordinates."
            ),
        },
    ]


def evaluate_likelihood_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    failures = [
        field for field in LIKELIHOOD_ACCEPTANCE_FIELDS
        if candidate.get(field) is not True
    ]
    return canonicalize_json_floats({
        "candidate_id": candidate["candidate_id"],
        "evidence_family": candidate["evidence_family"],
        "criteria": {
            field: candidate.get(field) is True
            for field in LIKELIHOOD_ACCEPTANCE_FIELDS
        },
        "failed_criteria": failures,
        "ready_for_likelihood_packet": not failures,
        "ready_for_framework_claim": False,
        "interpretation": candidate["interpretation"],
    })


def diagnose_r4_public_shape_likelihood_search() -> dict[str, Any]:
    candidates = public_r4_likelihood_candidates()
    evaluations = {
        candidate["candidate_id"]: evaluate_likelihood_candidate(candidate)
        for candidate in candidates
    }
    ready = [
        candidate_id for candidate_id, row in evaluations.items()
        if row["ready_for_likelihood_packet"]
    ]
    failure_counts: dict[str, int] = {}
    for row in evaluations.values():
        for failure in row["failed_criteria"]:
            failure_counts[failure] = failure_counts.get(failure, 0) + 1

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.158_bresciani_r4_shape_unitarity_diagnostic",
            "public_r4_shape_likelihood_search",
            "GWOSC_and_GREFT_candidate_sources",
        ],
        "acceptance_contract": r4_shape_likelihood_acceptance_contract(),
        "candidate_likelihood_sources": candidates,
        "evaluations": evaluations,
        "ready_likelihood_packets": ready,
        "claimable_framework_exclusions_now": [],
        "ready_for_measurement_likelihood_claim": False,
        "ready_for_framework_claim": False,
        "failure_counts": dict(sorted(failure_counts.items())),
        "route_status": "r4_public_shape_likelihood_search_no_ready_packet",
        "selected_next_build_action": (
            "build_r4_shape_likelihood_packet_requirements_manifest"
        ),
        "best_next_artifact": (
            "A reusable R4 likelihood-packet manifest/schema that can be used "
            "to ingest future GW/GREFT evidence without weakening the existing "
            "claim guards."
        ),
        "interpretation": (
            "Public GW and GREFT sources are relevant, but none currently "
            "meets the engine's packet contract for a Bresciani R4 shape "
            "likelihood."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.159/"
            "r4_public_shape_likelihood_search.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_r4_public_shape_likelihood_search()
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
