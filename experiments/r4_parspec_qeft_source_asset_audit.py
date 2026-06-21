"""Source-asset audit for the ParSpec qEFT bridge."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_parspec_engine_axis_map_contract import (
    DEFAULT_V2188_PATH,
    SOURCE_AXIS_UNITS,
    SOURCE_AXIS_WITH_UNIT,
    current_v2188_parspec_axis_map_slot,
    evaluate_parspec_engine_axis_map_packet,
)
from experiments.r4_parspec_ringdown_source_bridge import (
    CURRENT_V2187_EVENT,
    PARSPEC_ARXIV_DOI,
    PARSPEC_DOI,
    PARSPEC_QEFT_BOUND_KM_90,
    PARSPEC_SOURCE_URL,
    SOURCE_EVENTS,
)


VERSION = "v2.191"
DEFAULT_OUT = Path(
    "experiments/results/v2.191/r4_parspec_qeft_source_asset_audit.json"
)
PARSPEC_EPRINT_URL = "https://arxiv.org/e-print/2205.05132"
PARSPEC_SOURCE_PACKAGE_SHA256 = (
    "11b568f5107b4e31a7efd83b704178e7a9e938467fcd36a4856f53a208b05da2"
)
QEFT_TEX_SHA256 = (
    "e204f46bc95bdbbfaf4ea3fc13675f188d33a70b58363f605f40fd228da7dc0b"
)
QEFT_POSTERIORS_FIGURE_SHA256 = (
    "b41b2847087581da0d7b00ef947f59dfed369a503e512f45a8361e6596cb18b3"
)
QEFT_CDF_FIGURE_SHA256 = (
    "e71d3f19b28558bf0b52d43def1ca5390e1cfcb0fdd482fc556b8ead010f601c"
)
QEFT_POWER = 6
QEFT_EVENT_BOUNDS_KM_90 = {
    "GW150914": 51.7,
    "GW200129": 54.8,
    "combined": PARSPEC_QEFT_BOUND_KM_90,
}
QEFT_PARSPEC_EPSILON_THRESHOLDS = {
    "GW150914": 0.58,
    "GW200129": 0.64,
}
QEFT_QNM_DEFORMATION_COEFFICIENTS = {
    "nmax_0": {
        "delta_omega_qeft_0": -0.2114,
        "delta_tau_qeft_0": -0.6070,
    },
    "nmax_1": {
        "delta_omega_qeft_1": -1.5263,
        "delta_tau_qeft_1": 171.35,
    },
}
SOURCE_PACKAGE_TOP_LEVEL_FILES = (
    "GW150914_intrinsic_params.pdf",
    "GW150914_intrinsic_params_remnant.pdf",
    "ceft_cdf_varying_threshold.pdf",
    "ceft_posteriors_combined.pdf",
    "dcs_cdf_varying_threshold.pdf",
    "dcs_posteriors_combined.pdf",
    "edgb_cdf_varying_threshold.pdf",
    "edgb_gamma.pdf",
    "edgb_posteriors_combined.pdf",
    "example_waveform_cubicEFT.pdf",
    "paper_alt_theory_bounds.bbl",
    "paper_alt_theory_bounds.bib",
    "paper_alt_theory_bounds.tex",
    "qeft_cdf_varying_threshold.pdf",
    "qeft_posteriors_combined.pdf",
)


def parspec_qeft_source_package_assets() -> dict[str, Any]:
    """Record the source package assets that are useful but not sufficient."""

    return {
        "source_url": PARSPEC_SOURCE_URL,
        "source_doi": PARSPEC_DOI,
        "arxiv_doi": PARSPEC_ARXIV_DOI,
        "source_eprint_url": PARSPEC_EPRINT_URL,
        "source_package_tarball": {
            "sha256": PARSPEC_SOURCE_PACKAGE_SHA256,
            "size_bytes": 778370,
        },
        "top_level_files": list(SOURCE_PACKAGE_TOP_LEVEL_FILES),
        "audited_assets": [
            {
                "path": "paper_alt_theory_bounds.tex",
                "kind": "latex_source",
                "size_bytes": 101949,
                "sha256": QEFT_TEX_SHA256,
                "preserved_facts": [
                    "ParSpec gamma relation",
                    "qEFT power p_qEFT = 6",
                    "qEFT QNM deformation coefficients",
                    "GW150914/GW200129/combined qEFT bounds",
                ],
            },
            {
                "path": "qeft_posteriors_combined.pdf",
                "kind": "posterior_figure",
                "size_bytes": 28505,
                "sha256": QEFT_POSTERIORS_FIGURE_SHA256,
                "machine_readable_likelihood": False,
            },
            {
                "path": "qeft_cdf_varying_threshold.pdf",
                "kind": "cdf_figure",
                "size_bytes": 201759,
                "sha256": QEFT_CDF_FIGURE_SHA256,
                "machine_readable_likelihood": False,
            },
        ],
        "detected_machine_readable_likelihood_assets": [],
        "machine_readable_likelihood_ready": False,
        "audit_note": (
            "The arXiv source package contains TeX and figures sufficient to "
            "preserve the qEFT ParSpec power and published bounds, but not a "
            "public posterior-sample file, covariance object, or log-likelihood "
            "grid that can be attached to the engine."
        ),
    }


def qeft_parspec_source_equation_facts() -> dict[str, Any]:
    return {
        "source_refs": {
            "parspec_frequency_expansion": "paper_alt_theory_bounds.tex:639",
            "gamma_definition": "paper_alt_theory_bounds.tex:658-661",
            "qeft_posteriors": "paper_alt_theory_bounds.tex:1673-1685",
            "qeft_event_bounds": "paper_alt_theory_bounds.tex:1697-1702",
            "qeft_figure_caption": "paper_alt_theory_bounds.tex:1728-1738",
            "qeft_coefficients": "paper_alt_theory_bounds.tex:2040-2045",
        },
        "source_axis": SOURCE_AXIS_WITH_UNIT,
        "source_axis_units": SOURCE_AXIS_UNITS,
        "parspec_gamma_relation": {
            "symbol": "gamma",
            "relation": "(ell_th c^2 (1 + z) / (G M_f))^p",
            "qeft_power": QEFT_POWER,
            "status": "source_backed_for_parspec_deformation",
            "engine_r4_axis_normalization_ready": False,
        },
        "qnm_deformation_coefficients": QEFT_QNM_DEFORMATION_COEFFICIENTS,
        "event_bounds_90_credible_km": QEFT_EVENT_BOUNDS_KM_90,
        "parspec_epsilon_thresholds": QEFT_PARSPEC_EPSILON_THRESHOLDS,
        "event_set": list(SOURCE_EVENTS),
        "source_axis_power_policy_ready": True,
        "ringdown_qnm_deformation_coefficients_ready": True,
    }


def qeft_source_axis_power_policy() -> dict[str, Any]:
    facts = qeft_parspec_source_equation_facts()
    return {
        "status": "source_backed",
        "length_axis": SOURCE_AXIS_WITH_UNIT,
        "length_power_declared": True,
        "length_power": facts["parspec_gamma_relation"]["qeft_power"],
        "power_scope": (
            "ParSpec qEFT ringdown deformation power only; not a completed "
            "Bresciani engine R4-axis operator map."
        ),
        "gamma_relation": facts["parspec_gamma_relation"]["relation"],
        "source_refs": [
            facts["source_refs"]["gamma_definition"],
            facts["source_refs"]["qeft_coefficients"],
        ],
    }


def v2191_asset_enriched_parspec_axis_map_slot(
    path: str | Path = DEFAULT_V2188_PATH,
) -> dict[str, Any]:
    packet = current_v2188_parspec_axis_map_slot(path)
    packet["packet_id"] = "v2191_asset_enriched_parspec_qeft_axis_map_slot"
    packet["source_axis_power_policy"] = qeft_source_axis_power_policy()
    packet["source_asset_audit"] = {
        "status": "primary_source_package_audited",
        "source_package_sha256": PARSPEC_SOURCE_PACKAGE_SHA256,
        "qeft_tex_sha256": QEFT_TEX_SHA256,
        "qeft_posterior_figure_sha256": QEFT_POSTERIORS_FIGURE_SHA256,
    }
    return packet


def diagnose_r4_parspec_qeft_source_asset_audit(
    *,
    v2188_path: str | Path = DEFAULT_V2188_PATH,
) -> dict[str, Any]:
    baseline_packet = current_v2188_parspec_axis_map_slot(v2188_path)
    enriched_packet = v2191_asset_enriched_parspec_axis_map_slot(v2188_path)
    baseline = evaluate_parspec_engine_axis_map_packet(baseline_packet)
    enriched = evaluate_parspec_engine_axis_map_packet(enriched_packet)
    resolved_blockers = sorted(
        set(baseline["all_blockers"]) - set(enriched["all_blockers"])
    )

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.188_r4_parspec_ringdown_source_bridge",
            "v2.189_r4_research_continuity_ledger",
            "v2.190_r4_parspec_engine_axis_map_contract",
            "Silva_Ghosh_Buonanno_2023_arxiv_source_package",
        ],
        "source_package_assets": parspec_qeft_source_package_assets(),
        "source_equation_facts": qeft_parspec_source_equation_facts(),
        "v2191_asset_enriched_packet": enriched_packet,
        "baseline_v2188_evaluation": baseline,
        "v2191_asset_enriched_evaluation": enriched,
        "resolved_v2190_contract_blockers": resolved_blockers,
        "source_asset_readiness": {
            "source_package_assets_ready": True,
            "source_axis_power_policy_ready": (
                "source_axis_power_policy_missing" in resolved_blockers
            ),
            "ringdown_qnm_deformation_coefficients_ready": True,
            "published_bound_and_figure_assets_ready": True,
            "machine_readable_likelihood_ready": False,
            "operator_basis_map_ready": False,
            "engine_bresciani_axis_orientation_ready": False,
            "event_set_aligned_with_current_engine_run": (
                CURRENT_V2187_EVENT in SOURCE_EVENTS
            ),
            "claim_grade_systematics_export_ready": False,
        },
        "remaining_contract_blockers_after_asset_audit": enriched["all_blockers"],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": "parspec_qeft_source_asset_audit_ready_nonclaiming",
        "selected_next_build_action": (
            "derive_qeft_to_bresciani_engine_axis_map_or_acquire_public_likelihood_grid"
        ),
        "interpretation": (
            "The arXiv source package resolves the v2.190 source-axis power "
            "policy blocker by recording p_qEFT = 6 and the qEFT ringdown "
            "coefficients. It does not provide a machine-readable likelihood, "
            "does not align the current engine GW170608 run with GW150914/"
            "GW200129, and does not map the ParSpec qEFT length axis onto "
            "engine-normalized Bresciani R4 axes."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2188", default=str(DEFAULT_V2188_PATH))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_qeft_source_asset_audit(
        v2188_path=Path(args.v2188)
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
