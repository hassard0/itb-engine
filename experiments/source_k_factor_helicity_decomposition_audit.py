"""Audit the source K-factor needed for the R4 helicity decomposition."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.140"


def k_factor_source_status_rows() -> list[dict[str, Any]]:
    return [
        {
            "source_id": "russo_1997_type_iib_four_graviton",
            "url": "https://arxiv.org/abs/hep-th/9707241",
            "evidence_ref": "lines around tree-level A4 = kappa^2 K A4^0",
            "status": "k_factor_referenced_not_defined_locally",
            "provides_local_k_formula": False,
            "provides_low_energy_r4_contact_factor": True,
            "provides_helicity_decomposition": False,
            "blocker": "source_k_factor_not_local_in_russo",
            "interpretation": (
                "Russo supplies the low-energy R4 contact expansion, but "
                "refers K back to the usual Gross-Witten kinematic factor."
            ),
        },
        {
            "source_id": "gross_witten_1986",
            "url": "https://doi.org/10.1016/0550-3213(86)90429-3",
            "evidence_ref": "usual kinematic factor cited by Russo",
            "status": "primary_k_factor_source_not_ingested",
            "provides_local_k_formula": False,
            "provides_low_energy_r4_contact_factor": True,
            "provides_helicity_decomposition": False,
            "blocker": "gross_witten_kinematic_factor_definition_not_ingested",
            "interpretation": (
                "This is the likely primary location of K, but the current "
                "repo has not ingested a machine-checkable K expression."
            ),
        },
        {
            "source_id": "peeters_vanhove_westerberg_2001",
            "url": "https://arxiv.org/abs/hep-th/0010167",
            "evidence_ref": (
                "amplitude appendix notes ignored overall normalisations"
            ),
            "status": "tensor_structures_without_r4_helicity_normalization",
            "provides_local_k_formula": False,
            "provides_low_energy_r4_contact_factor": False,
            "provides_helicity_decomposition": False,
            "blocker": "amplitude_normalization_missing_in_tensor_source",
            "interpretation": (
                "The source gives useful tensor structures, but not the "
                "normalised four-dimensional K_plus/K_minus decomposition."
            ),
        },
        {
            "source_id": "peeters_weyl_projection_warning",
            "url": "https://arxiv.org/abs/hep-th/0010167",
            "evidence_ref": "Riemann_decompose, Weylprojop, t8t8_not_automatically_Weyl",
            "status": "weyl_projection_policy_required",
            "provides_local_k_formula": False,
            "provides_low_energy_r4_contact_factor": False,
            "provides_helicity_decomposition": False,
            "blocker": "weyl_projection_and_eom_policy_missing",
            "interpretation": (
                "The source explicitly warns that t8t8R4 does not "
                "automatically project onto Weyl/Ricci-flat terms, so a "
                "four-dimensional on-shell policy is required before matching."
            ),
        },
    ]


def required_k_decomposition_inputs() -> list[dict[str, Any]]:
    return [
        {
            "input": "machine_checkable_K_formula",
            "status": "missing",
            "blocker": "gross_witten_kinematic_factor_definition_not_ingested",
        },
        {
            "input": "polarization_to_spinor_helicity_dictionary",
            "status": "partially_sourced",
            "blocker": "source_K_spinor_helicity_projection_missing",
        },
        {
            "input": "four_dimensional_weyl_or_riemann_policy",
            "status": "missing",
            "blocker": "weyl_projection_and_eom_policy_missing",
        },
        {
            "input": "overall_R4_normalization",
            "status": "missing",
            "blocker": "engine_lambda_r4_normalization_missing",
        },
        {
            "input": "K_plus_and_K_minus_components",
            "status": "missing",
            "blocker": "source_K_plus_K_minus_components_missing",
        },
    ]


def decomposition_routes() -> list[dict[str, Any]]:
    return [
        {
            "route": "ingest_primary_k_factor",
            "status": "preferred_next",
            "needed_artifact": (
                "A parsed Gross-Witten K expression with source line/figure "
                "metadata and no manual transcription ambiguity."
            ),
            "risk": "paywall_or_scan_quality",
        },
        {
            "route": "rederive_k_from_polarization_tensors",
            "status": "fallback_parallel_route",
            "needed_artifact": (
                "A symbolic polarization-to-spinor-helicity derivation that "
                "projects t8t8R4/Weyl4 onto Bresciani monomials."
            ),
            "risk": "normalization_and_field_redefinition_ambiguity",
        },
    ]


def diagnose_source_k_factor_helicity_decomposition_audit() -> dict[str, Any]:
    rows = k_factor_source_status_rows()
    inputs = required_k_decomposition_inputs()
    blockers = sorted({
        row["blocker"] for row in rows
        if row["blocker"] is not None
    } | {
        row["blocker"] for row in inputs
        if row["blocker"] is not None
    })
    local_k_sources = [
        row["source_id"] for row in rows
        if row["provides_local_k_formula"]
    ]
    helicity_sources = [
        row["source_id"] for row in rows
        if row["provides_helicity_decomposition"]
    ]
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.139_four_dimensional_r4_projection_derivation_workbench",
            "v2.138_string_r4_helicity_source_equation_audit",
            "Russo_Gross_Witten_K_factor_trail",
        ],
        "k_factor_source_status_rows": rows,
        "required_k_decomposition_inputs": inputs,
        "decomposition_routes": decomposition_routes(),
        "machine_checkable_k_formula_sources": local_k_sources,
        "source_backed_helicity_decomposition_sources": helicity_sources,
        "can_solve_k_decomposition_now": bool(local_k_sources and helicity_sources),
        "current_blockers": blockers,
        "claimable_framework_exclusions_now": [],
        "route_status": "source_k_factor_helicity_decomposition_blocked_on_k_formula",
        "selected_next_build_action": (
            "ingest_gross_witten_kinematic_factor_or_rederive_from_polarizations"
        ),
        "best_next_artifact": (
            "A machine-checkable K-factor expression, either ingested from "
            "Gross-Witten or independently rederived from polarization tensors, "
            "so v2.139 can compute K_plus and complex K_minus."
        ),
        "interpretation": (
            "The R4 projection route is now blocked at a precise source object: "
            "the normalised four-graviton kinematic factor K and its "
            "four-dimensional spinor-helicity decomposition. Russo supplies "
            "the low-energy R4 contact coefficient but not K itself."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.140/"
            "source_k_factor_helicity_decomposition_audit.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_source_k_factor_helicity_decomposition_audit()
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
