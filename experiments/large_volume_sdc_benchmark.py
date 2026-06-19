"""Large-volume SDC benchmark audit (v2.37).

v2.36 showed that the finite-range quintic tower candidate should not be
promoted into generic string tree EFT. This audit checks a stronger primary
source: the large-volume asymptotic fit in Blumenhagen et al. It is encoded as a
benchmark, not a framework prediction, because the one-Planck displacement is an
audit assumption rather than a native framework assignment.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.tower_spectrum_readiness import diagnose_tower_spectrum_readiness
from itb.tower import TowerEvidence, TowerSpectrum, validate_tower_evidence


SOURCE = {
    "title": (
        "Blumenhagen, Klaewer, Schlechter, and Wolf, The Refined Swampland "
        "Distance Conjecture in Calabi-Yau Moduli Spaces"
    ),
    "url": "https://arxiv.org/abs/1803.04989",
    "table": "Table 3",
    "equations": ["Eq. (4.19)", "Eq. (4.20)", "Eq. (4.21)"],
}

TABLE3_LAMBDA_INVERSE = (
    0.9605,
    0.9865,
    0.9780,
    0.9567,
    0.9611,
    0.9275,
    0.9253,
    0.8969,
    0.8845,
    0.8657,
)


def _lambda_summary() -> dict[str, Any]:
    lambdas = [1.0 / value for value in TABLE3_LAMBDA_INVERSE]
    mean = statistics.fmean(lambdas)
    angular_sigma = statistics.pstdev(lambdas)
    return {
        "lambda_inverse_values": list(TABLE3_LAMBDA_INVERSE),
        "lambda_sdc_values": lambdas,
        "lambda_sdc_min": min(lambdas),
        "lambda_sdc_max": max(lambdas),
        "lambda_sdc_mean": mean,
        "lambda_sdc_angular_sigma": angular_sigma,
        "angular_variation_note": (
            "This is variation across geodesic angles in the source table, not "
            "a statistical measurement uncertainty."
        ),
        "conservative_interpretation": (
            "Use the source fit lambda as the SDC mass exponent. Do not use the "
            "additional rough factor of two from M_KK ~ exp(-2 lambda Theta)."
        ),
    }


def _benchmark_spectrum(delta_moduli: float = 1.0) -> TowerSpectrum:
    summary = _lambda_summary()
    phi_mean = float(summary["lambda_sdc_mean"]) * delta_moduli
    phi_sigma = float(summary["lambda_sdc_angular_sigma"]) * delta_moduli
    return TowerSpectrum(
        tower_family="large_volume_calabi_yau_sdc_lambda_table3",
        phi_tower_mean=phi_mean,
        phi_tower_sigma=phi_sigma,
        tower_mass_gap=math.exp(-phi_mean),
        normalization=(
            "phi_tower = lambda_sdc * Delta_moduli with Delta_moduli fixed "
            "to a one-Planck-unit benchmark"
        ),
        source=f"{SOURCE['title']}, {SOURCE['table']}",
        metadata={
            "source": SOURCE,
            "delta_moduli_mean": delta_moduli,
            "lambda_summary": summary,
            "benchmark_kind": "one_planck_large_volume_displacement",
            "scope_note": (
                "The source supplies an asymptotic large-volume slope. This "
                "audit supplies Delta_moduli=1 as a benchmark; the source does "
                "not claim that generic string_tree_eft must occupy this point."
            ),
        },
    )


def _benchmark_evidence(spectrum: TowerSpectrum) -> TowerEvidence:
    return TowerEvidence(
        framework="string_tree_eft",
        spectrum=spectrum,
        adapter_kind="sdc_large_volume_lambda_benchmark",
        source_url=SOURCE["url"],
        source_type="primary_literature",
        derivation_kind="asymptotic_large_volume_table_fit",
        uncertainty_kind="geodesic_angle_variation_not_statistical_uncertainty",
        normalization_reference=(
            "Theta(t) ~= lambda^-1 log(t) + alpha0 + alpha1/t^3; "
            "benchmark sets Delta_moduli=1 in Planck units"
        ),
        metadata={
            "candidate_label": "blumenhagen_large_volume_delta1_benchmark",
            "source": SOURCE,
        },
    )


def diagnose_large_volume_sdc_benchmark() -> dict[str, Any]:
    spectrum = _benchmark_spectrum()
    evidence = _benchmark_evidence(spectrum)
    readiness = diagnose_tower_spectrum_readiness(spectra={"string_tree_eft": spectrum})
    framework_row = readiness["frameworks"]["string_tree_eft"]
    validation = validate_tower_evidence(evidence)
    lambda_summary = spectrum.metadata["lambda_summary"]
    critical = float(framework_row["critical_phi_tower"])
    lambda_mean = float(lambda_summary["lambda_sdc_mean"])
    lambda_sigma = float(lambda_summary["lambda_sdc_angular_sigma"])
    conservative_delta_for_exclusion = critical / (lambda_mean - 2.0 * lambda_sigma)
    return {
        "basis": ["primary_literature", "large_volume_sdc", "benchmark_gate"],
        "candidate": {
            "label": "blumenhagen_large_volume_delta1_benchmark",
            "framework": "string_tree_eft",
            "evidence": evidence.to_dict(),
            "evidence_validation": validation,
            "framework_tower_verdict": framework_row["framework_tower_verdict"],
            "tower_claimable_by_math": framework_row["claimable_exclusion"],
            "two_sigma_phi_interval": framework_row["two_sigma_phi_interval"],
            "critical_phi_tower": critical,
            "conservative_delta_moduli_required_for_exclusion": (
                conservative_delta_for_exclusion
            ),
            "claimable_now": False,
            "scope_blockers": [
                "delta_moduli_equals_one_is_benchmark_not_framework_prediction",
                "geodesic_angle_variation_is_not_statistical_uncertainty",
                "not_native_string_tree_eft_tower_evidence",
                "generic_string_tree_eft_does_not_select_large_volume_endpoint",
            ],
        },
        "benchmark_status": {
            "schema_ready": validation["ready_for_framework_claim"],
            "math_excluding_if_delta1_assumed": framework_row["claimable_exclusion"],
            "framework_claim_ready": False,
        },
        "claimable_framework_exclusions_now": [],
        "literature_guardrail": {
            "claim": (
                "The large-volume source gives an asymptotic numeric SDC slope. "
                "The one-Planck displacement is this audit's benchmark, so the "
                "math exclusion is not yet a framework-level exclusion."
            ),
            "primary_sources": [SOURCE],
        },
        "interpretation": (
            "The blocker has moved: sourceability is no longer the limiting issue "
            "for this benchmark. The missing ingredient is framework ownership of "
            "Delta_moduli, uncertainty semantics, and endpoint selection."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.37/large_volume_sdc_benchmark.json",
    )
    args = parser.parse_args()

    result = diagnose_large_volume_sdc_benchmark()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
