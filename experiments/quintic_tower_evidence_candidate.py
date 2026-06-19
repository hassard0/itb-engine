"""Quintic KK tower evidence candidate for string-tree EFT (v2.34).

v2.33 showed that no current framework encoder can supply a sourced
TowerEvidence row. This audit adds one non-synthetic candidate from primary
literature without promoting it to a framework-level claim.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.tower_spectrum_readiness import diagnose_tower_spectrum_readiness
from itb.tower import TowerEvidence, TowerSpectrum, validate_tower_evidence


SOURCE = {
    "title": (
        "Ashmore and Ruehle, Moduli-dependent KK towers and the swampland "
        "distance conjecture on the quintic Calabi-Yau manifold"
    ),
    "authors": ["Anthony Ashmore", "Fabian Ruehle"],
    "url": "https://arxiv.org/abs/2103.07472",
    "arxiv": "2103.07472",
    "equation": "Eq. (28)",
}

LAPLACIAN_FIT_EXPONENT = 0.906
LAPLACIAN_FIT_95CI_HALF_WIDTH = 0.034
CONFIDENCE_TO_ONE_SIGMA = 1.96


def _mass_exponent_summary() -> dict[str, float | str]:
    """Convert the source's Laplacian eigenvalue fit into a mass exponent.

    The source fits a Laplacian eigenvalue as lambda ~ exp(-0.906 d). The
    four-dimensional mass scales as m_KK ~ sqrt(lambda), so the mass exponent is
    half the eigenvalue exponent.
    """
    mass_exponent = 0.5 * LAPLACIAN_FIT_EXPONENT
    mass_95ci_half_width = 0.5 * LAPLACIAN_FIT_95CI_HALF_WIDTH
    mass_one_sigma = mass_95ci_half_width / CONFIDENCE_TO_ONE_SIGMA
    return {
        "laplacian_fit_exponent": LAPLACIAN_FIT_EXPONENT,
        "laplacian_fit_95ci_half_width": LAPLACIAN_FIT_95CI_HALF_WIDTH,
        "mass_exponent_mean": mass_exponent,
        "mass_exponent_95ci_half_width": mass_95ci_half_width,
        "mass_exponent_one_sigma": mass_one_sigma,
        "conversion": "m_KK is proportional to sqrt(laplacian_eigenvalue)",
    }


def _quintic_spectrum(delta_moduli: float = 1.0) -> TowerSpectrum:
    exponent = _mass_exponent_summary()
    phi_mean = float(exponent["mass_exponent_mean"]) * delta_moduli
    phi_sigma = float(exponent["mass_exponent_one_sigma"]) * delta_moduli
    return TowerSpectrum(
        tower_family="quintic_scalar_laplacian_kk_lambda3",
        phi_tower_mean=phi_mean,
        phi_tower_sigma=phi_sigma,
        tower_mass_gap=math.exp(-phi_mean),
        normalization=(
            "phi_tower = alpha_mass * Delta for one Planck-unit geodesic "
            "distance from psi=2 in the source convention"
        ),
        source=f"{SOURCE['title']}, {SOURCE['equation']}",
        metadata={
            "source": SOURCE,
            "delta_moduli_mean": delta_moduli,
            "fit_range": "2 <= psi <= 1000",
            "compactification": "one-parameter quintic Calabi-Yau manifold",
            "mode": "third scalar Laplacian eigenvalue; a KK subtower proxy",
            "source_fit": "lambda_3 ~= 56.4 * exp(-(0.906 +/- 0.034) d(2,rho))",
            "uncertainty_note": (
                "Source quotes a 95% confidence interval for the Laplacian "
                "exponent; this audit converts half-width/2/1.96 into an "
                "approximate one-sigma mass-exponent uncertainty."
            ),
            "mass_exponent": exponent,
        },
    )


def _candidate_evidence(spectrum: TowerSpectrum) -> TowerEvidence:
    return TowerEvidence(
        framework="string_tree_eft",
        spectrum=spectrum,
        adapter_kind="sdc_mass_exponent",
        source_url=SOURCE["url"],
        source_type="primary_literature",
        derivation_kind="direct_numeric_quintic_laplacian_fit",
        uncertainty_kind="published_95ci_converted_to_mass_one_sigma",
        normalization_reference=(
            "m_KK(Delta)/m_KK(0) = exp(-alpha_mass * Delta), "
            "with Delta fixed to one Planck-unit geodesic distance"
        ),
        metadata={
            "candidate_label": "ashmore_ruehle_quintic_kk",
            "framework_scope": "single_compactification_candidate",
            "source": SOURCE,
        },
    )


def _candidate_row() -> dict[str, Any]:
    spectrum = _quintic_spectrum()
    evidence = _candidate_evidence(spectrum)
    readiness = diagnose_tower_spectrum_readiness(spectra={"string_tree_eft": spectrum})
    framework_row = readiness["frameworks"]["string_tree_eft"]
    validation = validate_tower_evidence(evidence)
    scope_blockers = [
        "single_compactification_not_full_string_tree_eft_catalogue",
        "single_scalar_laplacian_subtower_not_complete_compactification_spectrum",
        "finite_range_fit_not_asymptotic_large-distance_spectrum",
        "not_exposed_by_string_tree_eft.tower_evidence",
    ]
    return {
        "label": "ashmore_ruehle_quintic_kk",
        "framework": "string_tree_eft",
        "evidence": evidence.to_dict(),
        "evidence_validation": validation,
        "framework_tower_verdict": framework_row["framework_tower_verdict"],
        "tower_claimable_by_math": framework_row["claimable_exclusion"],
        "two_sigma_phi_interval": framework_row["two_sigma_phi_interval"],
        "critical_phi_tower": framework_row["critical_phi_tower"],
        "candidate_scope": {
            "schema_ready": validation["ready_for_framework_claim"],
            "non_synthetic_primary_source": True,
            "framework_claim_ready": False,
            "blockers": scope_blockers,
        },
        "claimable_now": False,
    }


def diagnose_quintic_tower_evidence_candidate() -> dict[str, Any]:
    candidate = _candidate_row()
    return {
        "basis": ["TowerEvidence", "primary_literature", "quintic_kk_spectrum"],
        "candidate_count": 1,
        "schema_ready_candidates": [
            candidate["label"]
        ] if candidate["candidate_scope"]["schema_ready"] else [],
        "framework_claim_ready_candidates": [],
        "claimable_framework_exclusions_now": [],
        "candidates": [candidate],
        "literature_guardrail": {
            "claim": (
                "This is the first non-synthetic sourced tower-evidence "
                "candidate in the loop, but it is not a framework-level "
                "string-tree EFT claim."
            ),
            "primary_sources": [SOURCE],
        },
        "interpretation": (
            "Ashmore and Ruehle provide a numeric quintic KK subtower fit that "
            "can populate the TowerEvidence schema. The candidate is mathematically "
            "tower-allowed in the current diagnostic gate and remains scope-blocked "
            "from any framework-level exclusion."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.34/quintic_tower_evidence_candidate.json",
    )
    args = parser.parse_args()

    result = diagnose_quintic_tower_evidence_candidate()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
