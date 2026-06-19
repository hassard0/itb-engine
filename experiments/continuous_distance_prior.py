"""Continuous hierarchy-prior diagnostics for the v2.13 parity lobes.

v2.14/v2.15 showed that the four straight-line parity components are split by
the hard nonzero-threshold encoding of `swampland_distance_conjecture`.

This file does not propose a corrected Swampland Distance Conjecture. It tests
families of coefficient-space hierarchy priors that are continuous, sectorized,
or symmetry-aware enough to diagnose whether the lobe split is robust.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Callable

import numpy as np

sys.path.insert(0, ".")
from experiments.phases import KEYS
from experiments.stack import build_stack
from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.engine import check
from itb.theory import Theory


PARITY_KEYS = {"g_R2_parity", "g_R3_parity"}
DEFAULT_SWEEP_VALUES = (1e-6, 0.005, 0.01, 0.02, 0.025, 0.03, 0.04, 0.05)
SECTORS = {
    "matter": ("g_4", "g_6", "g_8"),
    "curvature": ("g_R2", "g_R3"),
    "central_charge": ("g_C",),
    "parity": ("g_R2_parity", "g_R3_parity"),
}


class HardThresholdDistancePrior(Constraint):
    """Default aspect-ratio prior with a tunable nonzero threshold."""

    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, threshold: float, R_max: float = 20.0):
        self.threshold = float(threshold)
        self.R_max = float(R_max)
        self.name = "hard_threshold_distance_prior"
        self.citation = "v2.16 threshold sweep of the coefficient hierarchy prior"

    def evaluate(self, theory: Theory) -> ConstraintResult:
        values = [
            abs(v)
            for v in theory.coefficients.values()
            if abs(v) > self.threshold
        ]
        if len(values) <= 1:
            return ConstraintResult(
                self.name,
                True,
                self.R_max,
                self.R_max,
                {"trivially_satisfied": "<=1 active coefficient"},
            )
        ratio = max(values) / min(values)
        margin = self.R_max - ratio
        return ConstraintResult(
            self.name,
            margin >= 0.0,
            margin,
            margin,
            {
                "threshold": self.threshold,
                "ratio": ratio,
                "max_coef": max(values),
                "min_coef": min(values),
                "bound": f"active max/min <= {self.R_max}",
            },
        )


class SmoothFloorDistancePrior(Constraint):
    """Continuous max/min proxy using sqrt(g^2 + floor^2) magnitudes."""

    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, floor: float, R_max: float = 20.0):
        self.floor = float(floor)
        self.R_max = float(R_max)
        self.name = "smooth_floor_distance_prior"
        self.citation = "v2.16 smooth-floor coefficient hierarchy diagnostic"

    def evaluate(self, theory: Theory) -> ConstraintResult:
        values = [
            math.sqrt(float(v) * float(v) + self.floor * self.floor)
            for v in theory.coefficients.values()
        ]
        if len(values) <= 1:
            return ConstraintResult(self.name, True, self.R_max, self.R_max, {})
        ratio = max(values) / min(values)
        margin = self.R_max - ratio
        return ConstraintResult(
            self.name,
            margin >= 0.0,
            margin,
            margin,
            {
                "floor": self.floor,
                "ratio": ratio,
                "max_smooth_coef": max(values),
                "min_smooth_coef": min(values),
                "bound": f"smooth max/min <= {self.R_max}",
            },
        )


class SoftActiveLogHierarchyPrior(Constraint):
    """Continuous log-spread proxy with zero coefficients smoothly deactivated.

    The pairwise spread is weighted by sqrt(w_i w_j), where
    w_i = |g_i|^2 / (|g_i|^2 + floor^2). Exact zeros therefore do not become
    denominators, while small active coefficients are penalized continuously.
    """

    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, floor: float, R_max: float = 20.0):
        self.floor = float(floor)
        self.R_max = float(R_max)
        self.name = "soft_active_log_hierarchy_prior"
        self.citation = "v2.16 soft-active log hierarchy diagnostic"

    def evaluate(self, theory: Theory) -> ConstraintResult:
        mags = np.array([abs(float(v)) for v in theory.coefficients.values()], dtype=float)
        weights = (mags * mags) / (mags * mags + self.floor * self.floor)
        if np.count_nonzero(weights > 1e-12) <= 1:
            margin = math.log(self.R_max)
            return ConstraintResult(
                self.name,
                True,
                margin,
                margin,
                {"trivially_satisfied": "<=1 active coefficient"},
            )

        logs = np.log(np.sqrt(mags * mags + self.floor * self.floor))
        spread = 0.0
        for i in range(len(logs)):
            for j in range(i + 1, len(logs)):
                spread = max(
                    spread,
                    float(math.sqrt(weights[i] * weights[j]) * abs(logs[i] - logs[j])),
                )
        margin = math.log(self.R_max) - spread
        return ConstraintResult(
            self.name,
            margin >= 0.0,
            margin,
            margin,
            {
                "floor": self.floor,
                "log_spread": spread,
                "ratio_equivalent": math.exp(spread),
                "bound": f"soft-active log spread <= log({self.R_max})",
            },
        )


class SectorNormDistancePrior(Constraint):
    """Aspect-ratio prior on sector norms rather than individual coefficients."""

    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, threshold: float, R_max: float = 20.0):
        self.threshold = float(threshold)
        self.R_max = float(R_max)
        self.name = "sector_norm_distance_prior"
        self.citation = "v2.16 sector-norm hierarchy diagnostic"

    def evaluate(self, theory: Theory) -> ConstraintResult:
        norms = {}
        for sector, keys in SECTORS.items():
            norm = math.sqrt(
                sum(float(theory.coefficients.get(key, 0.0)) ** 2 for key in keys)
            )
            if norm > self.threshold:
                norms[sector] = norm
        if len(norms) <= 1:
            return ConstraintResult(
                self.name,
                True,
                self.R_max,
                self.R_max,
                {"trivially_satisfied": "<=1 active sector"},
            )
        ratio = max(norms.values()) / min(norms.values())
        margin = self.R_max - ratio
        return ConstraintResult(
            self.name,
            margin >= 0.0,
            margin,
            margin,
            {
                "threshold": self.threshold,
                "ratio": ratio,
                "active_sector_norms": norms,
                "bound": f"active sector max/min <= {self.R_max}",
            },
        )


def _json_default(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    raise TypeError(f"cannot serialize {type(value).__name__}")


def _parse_float_list(raw: str) -> list[float]:
    return [float(part.strip()) for part in raw.split(",") if part.strip()]


def _theory(x: np.ndarray) -> Theory:
    return Theory(coefficients={k: float(v) for k, v in zip(KEYS, x)})


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


def _base_stack() -> list[Constraint]:
    return build_stack(bnossw_mean="geometric", rfc_form="convex_hull")


def _without_distance_prior() -> list[Constraint]:
    return [
        constraint
        for constraint in _base_stack()
        if constraint.name != "swampland_distance_conjecture"
    ]


def _stack_with(distance_prior: Constraint | None) -> list[Constraint]:
    if distance_prior is None:
        return _without_distance_prior()
    return _without_distance_prior() + [distance_prior]


def _segment_scan(
    a: np.ndarray,
    b: np.ndarray,
    constraints: list[Constraint],
    samples: int,
) -> dict:
    first_failure = None
    worst = {"t": 0.0, "constraint": None, "margin": float("inf")}
    for t in np.linspace(0.0, 1.0, samples):
        x = a + float(t) * (b - a)
        report = check(_theory(x), constraints)
        row = min(report.results, key=lambda result: result.margin)
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


def _diagnose_stack(
    centroids: list[np.ndarray],
    zero_points: list[np.ndarray],
    constraints: list[Constraint],
    samples: int,
) -> dict:
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

    blockers: dict[str, int] = {}
    for scan in lobe_to_zero:
        first = scan["first_failure"]
        if first:
            blockers[first["constraint"]] = blockers.get(first["constraint"], 0) + 1

    return {
        "all_lobes_reach_parity_zero": all(scan["feasible"] for scan in lobe_to_zero),
        "parity_zero_plane_connected": all(scan["feasible"] for scan in zero_pair_scans),
        "all_connected_by_parity_zero_detour": (
            all(scan["feasible"] for scan in lobe_to_zero)
            and all(scan["feasible"] for scan in zero_pair_scans)
        ),
        "lobe_to_zero_first_failure_blockers": blockers,
        "lobe_to_zero_worst_constraints": [
            scan["worst"]["constraint"] for scan in lobe_to_zero
        ],
        "minimum_worst_lobe_margin": min(
            float(scan["worst"]["margin"]) for scan in lobe_to_zero
        ),
        "direct_pair_failures": [
            {
                "pair": scan["pair"],
                "first_failure": scan["first_failure"],
            }
            for scan in direct_pair_scans
            if not scan["feasible"]
        ],
    }


def _sweep(
    centroids: list[np.ndarray],
    zero_points: list[np.ndarray],
    samples: int,
    values: list[float],
    factory: Callable[[float], Constraint],
) -> dict:
    rows = []
    for value in values:
        rows.append({
            "value": float(value),
            **_diagnose_stack(
                centroids,
                zero_points,
                _stack_with(factory(float(value))),
                samples=samples,
            ),
        })
    first_connecting = next(
        (
            row["value"]
            for row in rows
            if row["all_connected_by_parity_zero_detour"]
        ),
        None,
    )
    return {
        "rows": rows,
        "first_connecting_value": first_connecting,
    }


def diagnose_continuous_priors(
    phases_path: str | Path,
    samples: int = 101,
    thresholds: list[float] | None = None,
    floors: list[float] | None = None,
) -> dict:
    phases_doc = json.loads(Path(phases_path).read_text(encoding="utf-8"))
    centroids = _centroids(phases_doc)
    zero_points = [_parity_zero(x) for x in centroids]
    threshold_values = thresholds or list(DEFAULT_SWEEP_VALUES)
    floor_values = floors or list(DEFAULT_SWEEP_VALUES)

    variants = {
        "default": _diagnose_stack(
            centroids,
            zero_points,
            _base_stack(),
            samples=samples,
        ),
        "no_distance_prior": _diagnose_stack(
            centroids,
            zero_points,
            _without_distance_prior(),
            samples=samples,
        ),
        "hard_threshold_sweep": _sweep(
            centroids,
            zero_points,
            samples,
            threshold_values,
            lambda value: HardThresholdDistancePrior(threshold=value),
        ),
        "smooth_floor_sweep": _sweep(
            centroids,
            zero_points,
            samples,
            floor_values,
            lambda value: SmoothFloorDistancePrior(floor=value),
        ),
        "soft_active_log_sweep": _sweep(
            centroids,
            zero_points,
            samples,
            floor_values,
            lambda value: SoftActiveLogHierarchyPrior(floor=value),
        ),
        "sector_norm_threshold_sweep": _sweep(
            centroids,
            zero_points,
            samples,
            threshold_values,
            lambda value: SectorNormDistancePrior(threshold=value),
        ),
    }

    return {
        "input": str(phases_path),
        "basis": KEYS,
        "samples_per_segment": samples,
        "sweep_values": {
            "thresholds": threshold_values,
            "floors": floor_values,
        },
        "literature_guardrail": {
            "claim": (
                "The Swampland Distance Conjecture is a moduli-space statement "
                "about geodesic distance and towers of light states. These "
                "coefficient-space hierarchy priors are diagnostics, not a "
                "replacement for a moduli/tower model."
            ),
            "primary_sources": [
                {
                    "title": "Ooguri and Vafa, On the Geometry of the String Landscape and the Swampland",
                    "url": "https://arxiv.org/abs/hep-th/0605264",
                },
                {
                    "title": "Palti, The Swampland: Introduction and Review",
                    "url": "https://arxiv.org/abs/1903.06239",
                },
                {
                    "title": "Debusschere, Tonioni, and Van Riet, A distance conjecture beyond moduli?",
                    "url": "https://arxiv.org/html/2407.03715v3",
                },
            ],
        },
        "variants": variants,
        "interpretation": (
            "If multiple continuous or sectorized hierarchy priors reconnect the "
            "v2.13 parity lobes through the parity-zero plane, the four-lobe "
            "topology remains a functional-form artifact of the current distance "
            "prior rather than evidence for disconnected physical phases."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="experiments/results/v2.13/phases_8d_1200.json")
    parser.add_argument("--out", default="experiments/results/v2.16/continuous_distance_prior.json")
    parser.add_argument("--samples", type=int, default=101)
    parser.add_argument(
        "--thresholds",
        default=",".join(str(value) for value in DEFAULT_SWEEP_VALUES),
        help="comma-separated hard/sector threshold values",
    )
    parser.add_argument(
        "--floors",
        default=",".join(str(value) for value in DEFAULT_SWEEP_VALUES),
        help="comma-separated smooth/soft floor values",
    )
    args = parser.parse_args()

    result = diagnose_continuous_priors(
        args.input,
        samples=args.samples,
        thresholds=_parse_float_list(args.thresholds),
        floors=_parse_float_list(args.floors),
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
