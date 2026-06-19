"""SDC distance requirements for a future tower adapter (v2.27).

v2.26 found qualitative SDC literature seeds but no actionable framework
adapter. This audit converts the exponential SDC relation

    m_tower / m0 = exp(-lambda_sdc * Delta)

into the moduli-distance ranges that would clear the v2.25 two-sigma tower
adapter thresholds.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.tower_adapter_thresholds import DEFAULT_SIGMA_VALUES, diagnose_tower_adapter_thresholds


DEFAULT_DIMENSIONS = (4, 5, 6, 10)
DEFAULT_SLOPES = (0.50, 0.75, 1.00, 1.25)


def _sharpened_lambda(dimension: int) -> float | None:
    if dimension <= 2:
        return None
    return 1.0 / math.sqrt(dimension - 2.0)


def _distance_row(
    label: str,
    lambda_sdc: float,
    sigma_thresholds: list[dict],
) -> dict:
    rows = []
    for threshold in sigma_thresholds:
        exclusion_phi = threshold["claimable_exclusion_requires_phi_mean_gt"]
        allowance_phi = threshold["claimable_allowance_requires_phi_mean_lte"]
        rows.append({
            "phi_tower_sigma": threshold["phi_tower_sigma"],
            "claimable_exclusion_requires_distance_gt": (
                exclusion_phi / lambda_sdc if lambda_sdc > 0.0 else None
            ),
            "claimable_allowance_requires_distance_lte": (
                allowance_phi / lambda_sdc
                if lambda_sdc > 0.0 and allowance_phi is not None
                else None
            ),
            "claimable_exclusion_requires_mass_gap_lt": (
                threshold["claimable_exclusion_requires_mass_gap_mean_lt"]
            ),
            "claimable_allowance_requires_mass_gap_gte": (
                threshold["claimable_allowance_requires_mass_gap_mean_gte"]
            ),
        })
    return {
        "label": label,
        "lambda_sdc": lambda_sdc,
        "distance_thresholds": rows,
    }


def diagnose_sdc_distance_requirements(
    dimensions: list[int] | None = None,
    slopes: list[float] | None = None,
    sigma_values: list[float] | None = None,
) -> dict:
    dims = dimensions if dimensions is not None else list(DEFAULT_DIMENSIONS)
    slope_values = slopes if slopes is not None else list(DEFAULT_SLOPES)
    thresholds = diagnose_tower_adapter_thresholds(
        sigma_values=sigma_values if sigma_values is not None else list(DEFAULT_SIGMA_VALUES)
    )
    reference = thresholds["frameworks"]["string_tree_eft"]["sigma_thresholds"]

    dimension_rows = []
    for dimension in dims:
        lam = _sharpened_lambda(dimension)
        if lam is None:
            continue
        dimension_rows.append(
            {
                "dimension": dimension,
                **_distance_row(f"sharpened_d_{dimension}", lam, reference),
            }
        )

    slope_rows = [
        _distance_row(f"lambda_{slope:g}", slope, reference)
        for slope in slope_values
        if slope > 0.0
    ]

    return {
        "basis": ["SDC", "TowerSpectrum", "Delta_moduli", "phi_tower"],
        "critical_phi_tower": thresholds["critical_phi_tower"],
        "critical_tower_mass": thresholds["critical_tower_mass"],
        "sigma_values": thresholds["sigma_values"],
        "dimension_requirements": dimension_rows,
        "slope_requirements": slope_rows,
        "claimable_framework_exclusions_now": [],
        "literature_guardrail": {
            "claim": (
                "These are SDC distance requirements for a future adapter, not "
                "framework predictions. They assume an exponential tower relation "
                "and still require a framework-specific Delta_moduli and "
                "normalization before any tower verdict is claimable."
            ),
            "primary_sources": [
                {
                    "title": "Ooguri and Vafa, On the Geometry of the String Landscape and the Swampland",
                    "url": "https://arxiv.org/abs/hep-th/0605264",
                },
                {
                    "title": "Etheredge, Heidenreich, Kaya, Qiu, and Reece, Sharpening the Distance Conjecture in diverse dimensions",
                    "url": "https://arxiv.org/abs/2206.04063",
                },
            ],
        },
        "interpretation": (
            "The SDC seed becomes operational only after a compactification or "
            "framework adapter supplies Delta_moduli. For d=4 and sigma=0.05, "
            "a sharpened lambda=1/sqrt(2) requires Delta above the listed "
            "threshold to claim tower exclusion."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/results/v2.27/sdc_distance_requirements.json")
    args = parser.parse_args()

    result = diagnose_sdc_distance_requirements()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
