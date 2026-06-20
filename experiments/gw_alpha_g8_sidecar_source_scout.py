"""Current-source scout for real G8 sidecar packets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.g8_joint_source_discovery_queue import (
    current_joint_source_candidates,
)
from experiments.gw_alpha_g8_sidecar_acceptance_gate import (
    evaluate_g8_sidecar_packet,
)
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.129"
SCAN_DATE = "2026-06-20"


def primary_source_scout_rows() -> list[dict[str, Any]]:
    """Return the source-backed rows scanned for a real G8 sidecar packet."""
    return [
        {
            "label": "bresciani_partial_wave_unitarity_bounds_v2_2026",
            "source_url": "https://arxiv.org/abs/2504.12855",
            "source_kind": "primary_theory_formalism",
            "source_status": "revised_2026_04_24_published_version",
            "why_checked": (
                "Latest primary partial-wave unitarity formalism explicitly "
                "advertises spin-2 or higher-spin gravity EFT applications."
            ),
            "supplies": [
                "partial_wave_unitarity_formalism",
                "gravity_eft_high_spin_relevance",
            ],
            "missing_for_real_sidecar": [
                "external_numeric_g8_measurement",
                "source_backed_engine_g8_jacobian",
                "public_g8_likelihood_or_covariance",
                "cross_covariance_with_alpha",
                "closed_g8_systematics",
                "framework_pair_exclusion_math",
            ],
            "packet_attempt": {
                "label": "bresciani_partial_wave_unitarity_bounds_v2_2026",
                "source_url": "https://arxiv.org/abs/2504.12855",
                "source_type": "primary_literature_or_public_dataset",
                "observable_basis": "spin4_partial_wave_or_detector_high_moment",
                "projection_to_engine_g8": {
                    "status": "formalism_only_projection_not_derived",
                    "operator_identity": None,
                    "jacobian_to_engine_g8": None,
                },
                "synthetic_fixture": False,
            },
        },
        {
            "label": "cms_energy_correlator_hepdata_2024",
            "source_url": "https://doi.org/10.17182/hepdata.147275",
            "source_page_url": "https://www.hepdata.net/record/150737",
            "source_kind": "public_data_product",
            "source_status": "public_hepdata_record",
            "why_checked": (
                "Public E2C/E3C jet energy-correlator data are the closest "
                "available detector high-moment-like measurement product."
            ),
            "supplies": [
                "public_energy_correlator_tables",
                "public_correlation_matrices",
                "alpha_s_measurement",
            ],
            "missing_for_real_sidecar": [
                "quantum_gravity_g8_observable_basis",
                "engine_g8_normalization",
                "g8_numeric_value_or_bound",
                "g8_likelihood_axis",
                "shared_eft_domain_with_gw_alpha",
                "framework_pair_exclusion_math",
            ],
            "packet_attempt": {
                "label": "cms_energy_correlator_hepdata_2024",
                "source_url": "https://doi.org/10.17182/hepdata.147275",
                "source_type": "public_data_product",
                "observable_basis": "qcd_jet_energy_correlator",
                "covariance_or_likelihood": {
                    "status": "public_covariance_matrix",
                    "kind": "hepdata_energy_correlator_tables",
                    "axes": ["E2C", "E3C", "alpha_s"],
                },
                "projection_to_engine_g8": {
                    "status": "no_source_backed_projection_to_engine_g8",
                },
                "synthetic_fixture": False,
            },
        },
        {
            "label": "caron_huot_detector_operator_formalism_2022",
            "source_url": "https://arxiv.org/abs/2209.00008",
            "source_kind": "primary_theory_formalism",
            "source_status": "published_detector_operator_theory",
            "why_checked": (
                "Detector operators at null infinity are a relevant bridge for "
                "future high-moment measurement design."
            ),
            "supplies": [
                "detector_operator_formalism",
                "light_ray_operator_relation",
                "regge_trajectory_mixing_discussion",
            ],
            "missing_for_real_sidecar": [
                "gravity_g8_measurement",
                "engine_g8_projection",
                "public_numeric_likelihood",
                "alpha_cross_covariance",
                "framework_pair_exclusion_math",
            ],
            "packet_attempt": {
                "label": "caron_huot_detector_operator_formalism_2022",
                "source_url": "https://arxiv.org/abs/2209.00008",
                "source_type": "primary_literature_or_public_dataset",
                "observable_basis": "detector_operator_theory_formalism",
                "synthetic_fixture": False,
            },
        },
        {
            "label": "sharp_boundaries_swampland_sum_rules_2021",
            "source_url": "https://arxiv.org/abs/2102.08951",
            "source_kind": "primary_theory_bound",
            "source_status": "published_gravity_eft_bound",
            "why_checked": (
                "Dispersive sum rules bound higher derivative gravitational "
                "couplings and can constrain normalization assumptions."
            ),
            "supplies": [
                "gravity_eft_order_one_bounds",
                "small_impact_parameter_sum_rule_strategy",
            ],
            "missing_for_real_sidecar": [
                "direct_g8_measurement",
                "source_specific_engine_g8_jacobian",
                "public_g8_likelihood",
                "alpha_cross_covariance",
                "registered_framework_exclusion_math",
            ],
            "packet_attempt": {
                "label": "sharp_boundaries_swampland_sum_rules_2021",
                "source_url": "https://arxiv.org/abs/2102.08951",
                "source_type": "primary_literature_or_public_dataset",
                "observable_basis": "gravity_eft_theory_bound",
                "synthetic_fixture": False,
            },
        },
        {
            "label": "liu_yunes_gw170608_alpha_constraints_2024",
            "source_url": "https://arxiv.org/abs/2407.08929",
            "source_kind": "primary_measurement_analysis",
            "source_status": "primary_gw_alpha_constraint",
            "why_checked": (
                "This is the current source-backed GW alpha side of the joint "
                "route, so it must not be mistaken for the missing G8 sidecar."
            ),
            "supplies": [
                "gw170608_bayesian_alpha_constraints",
                "cubic_parity_preserving_waveform_analysis",
            ],
            "missing_for_real_sidecar": [
                "g8_observable_axis",
                "g8_likelihood",
                "g8_systematics",
                "g8_alpha_cross_covariance",
                "framework_pair_exclusion_math",
            ],
            "packet_attempt": {
                "label": "liu_yunes_gw170608_alpha_constraints_2024",
                "source_url": "https://arxiv.org/abs/2407.08929",
                "source_type": "primary_measurement",
                "observable_basis": "gw_cubic_alpha_constraint",
                "covariance_or_likelihood": {
                    "status": "public_literature_interval_not_g8_likelihood",
                    "kind": "alpha_bar_constraints",
                    "axes": ["alpha_bar_1", "alpha_bar_2"],
                },
                "synthetic_fixture": False,
            },
        },
        {
            "label": "gwosc_gwtc1_gw170608_public_strain",
            "source_url": "https://doi.org/10.7935/82H3-HH23",
            "source_page_url": "https://gwosc.org/GWTC-1/",
            "source_kind": "public_data_product",
            "source_status": "public_strain_and_metadata",
            "why_checked": (
                "Public GW170608 strain is usable for reanalysis, but it is raw "
                "input data rather than a completed G8 sidecar packet."
            ),
            "supplies": [
                "public_strain_data",
                "gw170608_special_case_metadata",
                "calibration_uncertainty_links",
            ],
            "missing_for_real_sidecar": [
                "modified_gravity_g8_waveform_adapter",
                "engine_g8_normalization",
                "public_g8_likelihood",
                "closed_systematics",
                "framework_pair_exclusion_math",
            ],
            "packet_attempt": {
                "label": "gwosc_gwtc1_gw170608_public_strain",
                "source_url": "https://doi.org/10.7935/82H3-HH23",
                "source_type": "public_data_product",
                "observable_basis": "gw_public_strain_reanalysis_input",
                "synthetic_fixture": False,
            },
        },
        {
            "label": "gwastro_o2_bbh_pe_public_posteriors",
            "source_url": "https://github.com/gwastro/o2-bbh-pe",
            "source_kind": "public_posterior_samples",
            "source_status": "public_gr_posterior_release",
            "why_checked": (
                "The release contains public GW170608 posterior samples and run "
                "files, but not modified-gravity G8 samples."
            ),
            "supplies": [
                "public_gr_posterior_samples",
                "reanalysis_run_files",
            ],
            "missing_for_real_sidecar": [
                "allowed_primary_source_url_form",
                "modified_gravity_g8_samples",
                "engine_g8_projection",
                "public_g8_likelihood",
                "framework_pair_exclusion_math",
            ],
            "packet_attempt": {
                "label": "gwastro_o2_bbh_pe_public_posteriors",
                "source_url": "https://github.com/gwastro/o2-bbh-pe",
                "source_type": "public_posterior_samples",
                "observable_basis": "gr_public_posterior_samples",
                "synthetic_fixture": False,
            },
        },
    ]


def _legacy_source_labels() -> list[str]:
    return sorted(row["label"] for row in current_joint_source_candidates())


def _ranked_attempts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    attempts: list[dict[str, Any]] = []
    for row in rows:
        evaluation = evaluate_g8_sidecar_packet(row["packet_attempt"])
        attempts.append(
            {
                "label": row["label"],
                "source_url": row["source_url"],
                "source_kind": row["source_kind"],
                "supplies": row["supplies"],
                "missing_for_real_sidecar": row["missing_for_real_sidecar"],
                "acceptance_ready": evaluation["acceptance_ready"],
                "claim_ready": evaluation["claim_ready"],
                "acceptance_blockers": evaluation["acceptance_blockers"],
                "claim_blockers": evaluation["claim_blockers"],
                "claim_blocker_count": len(evaluation["claim_blockers"]),
                "evaluation": evaluation,
            }
        )
    attempts.sort(
        key=lambda row: (
            row["claim_blocker_count"],
            row["label"] != "bresciani_partial_wave_unitarity_bounds_v2_2026",
            row["label"],
        )
    )
    return attempts


def diagnose_gw_alpha_g8_sidecar_source_scout() -> dict[str, Any]:
    rows = primary_source_scout_rows()
    attempts = _ranked_attempts(rows)
    acceptance_ready = [
        row["label"] for row in attempts if row["acceptance_ready"]
    ]
    claim_ready = [row["label"] for row in attempts if row["claim_ready"]]
    blocker_counts: dict[str, int] = {}
    for row in attempts:
        for blocker in row["claim_blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    closest = attempts[:3]
    return {
        "version": VERSION,
        "scan_date": SCAN_DATE,
        "basis": [
            "v2.128_gw_alpha_g8_sidecar_acceptance_gate",
            "current_primary_public_source_scan_2026_06_20",
            "v2.99_g8_joint_source_discovery_queue",
        ],
        "gate_target": "v2.128_gw_alpha_g8_sidecar_acceptance_gate",
        "legacy_source_queue_labels": _legacy_source_labels(),
        "source_count": len(rows),
        "evaluated_packet_attempt_count": len(attempts),
        "acceptance_ready_source_packets": acceptance_ready,
        "claim_ready_source_packets": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "source_urls_checked": sorted(
            {row.get("source_page_url", row["source_url"]) for row in rows}
            | {row["source_url"] for row in rows}
        ),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "closest_source_packet_attempts": closest,
        "evaluated_source_packet_attempts_ranked": attempts,
        "route_status": "current_g8_sidecar_sources_scanned_no_real_packet",
        "selected_next_build_action": (
            "derive_bresciani_v2_partial_wave_to_engine_g8_projection_audit"
        ),
        "best_next_artifact": (
            "A source-backed projection audit for the Bresciani v2 partial-wave "
            "formalism, explicitly determining whether an engine g8 Jacobian can "
            "be derived before any numeric measurement is available."
        ),
        "interpretation": (
            "Current primary/public sources provide useful formalism, public "
            "detector data, GW alpha constraints, and GW reanalysis inputs, but "
            "none is a real G8 sidecar packet. The closest route is still a "
            "formalism adapter, not a claim-ready discriminator."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.129/"
            "gw_alpha_g8_sidecar_source_scout.json"
        ),
    )
    args = parser.parse_args()

    result = canonicalize_json_floats(
        diagnose_gw_alpha_g8_sidecar_source_scout()
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
