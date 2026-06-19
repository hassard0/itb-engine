"""SDC adapter candidate scan (v2.28).

v2.27 computed distance requirements. This audit exercises the reusable
`sdc_tower_spectrum` adapter on synthetic distance candidates so future
frameworks can wire sourced compactification distances through the same path.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.tower_spectrum_readiness import diagnose_tower_spectrum_readiness
from itb.tower import sdc_tower_spectrum


DEFAULT_DISTANCE_CANDIDATES = (
    ("d4_allowance_fixture", 0.80, 0.05),
    ("d4_overlap_fixture", 1.05, 0.05),
    ("d4_exclusion_fixture", 1.25, 0.05),
)


def _sharpened_lambda(dimension: int) -> float:
    return 1.0 / math.sqrt(dimension - 2.0)


def _candidate_row(
    label: str,
    delta_mean: float,
    delta_sigma: float,
    dimension: int,
) -> dict:
    lambda_sdc = _sharpened_lambda(dimension)
    spectrum = sdc_tower_spectrum(
        tower_family="sdc_synthetic_candidate",
        delta_moduli_mean=delta_mean,
        delta_moduli_sigma=delta_sigma,
        lambda_sdc=lambda_sdc,
        normalization=f"sharpened_sdc_d_{dimension}_diagnostic",
        source="synthetic v2.28 adapter candidate",
        metadata={"candidate_label": label, "dimension": dimension},
    )
    readiness = diagnose_tower_spectrum_readiness(
        spectra={"string_tree_eft": spectrum}
    )
    verdict = readiness["frameworks"]["string_tree_eft"]
    return {
        "label": label,
        "dimension": dimension,
        "lambda_sdc": lambda_sdc,
        "delta_moduli_mean": delta_mean,
        "delta_moduli_sigma": delta_sigma,
        "tower_spectrum": spectrum.to_dict(),
        "framework_tower_verdict": verdict["framework_tower_verdict"],
        "two_sigma_phi_interval": verdict["two_sigma_phi_interval"],
        "claimable_exclusion_if_sourced": verdict["claimable_exclusion"],
    }


def diagnose_sdc_adapter_candidate_scan(
    candidates: list[tuple[str, float, float]] | None = None,
    dimension: int = 4,
) -> dict:
    candidate_values = candidates if candidates is not None else list(DEFAULT_DISTANCE_CANDIDATES)
    rows = [
        _candidate_row(label, delta_mean, delta_sigma, dimension)
        for label, delta_mean, delta_sigma in candidate_values
    ]
    return {
        "basis": ["SDC", "TowerSpectrum", "Delta_moduli", "framework_verdict"],
        "dimension": dimension,
        "lambda_sdc": _sharpened_lambda(dimension),
        "candidate_count": len(rows),
        "claimable_if_sourced": [
            row["label"] for row in rows if row["claimable_exclusion_if_sourced"]
        ],
        "verdict_counts": {
            verdict: sum(1 for row in rows if row["framework_tower_verdict"] == verdict)
            for verdict in sorted({row["framework_tower_verdict"] for row in rows})
        },
        "candidates": rows,
        "claimable_framework_exclusions_now": [],
        "literature_guardrail": {
            "claim": (
                "These are synthetic SDC adapter candidates. A row marked "
                "claimable_if_sourced shows the adapter path would support a "
                "verdict only after a real framework source supplies that "
                "Delta_moduli and uncertainty."
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
            "The adapter utility is sufficient to turn a sourced SDC distance "
            "into the existing tower-verdict machinery. The current candidates "
            "are synthetic fixtures, so they demonstrate readiness rather than "
            "claiming a framework exclusion."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/results/v2.28/sdc_adapter_candidate_scan.json")
    args = parser.parse_args()

    result = diagnose_sdc_adapter_candidate_scan()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
