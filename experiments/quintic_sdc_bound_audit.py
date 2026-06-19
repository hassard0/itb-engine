"""Quintic tower slope versus SDC bound contexts (v2.35).

v2.34 produced a non-synthetic quintic KK tower evidence candidate. This audit
checks which SDC slope comparisons are legitimate for that candidate and which
would be scope errors.
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
from experiments.quintic_tower_evidence_candidate import (
    diagnose_quintic_tower_evidence_candidate,
)


ASHMORE_RUEHLE = {
    "title": (
        "Ashmore and Ruehle, Moduli-dependent KK towers and the swampland "
        "distance conjecture on the quintic Calabi-Yau manifold"
    ),
    "url": "https://arxiv.org/abs/2103.07472",
}

ETHEREDGE_ET_AL = {
    "title": "Etheredge et al., Sharpening the Distance Conjecture in Diverse Dimensions",
    "url": "https://arxiv.org/abs/2206.04063",
}


def _candidate_slope() -> dict[str, float]:
    candidate = diagnose_quintic_tower_evidence_candidate()["candidates"][0]
    spectrum = candidate["evidence"]["spectrum"]
    mean = float(spectrum["phi_tower_mean"])
    sigma = float(spectrum["phi_tower_sigma"])
    ci95 = 1.96 * sigma
    return {
        "mean": mean,
        "one_sigma": sigma,
        "ci95_half_width": ci95,
        "ci95_lower": mean - ci95,
        "ci95_upper": mean + ci95,
    }


def _bound_rows(slope: dict[str, float]) -> list[dict[str, Any]]:
    sqrt6 = 1.0 / math.sqrt(6.0)
    d4_sharpened = 1.0 / math.sqrt(2.0)
    d10_sharpened = 1.0 / math.sqrt(8.0)
    return [
        {
            "label": "ashmore_ruehle_finite_range_sqrt6_reference",
            "bound_value": sqrt6,
            "source": ASHMORE_RUEHLE,
            "comparison_status": (
                "candidate_95ci_above_bound"
                if slope["ci95_lower"] > sqrt6
                else "candidate_95ci_overlaps_or_below_bound"
            ),
            "adjudication": "legitimate_finite_range_context",
            "scope_note": (
                "The source itself compares the fitted finite-range mass exponent "
                "to an alpha=1/sqrt(6) reference."
            ),
        },
        {
            "label": "etheredge_d4_asymptotic_lightest_tower_bound",
            "bound_value": d4_sharpened,
            "source": ETHEREDGE_ET_AL,
            "comparison_status": (
                "candidate_95ci_below_bound"
                if slope["ci95_upper"] < d4_sharpened
                else "candidate_95ci_overlaps_or_above_bound"
            ),
            "adjudication": "not_adjudicable_scope_mismatch",
            "scope_note": (
                "The bound is an asymptotic lightest-tower claim in d dimensions; "
                "the candidate is a finite-range scalar Laplacian subtower on one "
                "quintic compactification."
            ),
        },
        {
            "label": "etheredge_d10_asymptotic_reference",
            "bound_value": d10_sharpened,
            "source": ETHEREDGE_ET_AL,
            "comparison_status": (
                "candidate_95ci_above_bound"
                if slope["ci95_lower"] > d10_sharpened
                else "candidate_95ci_overlaps_or_below_bound"
            ),
            "adjudication": "context_only_not_framework_test",
            "scope_note": (
                "The d=10 value is useful as a dimension check, not as the "
                "four-dimensional tower discriminator used by the engine."
            ),
        },
    ]


def diagnose_quintic_sdc_bound_audit() -> dict[str, Any]:
    slope = _candidate_slope()
    bounds = _bound_rows(slope)
    return {
        "basis": ["quintic_kk_slope", "sdc_bound_context", "scope_gate"],
        "candidate": {
            "label": "ashmore_ruehle_quintic_kk",
            "framework": "string_tree_eft",
            "mass_exponent_alpha": slope,
        },
        "bounds": bounds,
        "bound_status_counts": {
            status: sum(1 for row in bounds if row["adjudication"] == status)
            for status in sorted({row["adjudication"] for row in bounds})
        },
        "decisive_sdc_tests_now": [],
        "claimable_framework_exclusions_now": [],
        "literature_guardrail": {
            "claim": (
                "The quintic source gives a real finite-range slope, but it is "
                "not an adjudication of asymptotic SDC bounds or a framework "
                "exclusion."
            ),
            "primary_sources": [ASHMORE_RUEHLE, ETHEREDGE_ET_AL],
        },
        "interpretation": (
            "The sourced quintic slope is above the 1/sqrt(6) reference used in "
            "the source, below the d=4 sharpened asymptotic bound, and not a "
            "valid test of that d=4 bound because the scopes differ."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.35/quintic_sdc_bound_audit.json",
    )
    args = parser.parse_args()

    result = diagnose_quintic_sdc_bound_audit()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
