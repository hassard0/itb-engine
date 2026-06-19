"""KK radius precision requirements for tower verdicts (v2.30).

v2.29 gave radius-ratio thresholds for fixed uncertainty. This inverse audit
asks how precise a sourced radius ratio must be to create a claimable tower
allowance or exclusion.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import ExplicitTowerModel, _critical_phi, _json_default


DEFAULT_RADIUS_RATIOS = (1.50, 1.70, 1.90, 2.102867546654528, 2.30, 2.60, 3.00)
DEFAULT_CHECK_SIGMAS = (0.03, 0.05, 0.10)
BOUNDARY_TOLERANCE = 1e-12


def _verdict_at_sigma(phi_mean: float, critical_phi: float, sigma: float) -> str:
    lower = phi_mean - 2.0 * sigma
    upper = phi_mean + 2.0 * sigma
    if lower > critical_phi:
        return "tower_exclusion"
    if upper <= critical_phi:
        return "tower_allowance"
    return "overlap"


def _precision_row(
    radius_ratio: float,
    critical_phi: float,
    check_sigmas: list[float],
) -> dict:
    phi_mean = math.log(radius_ratio)
    mass_gap = 1.0 / radius_ratio
    delta = phi_mean - critical_phi
    if delta > BOUNDARY_TOLERANCE:
        side = "exclusion_side"
        max_sigma = 0.5 * delta
        target_verdict = "tower_exclusion"
        inequality = "log_radius_sigma must be strictly below this value"
    elif delta < -BOUNDARY_TOLERANCE:
        side = "allowance_side"
        max_sigma = -0.5 * delta
        target_verdict = "tower_allowance"
        inequality = "log_radius_sigma must be at or below this value"
    else:
        side = "critical_boundary"
        max_sigma = 0.0
        target_verdict = "tower_allowance_only_at_zero_uncertainty"
        inequality = "only zero uncertainty reaches the allowance boundary"

    return {
        "radius_ratio_mean": radius_ratio,
        "phi_tower_mean": phi_mean,
        "tower_mass_gap_mean": mass_gap,
        "side_of_critical_radius": side,
        "target_verdict": target_verdict,
        "max_log_radius_sigma_for_target_verdict": max_sigma,
        "max_one_sigma_radius_factor_for_target_verdict": math.exp(max_sigma),
        "precision_inequality": inequality,
        "verdict_at_check_sigmas": [
            {
                "log_radius_sigma": sigma,
                "verdict": _verdict_at_sigma(phi_mean, critical_phi, sigma),
            }
            for sigma in check_sigmas
        ],
    }


def diagnose_kk_radius_precision_requirements(
    radius_ratios: list[float] | None = None,
    check_sigmas: list[float] | None = None,
) -> dict:
    ratios = radius_ratios if radius_ratios is not None else list(DEFAULT_RADIUS_RATIOS)
    sigmas = check_sigmas if check_sigmas is not None else list(DEFAULT_CHECK_SIGMAS)
    model = ExplicitTowerModel(lambda_eft=0.65)
    critical = _critical_phi(model)
    critical_phi = float(critical["critical_phi"])
    critical_radius_ratio = math.exp(critical_phi)
    rows = [
        _precision_row(ratio, critical_phi, sigmas)
        for ratio in ratios
        if ratio > 0.0
    ]

    return {
        "basis": ["KK_radius", "precision_requirement", "TowerSpectrum"],
        "critical_phi_tower": critical_phi,
        "critical_tower_mass": critical["tower_mass"],
        "critical_radius_ratio": critical_radius_ratio,
        "check_sigmas": sigmas,
        "radius_precision_requirements": rows,
        "claimable_framework_exclusions_now": [],
        "literature_guardrail": {
            "claim": (
                "These are inverse precision requirements for future sourced "
                "KK-radius adapters. They do not assign a radius to any registered "
                "framework and therefore do not create a framework exclusion."
            ),
            "primary_sources": [
                {
                    "title": "Ooguri and Vafa, On the Geometry of the String Landscape and the Swampland",
                    "url": "https://arxiv.org/abs/hep-th/0605264",
                },
                {
                    "title": "Corvilain, Grimm, and Valenzuela, The Swampland Distance Conjecture for Kahler moduli",
                    "url": "https://arxiv.org/abs/1812.07548",
                },
            ],
        },
        "interpretation": (
            "The KK-radius path becomes decisive only when the one-sigma "
            "uncertainty in log(R/R0) is small enough that the two-sigma interval "
            "sits entirely on one side of the critical tower threshold."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.30/kk_radius_precision_requirements.json",
    )
    args = parser.parse_args()

    result = diagnose_kk_radius_precision_requirements()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
