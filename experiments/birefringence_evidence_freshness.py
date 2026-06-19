"""Cosmic-birefringence evidence freshness audit (v2.49).

The non-tower discriminator route is effectively one-observable: the
data-driven EFT lives or dies on isotropic cosmic birefringence. This audit
checks whether the engine's baseline beta=0.34 +/- 0.09 deg assumption is still
directionally supported by newer primary-source analyses.
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
from itb.constraints.cosmic_birefringence import BETA_MEAS_DEG, BETA_SIGMA_DEG


DATASETS = (
    {
        "label": "engine_baseline_wmap_planck",
        "beta_deg": 0.342,
        "sigma_deg": 0.094,
        "systematic_sigma_deg": None,
        "year": 2022,
        "instrument_family": "WMAP+Planck",
        "status": "published_hint",
        "source": {
            "title": (
                "Eskilt and Komatsu, Improved Constraints on Cosmic "
                "Birefringence from the WMAP and Planck CMB Polarization Data"
            ),
            "url": "https://arxiv.org/abs/2205.13962",
        },
    },
    {
        "label": "act_dr6",
        "beta_deg": 0.215,
        "sigma_deg": 0.074,
        "systematic_sigma_deg": None,
        "year": 2026,
        "instrument_family": "ACT",
        "status": "published_hint_systematics_unresolved",
        "source": {
            "title": (
                "Diego-Palazuelos and Komatsu, Cosmic Birefringence from the "
                "Atacama Cosmology Telescope Data Release 6"
            ),
            "url": "https://arxiv.org/abs/2509.13654",
        },
    },
    {
        "label": "planck_pr4_map_space_sevem",
        "beta_deg": 0.46,
        "sigma_deg": 0.04,
        "systematic_sigma_deg": 0.28,
        "year": 2025,
        "instrument_family": "Planck",
        "status": "systematic_dominated_consistent_with_zero",
        "source": {
            "title": "Sullivan et al., Planck PR4 (NPIPE) map-space cosmic birefringence",
            "url": "https://arxiv.org/abs/2502.07654",
        },
    },
    {
        "label": "planck_pr4_map_space_commander",
        "beta_deg": 0.48,
        "sigma_deg": 0.04,
        "systematic_sigma_deg": 0.28,
        "year": 2025,
        "instrument_family": "Planck",
        "status": "systematic_dominated_consistent_with_zero",
        "source": {
            "title": "Sullivan et al., Planck PR4 (NPIPE) map-space cosmic birefringence",
            "url": "https://arxiv.org/abs/2502.07654",
        },
    },
    {
        "label": "hybrid_ilc_planck_pr4",
        "beta_deg": 0.32,
        "sigma_deg": 0.12,
        "systematic_sigma_deg": None,
        "year": 2025,
        "instrument_family": "Planck",
        "status": "methodological_cross_check",
        "source": {
            "title": (
                "Remazeilles, Field-level constraints on cosmic birefringence "
                "from hybrid ILC maps"
            ),
            "url": "https://arxiv.org/abs/2507.22109",
        },
    },
)


def _total_sigma(row: dict[str, Any]) -> float:
    systematic = row["systematic_sigma_deg"]
    if systematic is None:
        return float(row["sigma_deg"])
    return math.hypot(float(row["sigma_deg"]), float(systematic))


def _dataset_row(row: dict[str, Any]) -> dict[str, Any]:
    total_sigma = _total_sigma(row)
    beta = float(row["beta_deg"])
    return {
        **row,
        "total_sigma_deg": total_sigma,
        "sign": "positive" if beta > 0.0 else "negative" if beta < 0.0 else "zero",
        "zero_exclusion_sigma": beta / total_sigma if total_sigma else None,
        "consistent_with_zero_at_2sigma": abs(beta) <= 2.0 * total_sigma,
    }


def _fixed_effect(rows: list[dict[str, Any]]) -> dict[str, Any]:
    weights = [1.0 / (_total_sigma(row) ** 2) for row in rows]
    beta = sum(float(row["beta_deg"]) * weight for row, weight in zip(rows, weights))
    beta /= sum(weights)
    sigma = math.sqrt(1.0 / sum(weights))
    return {
        "labels": [row["label"] for row in rows],
        "beta_deg": beta,
        "sigma_deg": sigma,
        "zero_exclusion_sigma": beta / sigma,
    }


def diagnose_birefringence_evidence_freshness() -> dict[str, Any]:
    rows = [_dataset_row(row) for row in DATASETS]
    positive_rows = [row for row in rows if row["sign"] == "positive"]
    systematic_dominated = [
        row["label"] for row in rows
        if row["systematic_sigma_deg"] is not None
        and row["systematic_sigma_deg"] > row["sigma_deg"]
    ]
    independent_pair = _fixed_effect([
        DATASETS[0],
        DATASETS[1],
    ])
    engine_baseline = {
        "beta_deg": BETA_MEAS_DEG,
        "sigma_deg": BETA_SIGMA_DEG,
        "zero_exclusion_sigma": BETA_MEAS_DEG / BETA_SIGMA_DEG,
    }

    return {
        "basis": [
            "cosmic_birefringence_primary_sources",
            "engine_data_driven_eft_route",
            "systematics_guardrail",
        ],
        "engine_baseline": engine_baseline,
        "dataset_count": len(rows),
        "positive_sign_dataset_count": len(positive_rows),
        "systematic_dominated_datasets": systematic_dominated,
        "datasets": rows,
        "independent_instrument_pair_fixed_effect": independent_pair,
        "claimable_discriminator_now": False,
        "claim_blockers": [
            "no_5sigma_single_dataset_detection",
            "instrument_angle_miscalibration_degeneracy",
            "foreground_systematics_not_closed",
            "data_driven_eft_still_one_observable_dominated",
        ],
        "route_status": (
            "alive_but_not_claimable"
            if len(positive_rows) == len(rows)
            else "sign_inconsistent"
        ),
        "literature_guardrail": {
            "claim": (
                "Newer analyses keep the birefringence sign positive but do not "
                "turn the data-driven EFT into a solved quantum-gravity "
                "discriminator. Systematics and one-observable dependence remain "
                "the controlling blockers."
            ),
            "primary_sources": [row["source"] for row in DATASETS],
        },
        "interpretation": (
            "The non-tower route remains more empirically alive than the current "
            "native tower route: ACT DR6 and Planck cross-checks preserve a "
            "positive beta sign. It is still not a solution claim because no "
            "single dataset has a systematic-safe 5 sigma detection, and the "
            "engine's favored data-driven EFT remains dominated by this "
            "one-observable route."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.49/birefringence_evidence_freshness.json",
    )
    args = parser.parse_args()

    result = diagnose_birefringence_evidence_freshness()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
