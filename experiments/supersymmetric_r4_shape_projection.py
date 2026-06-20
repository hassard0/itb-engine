"""Project a source-backed supersymmetric R4 helicity shape into Bresciani axes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.bresciani_k_monomial_projector import (
    K_MINUS_CONJUGATE_MONOMIALS,
    K_MINUS_MONOMIALS,
    K_PLUS_MONOMIALS,
    project_bresciani_k_components,
)
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.polarization_k_factor_rederivation_route import (
    evaluate_k_rederivation_packet,
)


VERSION = "v2.144"

KALLOSH_SOURCE_SHA256 = (
    "e78d7380d7e80bb8c3b293b5c9546653344696c5b08e806e479699be730089f3"
)
BRESCIANI_SOURCE_SHA256 = (
    "393c41cd748ff5ba2e21f2113860cce3d3970646c2ae6d1ba24cb749e92c53ed"
)


def source_evidence() -> dict[str, Any]:
    return {
        "kallosh_lee_rube_2008": {
            "url": "https://arxiv.org/abs/0811.3417",
            "source_tarball_sha256": KALLOSH_SOURCE_SHA256,
            "equation_refs": [
                "November20.tex:Omega4",
                "November20.tex:P3-loop_UV",
                "November20.tex:Omega",
                "November20.tex:M_UV_3-loop",
            ],
            "source_facts": [
                (
                    "The N=8 four-point generating function carries a "
                    "degree-16 eta delta/product structure."
                ),
                (
                    "Positive-helicity gravitons are extracted by the identity "
                    "operator, while negative-helicity gravitons require eight "
                    "eta derivatives."
                ),
                (
                    "The Bel-Robinson-square R4 counterterm component is "
                    "M_UV(1-,2-,3+,4+) = kappa^4 <12>^4 [34]^4 in the "
                    "paper's bracket convention."
                ),
                (
                    "The paper's angle bracket is built from tilde-lambda and "
                    "therefore maps to Bresciani's square bracket; the paper's "
                    "square bracket maps to Bresciani's angle bracket."
                ),
            ],
        },
        "bresciani_levati_paradisi_2025": {
            "url": "https://arxiv.org/abs/2504.12855",
            "source_tarball_sha256": BRESCIANI_SOURCE_SHA256,
            "equation_refs": [
                "letter.tex:eq:Lag-quartic",
                "letter.tex:eq:amplitude",
                "letter.tex:c_plus_c_minus_definitions",
            ],
            "source_facts": [
                (
                    "The S=2 target amplitude has three equal c_plus monomial "
                    "channels and chiral c_minus/conjugate families."
                ),
                (
                    "For the Bresciani normalization, each target matrix entry "
                    "contains an explicit factor of 8 multiplying c_plus or "
                    "c_minus."
                ),
            ],
        },
    }


def kallosh_bresciani_shape_packet() -> dict[str, Any]:
    coefficients: dict[str, float] = {}
    for monomial in K_PLUS_MONOMIALS:
        coefficients[monomial] = 1.0
    for monomial in K_MINUS_MONOMIALS:
        coefficients[monomial] = 0.0
    for monomial in K_MINUS_CONJUGATE_MONOMIALS:
        coefficients[monomial] = 0.0

    return {
        "label": "kallosh_n8_r4_shape_packet",
        "source_urls": [
            "https://arxiv.org/abs/0811.3417",
            "https://arxiv.org/abs/2504.12855",
        ],
        "source_equation_refs": {
            "kallosh_lee_rube_2008": [
                "Omega4",
                "P3-loop_UV",
                "Omega",
                "M_UV_3-loop",
            ],
            "bresciani_levati_paradisi_2025": [
                "eq:amplitude",
                "c_plus_c_minus_definitions",
            ],
        },
        "source_backed_derivation": True,
        "derivation_scope": (
            "R4 helicity shape of the maximally supersymmetric "
            "Bel-Robinson-square counterterm; not the absolute type-II "
            "string alpha-prime coefficient."
        ),
        "derivation_steps": [
            {
                "step": "map_kallosh_component_to_bresciani_monomial",
                "input": "M_UV(1-,2-,3+,4+) = kappa^4 <12>^4 [34]^4",
                "bracket_policy": (
                    "Kallosh angle = Bresciani square; Kallosh square = "
                    "Bresciani angle."
                ),
                "output": "angle34^4_square12^4 has unit K_plus coefficient",
            },
            {
                "step": "extend_by_permutation_and_bresciani_target_symmetry",
                "input": (
                    "Kallosh P^L is symmetric in four points and Bresciani's "
                    "eq:amplitude gives one common c_plus coefficient."
                ),
                "output": "all K_plus monomial-family coefficients are 1",
            },
            {
                "step": "exclude_chiral_k_minus_shape",
                "input": (
                    "The source superamplitude has degree 16 in eta; all-plus "
                    "requires zero derivatives and all-minus requires 32."
                ),
                "output": "K_minus and conjugate monomial-family coefficients are 0",
            },
        ],
        "monomial_coefficients": coefficients,
        "normalization": {
            "overall_R4_factor": 8.0,
            "normalization_scope": "Bresciani unit shape: c_plus=1, c_minus=0",
            "absolute_string_alpha_prime_normalization_backed": False,
            "absolute_normalization_blocker": (
                "Gross-Witten/Russo fixes the string R4 coefficient trail, "
                "but the absolute engine Lambda_R4 normalization remains "
                "separate from this helicity-shape projection."
            ),
        },
    }


def kallosh_rederivation_packet() -> dict[str, Any]:
    shape = kallosh_bresciani_shape_packet()
    return {
        "label": "kallosh_n8_r4_rederivation_shape_packet",
        "source_urls": shape["source_urls"],
        "source_equation_refs": shape["source_equation_refs"],
        "four_dimensional_policy": "four_dimensional_on_shell_weyl_ricci_flat",
        "polarization_dictionary": {
            "kallosh_angle": "bresciani_square_tilde_lambda",
            "kallosh_square": "bresciani_angle_lambda",
            "negative_helicity_graviton": "eight_eta_derivatives",
            "positive_helicity_graviton": "identity_operator",
        },
        "source_k_formula": {
            "status": "source_backed_r4_shape",
            "formula": "K_shape = K_plus, K_plus=1, K_minus=0",
            "source_component": (
                "M_UV(1-,2-,3+,4+) = kappa^4 <12>^4 [34]^4"
            ),
            "scope": shape["derivation_scope"],
        },
        "helicity_components": {
            "K_plus": 1.0,
            "K_minus_real": 0.0,
            "K_minus_imag": 0.0,
        },
        "normalization": shape["normalization"],
        "source_backed_derivation": True,
    }


def diagnose_supersymmetric_r4_shape_projection() -> dict[str, Any]:
    shape_packet = kallosh_bresciani_shape_packet()
    projector = project_bresciani_k_components(shape_packet)
    rederivation = evaluate_k_rederivation_packet(kallosh_rederivation_packet())
    absolute_norm_backed = shape_packet["normalization"][
        "absolute_string_alpha_prime_normalization_backed"
    ]
    ready_for_framework_claim = (
        projector["ready_for_k_factor_projection"]
        and rederivation["ready_for_k_factor_projection"]
        and absolute_norm_backed
    )

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.143_bresciani_k_monomial_projector",
            "v2.142_polarization_k_factor_rederivation_route",
            "Kallosh_Lee_Rube_arXiv_0811_3417_N8_R4_helicity_counterterm",
            "Bresciani_Levati_Paradisi_arXiv_2504_12855_eq_amplitude",
        ],
        "source_evidence": source_evidence(),
        "shape_packet": shape_packet,
        "projector_evaluation": projector,
        "rederivation_evaluation": rederivation,
        "resolved_gap_this_iteration": [
            "source_backed_K_plus_monomial_shape",
            "source_backed_K_minus_zero_for_maximally_supersymmetric_R4_shape",
        ],
        "remaining_normalization_gaps": [
            "absolute_type_II_string_alpha_prime_R4_coefficient",
            "engine_Lambda_R4_unit_conversion",
        ],
        "ready_for_framework_claim": ready_for_framework_claim,
        "claimable_framework_exclusions_now": [],
        "route_status": (
            "supersymmetric_r4_shape_projected_string_normalization_open"
        ),
        "selected_next_build_action": (
            "normalize_supersymmetric_r4_shape_to_string_alpha_prime_units"
        ),
        "best_next_artifact": (
            "A source-backed conversion from the Kallosh/Russo/Gross-Witten "
            "R4 coefficient convention into the engine Lambda_R4 convention."
        ),
        "interpretation": (
            "A source-backed helicity shape now reaches the Bresciani projector: "
            "K_plus=1 and K_minus=0 for the maximally supersymmetric R4 "
            "Bel-Robinson-square shape. This is a real projection result, but "
            "not yet a quantum-gravity discriminator because the absolute "
            "string/engine normalization is still open."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.144/"
            "supersymmetric_r4_shape_projection.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_supersymmetric_r4_shape_projection()
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
