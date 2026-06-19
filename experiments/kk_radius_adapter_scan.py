"""KK radius adapter candidate scan (v2.29).

v2.28 wired SDC distances into `TowerSpectrum`. This audit adds the direct
KK-radius bridge: m_KK/m0 = R0/R, so phi_tower = log(R/R0). The candidates are
synthetic fixtures that exercise the existing tower-verdict path.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.tower_adapter_thresholds import diagnose_tower_adapter_thresholds
from experiments.tower_spectrum_readiness import diagnose_tower_spectrum_readiness
from itb.tower import kk_radius_tower_spectrum


DEFAULT_RADIUS_CANDIDATES = (
    ("kk_allowance_fixture", 1.70, 0.03),
    ("kk_overlap_fixture", 2.10, 0.05),
    ("kk_exclusion_fixture", 2.60, 0.04),
)


def _candidate_row(label: str, radius_ratio: float, log_radius_sigma: float) -> dict:
    spectrum = kk_radius_tower_spectrum(
        tower_family="kk_radius_synthetic_candidate",
        radius_ratio_mean=radius_ratio,
        log_radius_sigma=log_radius_sigma,
        normalization="radius_ratio_R_over_R0_diagnostic",
        source="synthetic v2.29 KK-radius adapter candidate",
        metadata={"candidate_label": label},
    )
    readiness = diagnose_tower_spectrum_readiness(
        spectra={"string_tree_eft": spectrum}
    )
    verdict = readiness["frameworks"]["string_tree_eft"]
    return {
        "label": label,
        "radius_ratio_mean": radius_ratio,
        "log_radius_sigma": log_radius_sigma,
        "tower_spectrum": spectrum.to_dict(),
        "framework_tower_verdict": verdict["framework_tower_verdict"],
        "two_sigma_phi_interval": verdict["two_sigma_phi_interval"],
        "claimable_exclusion_if_sourced": verdict["claimable_exclusion"],
    }


def _radius_threshold_rows() -> list[dict]:
    thresholds = diagnose_tower_adapter_thresholds()
    rows = []
    for threshold in thresholds["frameworks"]["string_tree_eft"]["sigma_thresholds"]:
        rows.append({
            "phi_tower_sigma": threshold["phi_tower_sigma"],
            "claimable_exclusion_requires_radius_ratio_gt": (
                1.0 / threshold["claimable_exclusion_requires_mass_gap_mean_lt"]
            ),
            "claimable_allowance_requires_radius_ratio_lte": (
                1.0 / threshold["claimable_allowance_requires_mass_gap_mean_gte"]
                if threshold["claimable_allowance_requires_mass_gap_mean_gte"] is not None
                else None
            ),
        })
    return rows


def diagnose_kk_radius_adapter_scan(
    candidates: list[tuple[str, float, float]] | None = None,
) -> dict:
    candidate_values = candidates if candidates is not None else list(DEFAULT_RADIUS_CANDIDATES)
    rows = [
        _candidate_row(label, radius_ratio, log_radius_sigma)
        for label, radius_ratio, log_radius_sigma in candidate_values
    ]
    return {
        "basis": ["KK_radius", "TowerSpectrum", "radius_ratio", "framework_verdict"],
        "radius_thresholds": _radius_threshold_rows(),
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
                "These are synthetic KK-radius adapter candidates. A sourced "
                "radius ratio can drive the tower-verdict path, but these fixture "
                "rows are not framework predictions."
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
                {
                    "title": "Etheredge, Heidenreich, Kaya, Qiu, and Reece, Sharpening the Distance Conjecture in diverse dimensions",
                    "url": "https://arxiv.org/abs/2206.04063",
                },
            ],
        },
        "interpretation": (
            "A KK-radius measurement or compactification calculation can now be "
            "converted to the tower gate through phi_tower=log(R/R0). The current "
            "rows are fixtures, so the audit demonstrates readiness and threshold "
            "values rather than claiming a registered framework exclusion."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/results/v2.29/kk_radius_adapter_scan.json")
    args = parser.parse_args()

    result = diagnose_kk_radius_adapter_scan()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
