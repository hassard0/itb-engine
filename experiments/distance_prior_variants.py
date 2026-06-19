"""Distance-prior variant diagnostics for the v2.13/v2.14 parity lobes.

v2.14 showed that the four straight-line parity lobes are split by the hard
nonzero-threshold encoding of `swampland_distance_conjecture`. This experiment
asks whether the split survives two controls:

1. remove the distance prior entirely;
2. replace it with a parity-optional prior that excludes symmetry-protected
   parity coefficients from the aspect-ratio denominator.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, ".")
from experiments.phases import KEYS
from experiments.stack import build_stack
from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.engine import check
from itb.theory import Theory


PARITY_KEYS = {"g_R2_parity", "g_R3_parity"}


class ParityOptionalDistancePrior(Constraint):
    """Aspect-ratio prior that treats exact parity absence as symmetry-protected.

    This is not asserted as the right Distance Conjecture. It is a diagnostic
    control for whether the parity-lobe topology depends on counting tiny parity
    coefficients in the hierarchy denominator.
    """

    name = "parity_optional_distance_prior"
    citation = "v2.15 diagnostic variant of the distance hierarchy prior"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, R_max: float = 20.0, min_threshold: float = 1e-6):
        self.R_max = float(R_max)
        self.min_threshold = float(min_threshold)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        nonzero_abs = [
            abs(v)
            for k, v in theory.coefficients.items()
            if k not in PARITY_KEYS and abs(v) > self.min_threshold
        ]
        if len(nonzero_abs) <= 1:
            margin = self.R_max
            details = {"trivially_satisfied": "<=1 non-parity coefficient"}
        else:
            ratio = max(nonzero_abs) / min(nonzero_abs)
            margin = self.R_max - ratio
            details = {
                "bound": f"non-parity max/min <= {self.R_max}",
                "ratio": ratio,
                "margin": margin,
            }
        return ConstraintResult(
            self.name,
            margin >= 0.0,
            margin,
            margin,
            details,
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        return {k: 0.0 for k in theory.coefficients}


def _json_default(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    raise TypeError(f"cannot serialize {type(value).__name__}")


def _stack_variant(name: str) -> list[Constraint]:
    stack = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    if name == "default":
        return stack
    without_distance = [c for c in stack if c.name != "swampland_distance_conjecture"]
    if name == "no_distance_prior":
        return without_distance
    if name == "parity_optional_distance_prior":
        return without_distance + [ParityOptionalDistancePrior()]
    raise ValueError(f"unknown variant: {name}")


def _theory(x: np.ndarray) -> Theory:
    return Theory(coefficients={k: float(v) for k, v in zip(KEYS, x)})


def _segment_scan(a: np.ndarray, b: np.ndarray, constraints: list[Constraint], samples: int) -> dict:
    first_failure = None
    worst = {"t": 0.0, "constraint": None, "margin": float("inf")}
    for t in np.linspace(0.0, 1.0, samples):
        x = a + float(t) * (b - a)
        report = check(_theory(x), constraints)
        row = min(report.results, key=lambda r: r.margin)
        if row.margin < worst["margin"]:
            worst = {
                "t": float(t),
                "constraint": row.constraint_name,
                "margin": float(row.margin),
            }
        if first_failure is None and not report.feasible:
            first_failure = {
                "t": float(t),
                "constraint": row.constraint_name,
                "margin": float(row.margin),
            }
    return {
        "feasible": first_failure is None,
        "first_failure": first_failure,
        "worst": worst,
    }


def _centroids(phases_doc: dict) -> list[np.ndarray]:
    return [
        np.array([phase["centroid"][k] for k in KEYS], dtype=float)
        for phase in phases_doc["phases"]
    ]


def _parity_zero(x: np.ndarray) -> np.ndarray:
    z = x.copy()
    z[KEYS.index("g_R2_parity")] = 0.0
    z[KEYS.index("g_R3_parity")] = 0.0
    return z


def diagnose_variants(phases_path: str | Path, samples: int = 101) -> dict:
    phases_doc = json.loads(Path(phases_path).read_text(encoding="utf-8"))
    centroids = _centroids(phases_doc)
    zero_points = [_parity_zero(x) for x in centroids]
    variants = {}

    for variant_name in (
        "default",
        "no_distance_prior",
        "parity_optional_distance_prior",
    ):
        constraints = _stack_variant(variant_name)
        lobe_to_zero = [
            _segment_scan(x, z, constraints, samples=samples)
            for x, z in zip(centroids, zero_points)
        ]
        zero_pair_scans = []
        direct_pair_scans = []
        for i in range(len(centroids)):
            for j in range(i + 1, len(centroids)):
                zero_pair_scans.append({
                    "pair": [i, j],
                    **_segment_scan(zero_points[i], zero_points[j], constraints, samples=samples),
                })
                direct_pair_scans.append({
                    "pair": [i, j],
                    **_segment_scan(centroids[i], centroids[j], constraints, samples=samples),
                })
        lobe_blockers: dict[str, int] = {}
        for scan in lobe_to_zero:
            first = scan["first_failure"]
            if first:
                lobe_blockers[first["constraint"]] = lobe_blockers.get(first["constraint"], 0) + 1

        variants[variant_name] = {
            "all_lobes_reach_parity_zero": all(scan["feasible"] for scan in lobe_to_zero),
            "parity_zero_plane_connected": all(scan["feasible"] for scan in zero_pair_scans),
            "all_connected_by_parity_zero_detour": (
                all(scan["feasible"] for scan in lobe_to_zero)
                and all(scan["feasible"] for scan in zero_pair_scans)
            ),
            "lobe_to_zero_first_failure_blockers": lobe_blockers,
            "direct_pair_failures": [
                {
                    "pair": scan["pair"],
                    "first_failure": scan["first_failure"],
                }
                for scan in direct_pair_scans
                if not scan["feasible"]
            ],
        }

    return {
        "input": str(phases_path),
        "basis": KEYS,
        "samples_per_segment": samples,
        "variants": variants,
        "interpretation": (
            "If the default stack splits the lobes but no-distance and parity-optional "
            "variants connect them through the parity-zero plane, then the four-lobe "
            "topology is controlled by the distance-prior encoding rather than by a "
            "robust physical phase boundary."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="experiments/results/v2.13/phases_8d_1200.json")
    parser.add_argument("--out", default="experiments/results/v2.15/distance_prior_variants.json")
    parser.add_argument("--samples", type=int, default=101)
    args = parser.parse_args()

    result = diagnose_variants(args.input, samples=args.samples)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
