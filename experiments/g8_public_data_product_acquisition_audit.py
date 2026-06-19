"""g_8 public data-product acquisition audit (v2.80).

v2.79 created an executable adapter gate for future g_8 packets. This audit
checks current public data products and theory bridges against that gate,
separating "downloadable or citable material exists" from "the material is an
engine-normalized quantum-gravity g_8 packet."
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.g8_adapter_acceptance_harness import evaluate_g8_adapter_packet


def _packet(
    *,
    label: str,
    source_url: str,
    source_type: str,
    measurement_kind: str,
    observable_basis: str,
    wilson_normalization: str,
    cutoff_domain: str,
    projection: dict[str, float] | None,
    covariance_or_likelihood: Any,
    systematics_status: str,
    framework_domain: str,
    discriminator_math: str,
) -> dict[str, Any]:
    return {
        "label": label,
        "axis": "g_8",
        "route": label,
        "source_url": source_url,
        "source_type": source_type,
        "measurement_kind": measurement_kind,
        "central_value_or_bound": None,
        "statistical_uncertainty": None,
        "systematic_uncertainty": None,
        "observable_basis": observable_basis,
        "wilson_coefficient_normalization": wilson_normalization,
        "cutoff_or_energy_domain": cutoff_domain,
        "jacobian_or_projection_to_g_8": projection or {},
        "mixing_with_g_4_g_6": "uncontrolled",
        "covariance_or_likelihood": covariance_or_likelihood,
        "systematics_budget": systematics_status,
        "framework_applicability_domain": framework_domain,
        "discriminator_math": discriminator_math,
        "synthetic_fixture": False,
    }


def _candidate(
    *,
    label: str,
    title: str,
    source_url: str,
    publication_url: str,
    data_product_url: str | None,
    data_product_kind: str,
    acquisition_status: str,
    external_numerical_data: bool,
    adapter_role: str,
    packet: dict[str, Any],
    source_specific_blockers: list[str],
) -> dict[str, Any]:
    assessment = evaluate_g8_adapter_packet(packet)
    blockers = sorted(set(assessment["acceptance_blockers"]) | set(source_specific_blockers))
    return {
        "label": label,
        "title": title,
        "source_url": source_url,
        "publication_url": publication_url,
        "data_product_url": data_product_url,
        "data_product_kind": data_product_kind,
        "acquisition_status": acquisition_status,
        "external_numerical_data": external_numerical_data,
        "adapter_role": adapter_role,
        "adapter_assessment": assessment,
        "acquisition_blockers": blockers,
        "ready_for_g8_claim": assessment["ready_for_g8_claim"],
    }


def acquisition_candidates() -> list[dict[str, Any]]:
    return [
        _candidate(
            label="cms_smp_22_015_hepdata_energy_correlators",
            title=(
                "CMS energy correlators inside jets and alpha_s determination"
            ),
            source_url="https://doi.org/10.17182/hepdata.147275",
            publication_url="https://doi.org/10.1103/PhysRevLett.133.071903",
            data_product_url="https://www.hepdata.net/record/150737",
            data_product_kind="hepdata_collection_and_table_dois",
            acquisition_status="public_table_collection_identified",
            external_numerical_data=True,
            adapter_role="data_seed_not_qg_g8_packet",
            packet=_packet(
                label="cms_smp_22_015_hepdata_energy_correlators",
                source_url="https://doi.org/10.17182/hepdata.147275",
                source_type="public_dataset",
                measurement_kind="external_numeric_measurement",
                observable_basis="qcd_jet_energy_correlator",
                wilson_normalization="qcd_alpha_s_not_engine_g8",
                cutoff_domain="qcd_jet_substructure_not_qg_eft",
                projection=None,
                covariance_or_likelihood="public_tables_not_engine_likelihood",
                systematics_status="bounded",
                framework_domain="standard_model_qcd_not_registered_qg_framework",
                discriminator_math="no_qg_framework_exclusion",
            ),
            source_specific_blockers=[
                "data_product_measures_alpha_s_and_qcd_jet_structure_not_qg_g8",
            ],
        ),
        _candidate(
            label="cms_hin_23_004_heavy_ion_eec",
            title="CMS heavy-ion energy-energy correlators inside jets",
            source_url="https://arxiv.org/abs/2503.19993",
            publication_url=(
                "https://cms-results.web.cern.ch/cms-results/public-results/"
                "publications/HIN-23-004/"
            ),
            data_product_url=(
                "https://cms-results.web.cern.ch/cms-results/public-results/"
                "publications/HIN-23-004/"
            ),
            data_product_kind="publication_page_links_hepdata_record",
            acquisition_status="public_measurement_with_hepdata_link_identified",
            external_numerical_data=True,
            adapter_role="heavy_ion_qcd_design_seed_not_qg_g8",
            packet=_packet(
                label="cms_hin_23_004_heavy_ion_eec",
                source_url="https://arxiv.org/abs/2503.19993",
                source_type="primary_literature",
                measurement_kind="external_numeric_measurement",
                observable_basis="qcd_heavy_ion_energy_correlator",
                wilson_normalization="qgp_model_comparison_not_engine_g8",
                cutoff_domain="heavy_ion_qcd_medium_not_qg_eft",
                projection=None,
                covariance_or_likelihood="hepdata_tables_not_engine_likelihood",
                systematics_status="bounded",
                framework_domain="qgp_model_not_registered_qg_framework",
                discriminator_math="no_qg_framework_exclusion",
            ),
            source_specific_blockers=[
                "heavy_ion_medium_observable_not_low_energy_qg_eft_g8",
            ],
        ),
        _candidate(
            label="cms_open_data_npoint_energy_correlators",
            title="N-point energy correlators inside CMS open data",
            source_url="https://arxiv.org/abs/2201.07800",
            publication_url="https://arxiv.org/abs/2201.07800",
            data_product_url="https://opendata.cern.ch/",
            data_product_kind="cms_open_data_analysis",
            acquisition_status="open_data_analysis_identified",
            external_numerical_data=True,
            adapter_role="open_data_method_seed_not_engine_likelihood",
            packet=_packet(
                label="cms_open_data_npoint_energy_correlators",
                source_url="https://arxiv.org/abs/2201.07800",
                source_type="primary_literature",
                measurement_kind="external_numeric_measurement",
                observable_basis="qcd_multipoint_energy_flow",
                wilson_normalization="qcd_jet_observable_not_engine_g8",
                cutoff_domain="qcd_open_data_not_qg_eft",
                projection=None,
                covariance_or_likelihood="open_data_analysis_not_engine_likelihood",
                systematics_status="open",
                framework_domain="standard_model_qcd_not_registered_qg_framework",
                discriminator_math="no_qg_framework_exclusion",
            ),
            source_specific_blockers=[
                "open_data_requires_new_analysis_before_any_adapter_packet",
            ],
        ),
        _candidate(
            label="gravity_energy_correlators_four_dimensional",
            title="Energy correlators in four-dimensional gravity",
            source_url="https://arxiv.org/abs/2512.23791",
            publication_url="https://arxiv.org/abs/2512.23791",
            data_product_url=None,
            data_product_kind="theory_calculation",
            acquisition_status="theory_bridge_identified",
            external_numerical_data=False,
            adapter_role="gravity_detector_observable_bridge",
            packet=_packet(
                label="gravity_energy_correlators_four_dimensional",
                source_url="https://arxiv.org/abs/2512.23791",
                source_type="primary_literature",
                measurement_kind="theory_formalism",
                observable_basis="asymptotic_detector_moment",
                wilson_normalization="gravity_correlator_not_engine_g8",
                cutoff_domain="theory_calculation_no_external_eft_window",
                projection={"g_8": 1.0},
                covariance_or_likelihood="none_theory_only",
                systematics_status="open",
                framework_domain="not_registered_framework_adapter",
                discriminator_math="no_qg_framework_exclusion",
            ),
            source_specific_blockers=[
                "theory_calculation_not_external_measurement",
            ],
        ),
        _candidate(
            label="spinning_energy_correlators_theory",
            title="Energy correlators of spinning sources",
            source_url="https://arxiv.org/abs/2512.16985",
            publication_url="https://arxiv.org/abs/2512.16985",
            data_product_url=None,
            data_product_kind="theory_calculation",
            acquisition_status="spin_sensitive_theory_bridge_identified",
            external_numerical_data=False,
            adapter_role="angular_information_bridge",
            packet=_packet(
                label="spinning_energy_correlators_theory",
                source_url="https://arxiv.org/abs/2512.16985",
                source_type="primary_literature",
                measurement_kind="theory_formalism",
                observable_basis="asymptotic_detector_moment",
                wilson_normalization="spinning_correlator_not_engine_g8",
                cutoff_domain="theory_calculation_no_external_eft_window",
                projection={"g_8": 1.0},
                covariance_or_likelihood="none_theory_only",
                systematics_status="open",
                framework_domain="not_registered_framework_adapter",
                discriminator_math="no_qg_framework_exclusion",
            ),
            source_specific_blockers=[
                "spin_sensitive_formalism_not_external_g8_measurement",
            ],
        ),
        _candidate(
            label="long_range_partial_wave_unitarity",
            title="Partial-wave unitarity and long-range interactions",
            source_url="https://arxiv.org/abs/2606.19432",
            publication_url="https://arxiv.org/abs/2606.19432",
            data_product_url=None,
            data_product_kind="theory_formalism",
            acquisition_status="current_long_range_partial_wave_bridge_identified",
            external_numerical_data=False,
            adapter_role="ir_obstruction_bridge",
            packet=_packet(
                label="long_range_partial_wave_unitarity",
                source_url="https://arxiv.org/abs/2606.19432",
                source_type="primary_literature",
                measurement_kind="theory_formalism",
                observable_basis="spin_4_partial_wave",
                wilson_normalization="long_range_partial_wave_not_engine_g8",
                cutoff_domain="formalism_only",
                projection={"g_8": 1.0},
                covariance_or_likelihood="none_theory_only",
                systematics_status="open",
                framework_domain="not_registered_framework_adapter",
                discriminator_math="no_qg_framework_exclusion",
            ),
            source_specific_blockers=[
                "long_range_partial_wave_formalism_not_measurement_packet",
            ],
        ),
    ]


def diagnose_g8_public_data_product_acquisition_audit() -> dict[str, Any]:
    rows = acquisition_candidates()
    public_data_products = [
        row["label"] for row in rows if row["external_numerical_data"]
    ]
    theory_bridges = [
        row["label"] for row in rows if not row["external_numerical_data"]
    ]
    claim_ready = [row["label"] for row in rows if row["ready_for_g8_claim"]]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["acquisition_blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": "v2.80",
        "basis": [
            "v2.79_g8_adapter_acceptance_harness",
            "current_primary_source_search_2026_06_19",
            "hepdata_cms_energy_correlator_record",
        ],
        "axis": "g_8",
        "candidate_count": len(rows),
        "public_data_product_candidates": public_data_products,
        "theory_bridge_candidates": theory_bridges,
        "claim_ready_routes": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "public_data_products_exist_but_no_g8_adapter_packet",
        "best_next_artifact": (
            "Either a source-backed derivation from a public energy-correlator "
            "dataset to engine g_8 with covariance, or a new spin-4/detector "
            "measurement published directly in the low-energy QG EFT basis."
        ),
        "interpretation": (
            "The acquisition audit finds public, citable energy-correlator data "
            "products and useful gravity/partial-wave theory bridges. They do "
            "not satisfy the v2.79 adapter gate because none supplies an "
            "engine-normalized g_8 likelihood, bounded QG EFT domain, and "
            "framework-exclusion calculation."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.80/"
            "g8_public_data_product_acquisition_audit.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_g8_public_data_product_acquisition_audit()
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
