"""GW parity PPV/helicity convention audit (v2.70).

This artifact separates source-declared PPV candidate mappings from promotion.
It records where Ng/Jenks/Callister conventions already line up and where a
single, engine-owned beta likelihood is still blocked.
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
from itb.gw_parity import GW_PARITY_PROJECTION_BLOCKERS


def _row(
    *,
    label: str,
    source_packet: str,
    source_urls: dict[str, str],
    source_formulas: list[str],
    source_declared_mapping: dict[str, Any],
    helicity_conventions: dict[str, str],
    readiness: dict[str, bool],
    blockers: list[str],
    notes: list[str],
) -> dict[str, Any]:
    return {
        "label": label,
        "source_packet": source_packet,
        "source_urls": source_urls,
        "source_formulas": source_formulas,
        "source_declared_mapping": source_declared_mapping,
        "helicity_conventions": helicity_conventions,
        "readiness": {
            **readiness,
            "engine_projection_ready": False,
            "claim_ready": False,
        },
        "engine_projection_allowed": False,
        "blockers": sorted(set(blockers)),
        "notes": notes,
    }


def convention_audit_rows() -> list[dict[str, Any]]:
    shared_projection_blockers = list(GW_PARITY_PROJECTION_BLOCKERS)
    return [
        _row(
            label="ng_kappa_to_jenks_beta10_candidate",
            source_packet="ng_gwtc3_kappa_at_100hz",
            source_urls={
                "ng_paper": "https://arxiv.org/abs/2305.05844",
                "jenks_ppv": "https://arxiv.org/abs/2305.10478",
                "ng_repository": (
                    "https://github.com/thomasckng/"
                    "Constraining-Birefringence-with-GWTC-3"
                ),
            },
            source_formulas=[
                "Ng: h_L/R^br = h_L/R^GR * exp(+/- kappa*d_C*f/100Hz)",
                "Ng: positive kappa enhances left-handed polarization.",
                "Jenks: delta_phi_A = kappa*D_C*(f/100Hz) is encoded in beta_1_0.",
                "Jenks: D_2*(1+z)=D_C for the Ng frequency and distance dependence.",
            ],
            source_declared_mapping={
                "target_ppv_parameter": "beta_1_0_amplitude_branch",
                "source_declares_ng_mapping": True,
                "formula_candidate_ready": True,
                "candidate_formula": (
                    "delta_phi_A = kappa_Gpc_inv*D_C_Gpc*(f_hz/100)"
                ),
                "posterior_product_ready_in_engine": False,
            },
            helicity_conventions={
                "ng": "positive_kappa_enhances_left",
                "jenks": "lambda_R=+1_lambda_L=-1",
                "harmonization_status": "sign_map_still_nonpromoting",
            },
            readiness={
                "source_declared_ppv_mapping_ready": True,
                "posterior_ingestion_ready": False,
                "helicity_harmonization_ready": False,
                "ppv_beta1_likelihood_ready": False,
            },
            blockers=[
                "ng_public_posterior_parser_not_implemented",
                "source_declared_beta10_not_engine_axis",
                *shared_projection_blockers,
            ],
            notes=[
                "This is the strongest current PPV candidate route.",
                "The source-declared beta mapping is not an engine likelihood.",
            ],
        ),
        _row(
            label="callister_waveform_alpha1_beta1_split_candidate",
            source_packet="callister_sgwb_kappaD_kappaz",
            source_urls={
                "callister_paper": "https://arxiv.org/abs/2312.12532",
                "jenks_ppv": "https://arxiv.org/abs/2305.10478",
                "callister_repository": (
                    "https://github.com/tcallister/stochastic-birefringence"
                ),
            },
            source_formulas=[
                "Callister: v_p = pi*(f/100Hz)*(kappa_z*z + kappa_D*D_C/Gpc).",
                "Callister: kappa_z corresponds to alpha_1 and kappa_D to beta_1.",
                "Callister: right-polarized waves are enhanced in the phenomenological approach.",
            ],
            source_declared_mapping={
                "target_ppv_parameters": [
                    "alpha_1_redshift_branch",
                    "beta_1_distance_branch",
                ],
                "source_declares_alpha_beta_split": True,
                "formula_candidate_ready": True,
                "candidate_formula": (
                    "v_p = pi*(f_hz/100)*(kappa_z*z + kappa_D*D_C_Gpc)"
                ),
                "single_beta1_likelihood_ready": False,
            },
            helicity_conventions={
                "callister": "positive_vp_enhances_right",
                "jenks": "lambda_R=+1_lambda_L=-1",
                "harmonization_status": "right_left_sign_not_combined_with_ng",
            },
            readiness={
                "source_declared_ppv_mapping_ready": True,
                "posterior_ingestion_ready": True,
                "helicity_harmonization_ready": False,
                "ppv_beta1_likelihood_ready": False,
            },
            blockers=[
                "redshift_term_not_beta1_distance_only",
                "two_axis_alpha1_beta1_not_single_beta1",
                "population_model_sensitivity_present",
                *shared_projection_blockers,
            ],
            notes=[
                "The Callister waveform-level formula is source-backed.",
                "It is a two-axis alpha/beta route, not the same object as the Ng-only beta route.",
            ],
        ),
        _row(
            label="callister_public_code_energy_density_convention",
            source_packet="callister_sgwb_kappaD_kappaz_energy_density",
            source_urls={
                "callister_paper": "https://arxiv.org/abs/2312.12532",
                "callister_code": (
                    "https://github.com/tcallister/stochastic-birefringence/"
                    "blob/main/code/numpyro_likelihoods.py"
                ),
            },
            source_formulas=[
                "Paper: SGWB Stokes I/V use cosh(2*v_p) and sinh(2*v_p).",
                "Code: A = 2*pi*(kappa_Dc*Dcs_fs + kappa_z*zs_fs)/100.",
                "Code: Omg_I weights multiply by cosh(A); Omg_V weights multiply by sinh(A).",
            ],
            source_declared_mapping={
                "target_quantity": "sgwb_energy_density_hyperbolic_argument",
                "code_argument_matches_2vp": True,
                "formula_candidate_ready": True,
                "candidate_formula": (
                    "A = 2*pi*(kappa_Dc*D_C_Gpc*f_hz + kappa_z*z*f_hz)/100"
                ),
                "waveform_ppv_beta_parameter_ready": False,
            },
            helicity_conventions={
                "callister_code": "positive_A_gives_positive_Stokes_V",
                "waveform": "A_is_energy_density_argument_not_waveform_log_gain",
                "harmonization_status": "energy_sign_not_a_standalone_ppv_beta",
            },
            readiness={
                "source_declared_ppv_mapping_ready": False,
                "posterior_ingestion_ready": True,
                "helicity_harmonization_ready": False,
                "ppv_beta1_likelihood_ready": False,
            },
            blockers=[
                "energy_density_argument_not_waveform_beta_parameter",
                "public_code_matches_energy_argument_not_waveform_log_gain",
                "no_posterior_to_waveform_ppv_likelihood_map",
                *shared_projection_blockers,
            ],
            notes=[
                "This row protects the factor-of-two distinction between waveform log gain and SGWB energy density.",
                "It is implementation-ready as code convention, not as a PPV promotion route.",
            ],
        ),
    ]


def diagnose_gw_parity_ppv_convention_audit() -> dict[str, Any]:
    rows = convention_audit_rows()
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    source_declared = [
        row["label"]
        for row in rows
        if row["readiness"]["source_declared_ppv_mapping_ready"]
    ]
    formula_candidates = [
        row["label"]
        for row in rows
        if row["source_declared_mapping"]["formula_candidate_ready"]
    ]

    return {
        "version": "v2.70",
        "basis": [
            "v2.64_gw_parity_ppv_formula_implementation",
            "v2.69_gw_parity_callister_fixed_variable_comparison",
            "Ng_2305.05844_waveform_modification",
            "Jenks_2305.10478_parameterized_parity_violation",
            "Callister_2312.12532_sgwb_birefringence",
            "Callister_public_code_numpyro_likelihoods",
        ],
        "audit_scope": "source_formula_and_helicity_conventions_only",
        "row_count": len(rows),
        "source_declared_ppv_candidate_routes": source_declared,
        "formula_candidate_routes": formula_candidates,
        "ng_beta10_candidate_ready": True,
        "callister_alpha1_beta1_split_candidate_ready": True,
        "callister_energy_code_convention_ready": True,
        "ppv_beta1_projection_ready": False,
        "helicity_harmonization_ready": False,
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "ppv_convention_audit_partial_candidates_projection_blocked",
        "best_next_artifact": (
            "Implement an Ng public posterior parser and a sign-harmonized beta_1_0 "
            "posterior adapter, while keeping Callister alpha/beta and SGWB energy "
            "routes separate."
        ),
        "interpretation": (
            "Ng is source-declared by Jenks as the closest beta_1_0 amplitude "
            "candidate. Callister supplies a source-backed alpha_1/beta_1 split "
            "and a separate public-code SGWB energy-density convention. None of "
            "these rows is an engine-axis quantum-gravity discriminator because "
            "helicity signs, posterior likelihood ownership, and engine projection "
            "remain blocked."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.70/gw_parity_ppv_convention_audit.json",
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_ppv_convention_audit()
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
