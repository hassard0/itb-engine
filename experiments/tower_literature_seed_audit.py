"""Literature seed audit for framework tower adapters (v2.26).

v2.25 gave the numerical thresholds a future `TowerSpectrum` must clear. This
audit records whether primary-source literature seeds already provide enough
information to instantiate such an adapter for a registered framework.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.tower_adapter_thresholds import diagnose_tower_adapter_thresholds
from experiments.tower_spectrum_readiness import REQUIRED_ACTIONABLE_FIELDS
from itb.predict import FRAMEWORKS


DEFAULT_LITERATURE_SEEDS: dict[str, list[dict[str, Any]]] = {
    "string_tree_eft": [
        {
            "seed_id": "ooguri_vafa_distance_conjecture",
            "tower_family": "sdc_exponential_tower",
            "source": "Ooguri and Vafa, On the Geometry of the String Landscape and the Swampland",
            "url": "https://arxiv.org/abs/hep-th/0605264",
            "source_type": "primary_conjecture",
            "qualitative_relation": "infinite-distance limits are accompanied by an infinite tower of light states",
            "adapter_status": "qualitative_tower_relation_only",
        },
        {
            "seed_id": "species_scale_distance_bound",
            "tower_family": "species_scale_tower_bound",
            "source": "van de Heisteeg, Vafa, and Wiesner, Bounds on Species Scale and the Distance Conjecture",
            "url": "https://arxiv.org/abs/2303.13580",
            "source_type": "primary_bound",
            "qualitative_relation": "tower masses cannot go to zero faster than exponentially in field distance",
            "adapter_status": "slope_bound_without_framework_coordinate",
        },
    ]
}


def _provided_fields(seed: dict[str, Any]) -> list[str]:
    return [
        field for field in REQUIRED_ACTIONABLE_FIELDS
        if seed.get(field) not in (None, "")
    ]


def _seed_row(framework: str, seed: dict[str, Any], threshold: dict) -> dict:
    provided = _provided_fields(seed)
    missing = [
        field for field in REQUIRED_ACTIONABLE_FIELDS
        if field not in provided
    ]
    return {
        "framework": framework,
        **seed,
        "provided_actionable_fields": provided,
        "missing_actionable_fields": missing,
        "actionable_as_tower_spectrum": len(missing) == 0,
        "threshold_context_sigma_0.05": {
            "claimable_exclusion_requires_phi_mean_gt": (
                threshold["claimable_exclusion_requires_phi_mean_gt"]
            ),
            "claimable_allowance_requires_phi_mean_lte": (
                threshold["claimable_allowance_requires_phi_mean_lte"]
            ),
        },
    }


def diagnose_tower_literature_seed_audit(
    seeds: dict[str, list[dict[str, Any]]] | None = None,
) -> dict:
    seed_map = seeds if seeds is not None else DEFAULT_LITERATURE_SEEDS
    thresholds = diagnose_tower_adapter_thresholds(sigma_values=[0.05])
    sigma_threshold = (
        thresholds["frameworks"]["string_tree_eft"]["sigma_thresholds"][0]
    )
    rows = []
    for framework, framework_seeds in seed_map.items():
        for seed in framework_seeds:
            rows.append(_seed_row(framework, seed, sigma_threshold))

    actionable = [row for row in rows if row["actionable_as_tower_spectrum"]]
    seeded_frameworks = sorted({row["framework"] for row in rows})
    registered_frameworks_without_seed = sorted(set(FRAMEWORKS) - set(seeded_frameworks))

    return {
        "basis": ["literature_seed", "TowerSpectrum", "phi_tower"],
        "required_actionable_fields": list(REQUIRED_ACTIONABLE_FIELDS),
        "seeded_frameworks": seeded_frameworks,
        "registered_frameworks_without_literature_seed": registered_frameworks_without_seed,
        "candidate_seed_count": len(rows),
        "actionable_seed_count": len(actionable),
        "actionable_seeds": actionable,
        "claimable_framework_exclusions_now": [],
        "seeds": rows,
        "literature_guardrail": {
            "claim": (
                "Primary sources can seed a tower-adapter search, but a qualitative "
                "tower relation is not an actionable TowerSpectrum. The adapter "
                "still needs phi_tower_mean, phi_tower_sigma, normalization, and "
                "source fields in the v2.24 contract."
            ),
            "primary_sources": [
                {
                    "title": "Ooguri and Vafa, On the Geometry of the String Landscape and the Swampland",
                    "url": "https://arxiv.org/abs/hep-th/0605264",
                },
                {
                    "title": "van de Heisteeg, Vafa, and Wiesner, Bounds on Species Scale and the Distance Conjecture",
                    "url": "https://arxiv.org/abs/2303.13580",
                },
            ],
        },
        "interpretation": (
            "The strongest current literature seed for a registered framework is "
            "string/SDC-like, but it does not assign the current string_tree_eft "
            "encoder a normalized phi_tower value or uncertainty. It therefore "
            "cannot clear the v2.25 thresholds."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/results/v2.26/tower_literature_seed_audit.json")
    args = parser.parse_args()

    result = diagnose_tower_literature_seed_audit()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
