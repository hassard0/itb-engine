"""Existing external measurement packet search for the g_8 route (v2.55).

v2.54 defined the packet required to promote the high-moment g_8 route. This
audit asks whether nearby public measurements already satisfy that packet. The
answer is deliberately conservative: modern energy-correlator measurements are
valuable design seeds, but none is a source-backed quantum-gravity g_8 cut.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
sys.path.insert(0, "src")
from experiments.explicit_tower_basis import _json_default
from experiments.g8_high_moment_measurement_specification import measurement_contract
from itb.nontower import ExternalMeasurementEvidence, evaluate_nontower_promotion_guard


SOURCES = {
    "cms_e2c_e3c": {
        "title": (
            "CMS, Measurement of energy correlators inside jets and "
            "determination of the strong coupling"
        ),
        "url": "https://arxiv.org/abs/2402.13864",
        "source_kind": "primary_literature",
    },
    "cms_open_data_n_point": {
        "title": "Komiske et al., N-point energy correlators inside CMS open data",
        "url": "https://arxiv.org/abs/2201.07800",
        "source_kind": "primary_literature",
    },
    "cms_hin_eec": {
        "title": (
            "CMS, Observation of nuclear modification of energy-energy "
            "correlators inside jets in heavy ion collisions"
        ),
        "url": "https://arxiv.org/abs/2503.19993",
        "source_kind": "primary_literature",
    },
    "detectors_theory": {
        "title": "Caron-Huot et al., Detectors in weakly-coupled field theories",
        "url": "https://arxiv.org/abs/2209.00008",
        "source_kind": "primary_literature",
    },
    "hadron_eec_blocks": {
        "title": (
            "Chen, Ruan, and Zhu, Energy-energy correlator at hadron colliders: "
            "celestial blocks and singularities"
        ),
        "url": "https://doi.org/10.1007/JHEP12(2025)168",
        "source_kind": "primary_literature",
    },
}


def _candidate(
    *,
    label: str,
    source_key: str,
    measurement_kind: str,
    numerical_value: float | None,
    uncertainty: float | None,
    detector_moment_relevance: str,
    public_likelihood_or_covariance: str,
    g8_axis_mapping: str,
    eft_domain: str,
    systematics_status: str,
    framework_applicability: str,
    discriminator_math: str,
    notes: list[str],
) -> dict[str, Any]:
    source = SOURCES[source_key]
    axis_mapping_kind = (
        "source_backed_direct"
        if g8_axis_mapping == "source_backed_direct_to_engine_g8"
        else "toy_or_missing"
    )
    evidence = ExternalMeasurementEvidence(
        axis="g_8",
        route=label,
        source_url=source["url"],
        source_type=source["source_kind"],
        measurement_kind=measurement_kind,
        numerical_value=numerical_value,
        uncertainty=uncertainty,
        axis_mapping_kind=axis_mapping_kind,
        systematics_status=systematics_status,
        metadata={
            "detector_moment_relevance": detector_moment_relevance,
            "public_likelihood_or_covariance": public_likelihood_or_covariance,
            "g8_axis_mapping": g8_axis_mapping,
            "eft_domain": eft_domain,
            "framework_applicability": framework_applicability,
            "discriminator_math": discriminator_math,
        },
    )
    discriminator_claimable = discriminator_math == "excludes_registered_framework"
    guard = evaluate_nontower_promotion_guard(
        evidence,
        discriminator_claimable_by_math=discriminator_claimable,
    )

    contract_failures = _contract_failures(
        measurement_kind=measurement_kind,
        numerical_value=numerical_value,
        uncertainty=uncertainty,
        detector_moment_relevance=detector_moment_relevance,
        public_likelihood_or_covariance=public_likelihood_or_covariance,
        g8_axis_mapping=g8_axis_mapping,
        eft_domain=eft_domain,
        systematics_status=systematics_status,
        framework_applicability=framework_applicability,
        discriminator_math=discriminator_math,
    )
    ready = not guard["blockers"] and not contract_failures
    return {
        "label": label,
        "source": source,
        "evidence": evidence.to_dict(),
        "guard": guard,
        "contract_failures": contract_failures,
        "contract_satisfied": not contract_failures,
        "ready_for_g8_claim": ready,
        "frontier_status": (
            "g8_measurement_packet_ready"
            if ready
            else "external_candidate_not_g8_claim_ready"
        ),
        "notes": notes,
    }


def _contract_failures(
    *,
    measurement_kind: str,
    numerical_value: float | None,
    uncertainty: float | None,
    detector_moment_relevance: str,
    public_likelihood_or_covariance: str,
    g8_axis_mapping: str,
    eft_domain: str,
    systematics_status: str,
    framework_applicability: str,
    discriminator_math: str,
) -> list[str]:
    failures = []
    if (
        measurement_kind not in {"external_numeric_measurement", "external_upper_bound"}
        or numerical_value is None
        or uncertainty is None
    ):
        failures.append("external_numeric_observable")
    if g8_axis_mapping != "source_backed_direct_to_engine_g8":
        failures.append("source_backed_g8_axis_mapping")
    if detector_moment_relevance != "spin4_or_direct_g8":
        failures.append("angular_or_partial_wave_isolation")
    if public_likelihood_or_covariance != "public_engine_usable":
        failures.append("public_likelihood_or_covariance")
    if eft_domain != "bounded_for_qg_eft":
        failures.append("eft_valid_energy_window")
    if systematics_status not in {"bounded", "closed"}:
        failures.append("closed_systematics_budget")
    if framework_applicability != "registered_framework_low_energy_eft":
        failures.append("framework_applicability_domain")
    if discriminator_math != "excludes_registered_framework":
        failures.append("excluding_discriminator_math")
    return failures


def candidate_rows() -> list[dict[str, Any]]:
    return [
        _candidate(
            label="cms_e2c_e3c_jet_substructure",
            source_key="cms_e2c_e3c",
            measurement_kind="external_numeric_measurement",
            numerical_value=None,
            uncertainty=None,
            detector_moment_relevance="qcd_energy_correlator_not_spin4_g8",
            public_likelihood_or_covariance="public_tables_not_engine_likelihood",
            g8_axis_mapping="absent_qcd_jet_observable",
            eft_domain="qcd_jet_substructure_not_qg_eft",
            systematics_status="bounded",
            framework_applicability="standard_model_qcd_not_registered_qg_framework",
            discriminator_math="no_qg_framework_exclusion",
            notes=[
                "External energy-correlator data exist and include tabulated results.",
                "The observable constrains QCD jet structure and alpha_s, not the engine g_8.",
            ],
        ),
        _candidate(
            label="cms_open_data_n_point_energy_correlators",
            source_key="cms_open_data_n_point",
            measurement_kind="external_numeric_measurement",
            numerical_value=None,
            uncertainty=None,
            detector_moment_relevance="multipoint_qcd_energy_flow",
            public_likelihood_or_covariance="open_data_analysis_not_engine_likelihood",
            g8_axis_mapping="absent_qcd_jet_observable",
            eft_domain="qcd_open_data_not_qg_eft",
            systematics_status="open",
            framework_applicability="standard_model_qcd_not_registered_qg_framework",
            discriminator_math="no_qg_framework_exclusion",
            notes=[
                "Good design precedent for measuring multipoint energy flow.",
                "It is not a source-backed projection to the engine's g_8 coordinate.",
            ],
        ),
        _candidate(
            label="cms_heavy_ion_eec_modification",
            source_key="cms_hin_eec",
            measurement_kind="external_numeric_measurement",
            numerical_value=None,
            uncertainty=None,
            detector_moment_relevance="qcd_medium_energy_correlator",
            public_likelihood_or_covariance="hepdata_tables_not_engine_likelihood",
            g8_axis_mapping="absent_heavy_ion_qcd_observable",
            eft_domain="qcd_medium_not_qg_eft",
            systematics_status="bounded",
            framework_applicability="qgp_model_comparison_not_qg_framework",
            discriminator_math="no_qg_framework_exclusion",
            notes=[
                "The CMS page links a HepData record and reports statistical/systematic uncertainties.",
                "The measured ratio probes quark-gluon-plasma jet modification, not g_8.",
            ],
        ),
        _candidate(
            label="detector_operator_theory_bridge",
            source_key="detectors_theory",
            measurement_kind="theory_formalism",
            numerical_value=None,
            uncertainty=None,
            detector_moment_relevance="detector_formalism_theory",
            public_likelihood_or_covariance="none_theory_only",
            g8_axis_mapping="not_engine_normalized",
            eft_domain="formal_qft_not_specific_qg_eft_cut",
            systematics_status="open",
            framework_applicability="not_registered_framework_adapter",
            discriminator_math="no_qg_framework_exclusion",
            notes=[
                "This remains a source-backed theory bridge.",
                "It is not an external numerical measurement packet.",
            ],
        ),
        _candidate(
            label="hadron_eec_celestial_block_partial_wave_decomposition",
            source_key="hadron_eec_blocks",
            measurement_kind="theory_formalism",
            numerical_value=None,
            uncertainty=None,
            detector_moment_relevance="partial_wave_decomposition_theory",
            public_likelihood_or_covariance="none_theory_only",
            g8_axis_mapping="not_engine_normalized",
            eft_domain="pure_yang_mills_example_not_qg_eft_cut",
            systematics_status="open",
            framework_applicability="not_registered_framework_adapter",
            discriminator_math="no_qg_framework_exclusion",
            notes=[
                "Useful bridge from EECs to partial-wave language.",
                "Still lacks an external g_8 measurement and framework cut.",
            ],
        ),
    ]


def diagnose_g8_existing_measurement_packet_search() -> dict[str, Any]:
    rows = candidate_rows()
    ready = [row for row in rows if row["ready_for_g8_claim"]]
    external_numeric = [
        row for row in rows
        if row["evidence"]["measurement_kind"] == "external_numeric_measurement"
    ]
    source_backed_candidates = [
        row for row in rows
        if row["source"]["source_kind"] == "primary_literature"
    ]
    failure_counts: dict[str, int] = {}
    for row in rows:
        for failure in row["contract_failures"]:
            failure_counts[failure] = failure_counts.get(failure, 0) + 1

    return {
        "basis": [
            "v2.54_g8_measurement_contract",
            "web_primary_source_search_2026_06_19",
            "nontower_promotion_guard",
        ],
        "axis": "g_8",
        "contract_requirement_ids": [
            requirement["id"] for requirement in measurement_contract()
        ],
        "candidate_count": len(rows),
        "external_numeric_candidate_count": len(external_numeric),
        "source_backed_candidate_count": len(source_backed_candidates),
        "contract_satisfied_candidates": [
            row["label"] for row in rows if row["contract_satisfied"]
        ],
        "claim_ready_routes": [row["label"] for row in ready],
        "claimable_discriminator_now": bool(ready),
        "contract_failure_counts": dict(sorted(failure_counts.items())),
        "rows": rows,
        "route_status": "existing_public_measurements_do_not_satisfy_g8_contract",
        "best_next_artifact": (
            "A source-backed adapter deriving an engine-normalized g_8 likelihood "
            "from spin-4/energy-correlator data, or a new measurement designed "
            "directly for that coefficient."
        ),
        "interpretation": (
            "Existing collider energy-correlator measurements are real external "
            "data and useful design seeds. None currently supplies a public, "
            "engine-usable, source-backed map to the quantum-gravity g_8 axis, "
            "an EFT-valid framework domain, or excluding discriminator math."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.55/g8_existing_measurement_packet_search.json",
    )
    args = parser.parse_args()

    result = diagnose_g8_existing_measurement_packet_search()
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
