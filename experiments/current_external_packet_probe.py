"""Current public source probe against the external packet intake gate (v2.94)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.external_evidence_intake_gate import evaluate_external_evidence_packet


def current_source_candidate_packets() -> list[dict[str, Any]]:
    return [
        {
            "label": "cms_hepdata_energy_correlator_2024",
            "route": "future_public_g8_measurement_ingestion",
            "source_url": "https://www.hepdata.net/record/150737",
            "source_type": "public_data_product",
            "source_version_or_release": "PhysRevLett.133.071903_HEPData_150737",
            "public_data_or_code_url": "https://www.hepdata.net/record/150737",
            "license_or_access_terms": "public_hepdata_record",
            "citation": (
                "CMS Collaboration, Measurement of energy correlators inside jets "
                "and determination of alpha_S(m_Z), Phys. Rev. Lett. 133, 071903"
            ),
            "synthetic_fixture": False,
            "claim_gates": {
                "primary_or_release_source_present": True,
                "public_likelihood_or_covariance_present": False,
                "component_systematics_budget_closed": False,
                "engine_axis_mapping_source_backed": False,
                "registered_framework_domain_bounded": False,
                "framework_exclusion_math_present": False,
            },
            "known_rejection_tests": [
                "observable_basis_not_adapter_supported",
                "wilson_coefficient_normalization_not_engine_g8",
                "g8_not_isolated_from_lower_matter_moments",
                "missing_public_likelihood_or_covariance",
                "missing_framework_exclusion_math",
            ],
            "source_assessment": (
                "Public QCD jet E2C/E3C data and correlations are useful "
                "acquisition material, but they are not an engine-normalized "
                "low-energy QG g_8 packet."
            ),
        },
        {
            "label": "bresciani_partial_wave_unitarity_bounds_2025",
            "route": "future_source_backed_g8_operator_identity_search",
            "source_url": "https://arxiv.org/abs/2504.12855",
            "source_type": "primary_theory_formalism",
            "source_version_or_release": "arXiv:2504.12855",
            "public_data_or_code_url": "https://arxiv.org/abs/2504.12855",
            "license_or_access_terms": "arxiv_public",
            "citation": (
                "Bresciani, Levati, and Paradisi, Amplitudes and partial wave "
                "unitarity bounds"
            ),
            "synthetic_fixture": False,
            "claim_gates": {
                "primary_or_release_source_present": True,
                "public_likelihood_or_covariance_present": False,
                "component_systematics_budget_closed": False,
                "engine_axis_mapping_source_backed": False,
                "registered_framework_domain_bounded": False,
                "framework_exclusion_math_present": False,
            },
            "known_rejection_tests": [
                "operator_identity_missing",
                "jacobian_to_engine_g8_missing",
                "missing_public_likelihood_or_covariance",
                "missing_framework_exclusion_math",
            ],
            "source_assessment": (
                "A useful partial-wave formalism for higher-spin/EFT bounds, "
                "but not an external numerical g_8 measurement or source-backed "
                "operator identity packet."
            ),
        },
        {
            "label": "plestid_quilez_long_range_partial_wave_2026",
            "route": "future_source_backed_g8_operator_identity_search",
            "source_url": "https://arxiv.org/abs/2606.19432",
            "source_type": "primary_theory_formalism",
            "source_version_or_release": "arXiv:2606.19432v1",
            "public_data_or_code_url": "https://arxiv.org/abs/2606.19432",
            "license_or_access_terms": "arxiv_public",
            "citation": (
                "Plestid and Quilez Lasanta, Partial-wave unitarity and "
                "long-range interactions"
            ),
            "synthetic_fixture": False,
            "claim_gates": {
                "primary_or_release_source_present": True,
                "public_likelihood_or_covariance_present": False,
                "component_systematics_budget_closed": False,
                "engine_axis_mapping_source_backed": False,
                "registered_framework_domain_bounded": False,
                "framework_exclusion_math_present": False,
            },
            "known_rejection_tests": [
                "operator_identity_missing",
                "jacobian_to_engine_g8_missing",
                "missing_public_likelihood_or_covariance",
                "missing_framework_exclusion_math",
            ],
            "source_assessment": (
                "A current theory source that may improve future partial-wave "
                "normalization work for long-range forces, but it does not "
                "supply a g_8 packet, covariance, or framework exclusion."
            ),
        },
        {
            "label": "quest_length_fluctuation_limits_2025",
            "route": "gw_parity_operator_normalization_search",
            "source_url": "https://link.aps.org/doi/10.1103/61j9-cjkk",
            "source_type": "primary_measurement",
            "source_version_or_release": "PhysRevLett_QUEST_2025",
            "public_data_or_code_url": "https://link.aps.org/doi/10.1103/61j9-cjkk",
            "license_or_access_terms": "publisher_record",
            "citation": (
                "QUEST Collaboration, Broadband limits on stochastic length "
                "fluctuations from a pair of table-top interferometers"
            ),
            "synthetic_fixture": False,
            "claim_gates": {
                "primary_or_release_source_present": True,
                "public_likelihood_or_covariance_present": False,
                "component_systematics_budget_closed": False,
                "engine_axis_mapping_source_backed": False,
                "registered_framework_domain_bounded": False,
                "framework_exclusion_math_present": False,
            },
            "known_rejection_tests": [
                "source_backed_operator_normalization_missing",
                "source_native_packet_not_engine_axis",
                "engine_axis_target_missing",
                "missing_public_likelihood_or_covariance",
                "missing_framework_exclusion_math",
            ],
            "source_assessment": (
                "A real interferometric limit on stochastic length fluctuations, "
                "but it is not a PPV-to-engine gravitational parity operator "
                "bridge or registered-framework exclusion packet."
            ),
        },
    ]


def diagnose_current_external_packet_probe() -> dict[str, Any]:
    packets = current_source_candidate_packets()
    evaluations = [
        evaluate_external_evidence_packet(packet)
        for packet in packets
    ]
    rows = []
    for packet, evaluation in zip(packets, evaluations, strict=True):
        rows.append(
            {
                "label": packet["label"],
                "route": packet["route"],
                "source_url": packet["source_url"],
                "citation": packet["citation"],
                "source_assessment": packet["source_assessment"],
                "schema_ready": evaluation["schema_ready"],
                "claim_ready": evaluation["claim_ready"],
                "missing_fields": evaluation["missing_fields"],
                "active_rejection_tests": evaluation["active_rejection_tests"],
                "failed_claim_gates": evaluation.get("failed_claim_gates", []),
                "blockers": evaluation["blockers"],
            }
        )

    claim_ready = [row["label"] for row in rows if row["claim_ready"]]
    schema_ready = [row["label"] for row in rows if row["schema_ready"]]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": "v2.94",
        "basis": [
            "v2.93_external_evidence_intake_gate",
            "current_public_source_recheck_2026_06_19",
        ],
        "probe_scope": "current_public_sources_against_intake_gate",
        "candidate_count": len(rows),
        "schema_ready_candidates": schema_ready,
        "claim_ready_candidates": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "source_urls_checked": [row["source_url"] for row in rows],
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "current_source_probe_no_external_packet_satisfies_gate",
        "best_next_artifact": (
            "No current public source in this probe satisfies the v2.93 intake "
            "gate; obtain a real engine-normalized external packet before "
            "attempting promotion."
        ),
        "interpretation": (
            "The recheck found useful source material and one current "
            "partial-wave formalism update, but no source provides a complete "
            "engine-normalized packet with public likelihood, closed "
            "systematics, and framework-exclusion math."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.94/current_external_packet_probe.json",
    )
    args = parser.parse_args()

    result = diagnose_current_external_packet_probe()
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
