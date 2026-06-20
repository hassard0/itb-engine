"""Open-source rederivation of the Virasoro-Shapiro/Russo R4 K bridge."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.string_r4_normalization_bridge import RUSSO_TREE_R4_CONTACT_SCALAR


VERSION = "v2.153"


def open_source_formula_inputs() -> list[dict[str, Any]]:
    return [
        {
            "source_id": "russo_1997_type_iib_four_graviton",
            "url": "https://arxiv.org/abs/hep-th/9707241",
            "formula_role": "open Virasoro-Shapiro scalar expansion",
            "statements": [
                "A4 = kappa^2 * K * A4^0",
                "sbar = alpha_prime * s / 4",
                "A4^0 = 1/(sbar*tbar*ubar) + 2*zeta(3) + ...",
            ],
            "machine_usable": True,
        },
        {
            "source_id": "kallosh_lee_rube_2008_tree_gravity_shape",
            "url": "https://arxiv.org/abs/0811.3417",
            "formula_role": "tree helicity pole normalization comparator",
            "statements": [
                "M_tree(1-,2-,3+,4+) = shape/(kappa^2*s*t*u)",
                "v2.144 maps the R4 shape to K_plus=1 and K_minus=0",
            ],
            "machine_usable": True,
        },
        {
            "source_id": "bresciani_levati_paradisi_2025_target_basis",
            "url": "https://arxiv.org/abs/2504.12855",
            "formula_role": "target R4 coordinate basis",
            "statements": [
                "S=2 target amplitude has 8*c_plus and 8*c_minus channels",
                "v2.144 source shape gives c_plus=1 and c_minus=0 under the engine unit policy",
            ],
            "machine_usable": True,
        },
    ]


def rederive_raw_k_bridge() -> dict[str, Any]:
    return canonicalize_json_floats({
        "massless_barred_variables": {
            "sbar": "alpha_prime*s/4",
            "tbar": "alpha_prime*t/4",
            "ubar": "alpha_prime*u/4",
            "sbar_tbar_ubar_product": (
                "alpha_prime^3*s*t*u/64"
            ),
        },
        "russo_pole_term": {
            "A4_string_pole": (
                "kappa^2*K_Russo*64/(alpha_prime^3*s*t*u)"
            ),
            "A4_r4_contact": "kappa^2*K_Russo*2*zeta(3)",
            "contact_scalar": RUSSO_TREE_R4_CONTACT_SCALAR,
        },
        "kallosh_tree_comparator": {
            "M_tree_helicity": "shape/(kappa^2*s*t*u)",
        },
        "pole_match_equation": (
            "kappa^2*K_Russo*64/alpha_prime^3 = shape/kappa^2"
        ),
        "derived_bridge": {
            "K_Russo_over_shape": "alpha_prime^3/(64*kappa^4)",
            "alpha_prime_set_to_one_control": "1/(64*kappa^4)",
            "reproduces_v2_146_raw_bridge": True,
        },
        "derived_r4_contact_after_pole_match": {
            "expression": (
                "2*zeta(3)*alpha_prime^3*shape/(64*kappa^2)"
            ),
            "engine_unit_status": "not_engine_lambda_r4_defined",
        },
    })


def evaluate_rederived_k_bridge() -> dict[str, Any]:
    bridge = rederive_raw_k_bridge()
    blockers = {
        "bridge_depends_on_kappa_convention",
        "bridge_depends_on_alpha_prime_units",
        "engine_lambda_r4_unit_conversion_missing",
        "amplitude_normalization_conventions_not_unified",
    }
    criteria = {
        "source_backed_open_rederivation": True,
        "reproduces_russo_low_energy_scalar": True,
        "reproduces_v2_146_raw_pole_bridge": True,
        "dimensionless_against_v2_144_shape": False,
        "independent_of_gravitational_coupling_convention": False,
        "engine_lambda_r4_unit_conversion_source_backed": False,
        "ready_for_framework_claim": False,
    }
    failed = [
        criterion for criterion, passed in criteria.items() if passed is not True
    ]
    return canonicalize_json_floats({
        "bridge": bridge,
        "criteria": criteria,
        "failed_criteria": failed,
        "acceptable_absolute_k_bridge": False,
        "claim_ready_now": False,
        "blockers": sorted(blockers),
        "interpretation": (
            "The open-source rederivation reproduces the v2.146 raw pole "
            "bridge with alpha_prime restored. That is progress, but it also "
            "proves the candidate is not yet an engine Wilson normalization: "
            "it still carries kappa and alpha-prime convention dependence."
        ),
    })


def diagnose_virasoro_shapiro_k_bridge_rederivation() -> dict[str, Any]:
    evaluation = evaluate_rederived_k_bridge()
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.152_gross_witten_source_access_probe",
            "v2.146_k_convention_bridge_audit",
            "Russo_arXiv_hep_th_9707241",
            "Kallosh_Lee_Rube_arXiv_0811_3417",
        ],
        "source_formula_inputs": open_source_formula_inputs(),
        "evaluation": evaluation,
        "claimable_framework_exclusions_now": [],
        "ready_to_claim_now": False,
        "route_status": (
            "open_virasoro_shapiro_rederivation_rejects_absolute_k_bridge"
        ),
        "selected_next_build_action": (
            "define_or_source_engine_lambda_r4_alpha_prime_policy"
        ),
        "best_next_artifact": (
            "A source-backed or explicit non-claiming policy for translating "
            "alpha_prime^3/kappa^2 factors into the engine Lambda_R4 axis. "
            "Without that, the R4 packet stays internal-only."
        ),
        "interpretation": (
            "The Gross-Witten file access blocker has been bypassed for the "
            "scalar low-energy expansion: Russo plus Kallosh are sufficient to "
            "rederive the raw bridge. The result is still not claimable because "
            "the bridge is alpha-prime and kappa convention dependent."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.153/"
            "virasoro_shapiro_k_bridge_rederivation.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_virasoro_shapiro_k_bridge_rederivation()
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
