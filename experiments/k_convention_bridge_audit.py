"""Audit candidate K-convention bridges for the string R4 normalization."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.146"


def k_bridge_acceptance_criteria() -> list[str]:
    return [
        "source_backed_primary_or_rederived",
        "dimensionless_against_v2_144_shape",
        "independent_of_gravitational_coupling_convention",
        "compatible_with_russo_barred_mandelstam_definition",
        "compatible_with_kallosh_bresciani_bracket_bridge",
    ]


def candidate_k_bridges() -> list[dict[str, Any]]:
    return [
        {
            "candidate": "match_supergravity_pole_raw",
            "source_inputs": [
                "Russo: A4 = kappa^2 K A4^0",
                "Russo: A4^0 = 1/(sbar*tbar*ubar) + 2*zeta(3) + ...",
                "Russo: sbar = alpha_prime*s/4",
                "Kallosh: M_tree(1-,2-,3+,4+) = shape/(kappa^2*s*t*u)",
            ],
            "assumptions": [
                "alpha_prime = 1",
                "Russo and Kallosh amplitude normalizations are directly comparable",
            ],
            "candidate_expression": "K_Russo / shape = 1/(64*kappa^4)",
            "source_backed_primary_or_rederived": True,
            "dimensionless_against_v2_144_shape": False,
            "independent_of_gravitational_coupling_convention": False,
            "compatible_with_russo_barred_mandelstam_definition": True,
            "compatible_with_kallosh_bresciani_bracket_bridge": True,
            "blockers": [
                "bridge_depends_on_kappa_convention",
                "bridge_not_dimensionless_against_shape",
                "amplitude_normalization_conventions_not_unified",
            ],
            "interpretation": (
                "Matching the pole identifies the convention problem but does "
                "not produce a usable dimensionless K bridge."
            ),
        },
        {
            "candidate": "unit_shape_bridge",
            "source_inputs": [
                "v2.144: Kallosh/Bresciani shape has K_plus=1 and K_minus=0",
            ],
            "assumptions": [
                "Define K_Russo equal to the v2.144 shape by convention",
            ],
            "candidate_expression": "K_Russo / shape = 1",
            "source_backed_primary_or_rederived": False,
            "dimensionless_against_v2_144_shape": True,
            "independent_of_gravitational_coupling_convention": True,
            "compatible_with_russo_barred_mandelstam_definition": False,
            "compatible_with_kallosh_bresciani_bracket_bridge": True,
            "blockers": [
                "bridge_is_engine_convention_not_source_backed",
                "russo_k_formula_not_ingested",
            ],
            "interpretation": (
                "This is useful as an internal convention control but cannot "
                "stand in for a source-backed K bridge."
            ),
        },
        {
            "candidate": "gross_witten_primary_k_formula",
            "source_inputs": [
                "Gross-Witten DOI/CERN record identified in v2.141",
            ],
            "assumptions": [
                "The primary article contains an explicit K formula",
                "The formula can be OCR/library-ingested without ambiguity",
            ],
            "candidate_expression": None,
            "source_backed_primary_or_rederived": False,
            "dimensionless_against_v2_144_shape": False,
            "independent_of_gravitational_coupling_convention": False,
            "compatible_with_russo_barred_mandelstam_definition": False,
            "compatible_with_kallosh_bresciani_bracket_bridge": False,
            "blockers": [
                "primary_k_formula_not_ingested",
                "gross_witten_pdf_or_ocr_still_required",
            ],
            "interpretation": (
                "This remains the cleanest route if a machine-checkable "
                "primary K expression can be obtained."
            ),
        },
    ]


def evaluate_k_bridge_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    criteria = k_bridge_acceptance_criteria()
    failed = [
        criterion for criterion in criteria
        if candidate.get(criterion) is not True
    ]
    blockers = set(candidate.get("blockers", []))
    blockers.update(f"{criterion}_failed" for criterion in failed)
    return canonicalize_json_floats({
        "candidate": candidate["candidate"],
        "candidate_expression": candidate.get("candidate_expression"),
        "criteria": {
            criterion: candidate.get(criterion) is True
            for criterion in criteria
        },
        "failed_criteria": failed,
        "acceptable_k_bridge": not failed and not blockers,
        "blockers": sorted(blockers),
        "interpretation": candidate["interpretation"],
    })


def diagnose_k_convention_bridge_audit() -> dict[str, Any]:
    candidates = candidate_k_bridges()
    evaluations = {
        candidate["candidate"]: evaluate_k_bridge_candidate(candidate)
        for candidate in candidates
    }
    acceptable = [
        label for label, row in evaluations.items()
        if row["acceptable_k_bridge"]
    ]
    blockers = sorted({
        blocker
        for row in evaluations.values()
        for blocker in row["blockers"]
    })
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.145_string_r4_normalization_bridge",
            "v2.144_supersymmetric_r4_shape_projection",
            "Russo_arXiv_hep-th_9707241_A4_expansion",
            "Kallosh_Lee_Rube_arXiv_0811_3417_tree_and_R4_helicity_amplitudes",
        ],
        "k_bridge_acceptance_criteria": k_bridge_acceptance_criteria(),
        "candidate_k_bridges": candidates,
        "evaluations": evaluations,
        "acceptable_k_bridge_candidates": acceptable,
        "current_blockers": blockers,
        "claimable_framework_exclusions_now": [],
        "route_status": "k_convention_bridge_candidates_audited_no_acceptable_bridge",
        "selected_next_build_action": (
            "ingest_primary_k_formula_or_define_engine_shape_normalization_convention"
        ),
        "best_next_artifact": (
            "Either a machine-checkable Gross-Witten K expression, or an "
            "explicit engine policy that intentionally treats the v2.144 "
            "Kallosh/Bresciani shape as the normalized K unit while keeping "
            "absolute string-scale claims disabled."
        ),
        "interpretation": (
            "The supergravity-pole comparison is not enough: it produces a "
            "bridge proportional to kappa^-4, so it has not unified the source "
            "amplitude conventions into the dimensionless K bridge required "
            "by v2.145. The repo therefore still must ingest the primary K "
            "formula or add an explicit non-claiming engine convention."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.146/k_convention_bridge_audit.json",
    )
    args = parser.parse_args()

    result = diagnose_k_convention_bridge_audit()
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
