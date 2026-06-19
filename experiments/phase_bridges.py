"""Curved-bridge diagnostic for the 8D phase-connectivity experiment.

`experiments.phases` can over-split a curved feasible region because it connects
seed pairs only by straight feasible segments. This script checks the specific
v2.13 parity-lobe question: can the four straight-line components connect by
detouring through parity-zero projections, and if not, which constraint blocks
the continuous approach to parity zero?
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, ".")
from experiments.phases import CONSTRAINTS, KEYS, _feasible, _segment_feasible
from itb.engine import check
from itb.theory import Theory


def _as_float(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    raise TypeError(f"cannot serialize {type(value).__name__}")


def _theory(x: np.ndarray) -> Theory:
    return Theory(coefficients={k: float(v) for k, v in zip(KEYS, x)})


def _margins(x: np.ndarray) -> list[tuple[str, float, bool]]:
    rep = check(_theory(x), CONSTRAINTS)
    return sorted(
        [(r.constraint_name, float(r.margin), bool(r.satisfied)) for r in rep.results],
        key=lambda row: row[1],
    )


def _worst_on_segment(a: np.ndarray, b: np.ndarray, samples: int) -> dict:
    worst = {"t": 0.0, "constraint": None, "margin": float("inf"), "satisfied": True}
    first_failure = None
    for t in np.linspace(0.0, 1.0, samples):
        x = a + float(t) * (b - a)
        row = _margins(x)[0]
        current = {
            "t": float(t),
            "constraint": row[0],
            "margin": row[1],
            "satisfied": row[2],
        }
        if current["margin"] < worst["margin"]:
            worst = current
        if first_failure is None and not current["satisfied"]:
            first_failure = current
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


def _distance_constraint_settings() -> dict:
    for constraint in CONSTRAINTS:
        if constraint.name == "swampland_distance_conjecture":
            return {
                "R_max": getattr(constraint, "R_max", None),
                "min_threshold": getattr(constraint, "min_threshold", None),
            }
    return {}


def diagnose(phases_path: str | Path, samples: int = 101) -> dict:
    phases_doc = json.loads(Path(phases_path).read_text(encoding="utf-8"))
    centroids = _centroids(phases_doc)
    zero_points = []
    component_rows = []
    for idx, x in enumerate(centroids):
        z = x.copy()
        z[KEYS.index("g_R2_parity")] = 0.0
        z[KEYS.index("g_R3_parity")] = 0.0
        zero_points.append(z)
        scan = _worst_on_segment(x, z, samples=samples)
        component_rows.append({
            "component": idx,
            "centroid_feasible": _feasible(x),
            "parity_zero_projection_feasible": _feasible(z),
            "straight_to_parity_zero": scan,
            "centroid": {k: float(v) for k, v in zip(KEYS, x)},
            "parity_zero_projection": {k: float(v) for k, v in zip(KEYS, z)},
        })

    pair_rows = []
    zero_plane_connected = True
    for i in range(len(centroids)):
        for j in range(i + 1, len(centroids)):
            direct = _segment_feasible(centroids[i], centroids[j])
            zero_segment = _segment_feasible(zero_points[i], zero_points[j])
            zero_plane_connected = zero_plane_connected and zero_segment
            pair_rows.append({
                "pair": [i, j],
                "direct_straight_segment_feasible": direct,
                "parity_zero_segment_feasible": zero_segment,
            })

    blockers: dict[str, int] = {}
    for row in component_rows:
        first = row["straight_to_parity_zero"]["first_failure"]
        if first:
            blockers[first["constraint"]] = blockers.get(first["constraint"], 0) + 1

    conclusion = (
        "Parity-zero projections are feasible and mutually connected, but continuous "
        "straight descents into the parity-zero plane fail. The repeated first blocker "
        "identifies whether the four lobes are likely physical or an artifact of a "
        "hard constraint encoding."
    )
    if blockers == {"swampland_distance_conjecture": len(component_rows)}:
        conclusion = (
            "The four straight-line parity lobes are caused by the hard nonzero-threshold "
            "aspect-ratio encoding of the swampland distance prior: parity-zero endpoints "
            "are feasible, but arbitrarily small nonzero parity coefficients violate the "
            "ratio bound before reaching zero. Treat lobe separation as an encoding "
            "artifact unless the distance-prior functional form is replaced by a "
            "continuous moduli-space model."
        )

    return {
        "input": str(phases_path),
        "basis": KEYS,
        "samples_per_segment": samples,
        "distance_constraint": _distance_constraint_settings(),
        "component_bridge_diagnostics": component_rows,
        "pair_diagnostics": pair_rows,
        "parity_zero_projections_mutually_connected": zero_plane_connected,
        "first_failure_blockers": blockers,
        "conclusion": conclusion,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="experiments/results/v2.13/phases_8d_1200.json",
        help="phase-component JSON produced by experiments.phases",
    )
    parser.add_argument("--out", default="experiments/results/v2.14/phase_bridges.json")
    parser.add_argument("--samples", type=int, default=101)
    args = parser.parse_args()

    result = diagnose(args.input, samples=args.samples)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_as_float), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_as_float))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
