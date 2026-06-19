"""Irreplaceability/overlap audit for v2.17 tower surrogates.

v2.17 found that continuous tower/species surrogates pass the first topology and
framework sanity gate. This experiment asks whether those surrogates add an
independent wall or merely repackage existing aggregate curvature constraints.

The sampling is targeted around the v2.13 parity-lobe/bridge region plus broad
stress points in the same 8D box. It is a diagnostic audit, not a global volume
theorem.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, ".")
from experiments.phases import HI, KEYS, LO
from experiments.stack import build_stack
from experiments.tower_surrogate_distance import TOWER_MODES, TowerSpeciesSurrogatePrior
from itb.constraints.base import Constraint
from itb.engine import check
from itb.theory import Theory


LEGACY_OVERLAP_CONSTRAINTS = (
    "swampland_distance_conjecture",
    "species_scale_bound",
    "complexity_cutoff",
)


def _json_default(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    raise TypeError(f"cannot serialize {type(value).__name__}")


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


def _reference_stack() -> list[Constraint]:
    return [
        constraint
        for constraint in _base_stack()
        if constraint.name not in {
            "swampland_distance_conjecture",
            "species_scale_bound",
        }
    ]


def _legacy_constraints() -> dict[str, Constraint]:
    return {
        constraint.name: constraint
        for constraint in _base_stack()
        if constraint.name in LEGACY_OVERLAP_CONSTRAINTS
    }


def _targeted_samples(
    centroids: list[np.ndarray],
    samples: int,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    zero_points = [_parity_zero(centroid) for centroid in centroids]
    rows = []

    # Always include the known witnesses so tiny test runs are meaningful.
    rows.extend(centroids)
    rows.extend(zero_points)
    for centroid, zero in zip(centroids, zero_points):
        for t in np.linspace(0.0, 1.0, 9):
            rows.append(centroid + float(t) * (zero - centroid))

    while len(rows) < samples:
        draw = rng.random()
        if draw < 0.45:
            idx = int(rng.integers(0, len(centroids)))
            t = float(rng.random())
            base = centroids[idx] + t * (zero_points[idx] - centroids[idx])
            noise = rng.normal(0.0, [0.025, 0.02, 0.02, 0.015, 0.012, 0.025, 0.006, 0.006])
            x = base + noise
        elif draw < 0.75:
            i, j = rng.choice(len(centroids), size=2, replace=False)
            t = float(rng.random())
            x = centroids[i] + t * (centroids[j] - centroids[i])
            x += rng.normal(0.0, [0.02, 0.018, 0.018, 0.012, 0.01, 0.02, 0.004, 0.004])
        else:
            x = LO + (HI - LO) * rng.random(len(KEYS))
        rows.append(np.clip(x, LO, HI))

    return np.array(rows[:samples], dtype=float)


def _constraint_satisfied(constraint: Constraint, x: np.ndarray) -> bool:
    return bool(constraint.evaluate(_theory(x)).satisfied)


def _fraction(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def _mode_audit(
    mode: str,
    points: np.ndarray,
    reference: list[Constraint],
    legacy: dict[str, Constraint],
    N_max: float,
) -> dict:
    prior = TowerSpeciesSurrogatePrior(mode=mode, N_max=N_max)
    reference_feasible = np.array([
        check(_theory(point), reference).feasible for point in points
    ])
    prior_satisfied = np.array([
        _constraint_satisfied(prior, point) for point in points
    ])
    candidate_feasible = reference_feasible & prior_satisfied
    prior_fail = ~prior_satisfied
    reference_gate = reference_feasible & prior_fail

    legacy_fail = {
        name: np.array([
            not _constraint_satisfied(constraint, point) for point in points
        ])
        for name, constraint in legacy.items()
    }
    all_prior_fail_count = int(prior_fail.sum())
    reference_gate_count = int(reference_gate.sum())

    all_prior_overlap = {
        name: {
            "count": int((prior_fail & failures).sum()),
            "fraction_of_surrogate_failures": _fraction(
                int((prior_fail & failures).sum()),
                all_prior_fail_count,
            ),
        }
        for name, failures in legacy_fail.items()
    }
    reference_gate_overlap = {
        name: {
            "count": int((reference_gate & failures).sum()),
            "fraction_of_reference_gate": _fraction(
                int((reference_gate & failures).sum()),
                reference_gate_count,
            ),
        }
        for name, failures in legacy_fail.items()
    }
    pass_old_distance_and_species = reference_gate.copy()
    for name in ("swampland_distance_conjecture", "species_scale_bound"):
        pass_old_distance_and_species &= ~legacy_fail[name]

    candidate_count = int(candidate_feasible.sum())
    reference_count = int(reference_feasible.sum())
    growth_pct = None
    if candidate_count:
        growth_pct = 100.0 * (reference_count / candidate_count - 1.0)

    return {
        "mode": mode,
        "N_max": float(N_max),
        "reference_feasible": reference_count,
        "candidate_feasible": candidate_count,
        "surrogate_gate_count": reference_gate_count,
        "irreplaceability_growth_pct": growth_pct,
        "all_surrogate_failures": all_prior_fail_count,
        "overlap_all_surrogate_failures": all_prior_overlap,
        "overlap_reference_gate": reference_gate_overlap,
        "reference_gate_passes_old_distance_and_species": int(
            pass_old_distance_and_species.sum()
        ),
        "interpretation": (
            "reference_gate_count is the number of sampled points admitted by the "
            "corrected stack with old hard distance/species removed but rejected by "
            "this tower surrogate. irreplaceability_growth_pct is the sampled island "
            "growth when the surrogate is removed."
        ),
    }


def audit_tower_surrogate_overlap(
    phases_path: str | Path,
    samples: int = 20_000,
    seed: int = 2718,
    N_max: float = 3.0,
) -> dict:
    phases_doc = json.loads(Path(phases_path).read_text(encoding="utf-8"))
    centroids = _centroids(phases_doc)
    points = _targeted_samples(centroids, samples=samples, seed=seed)
    reference = _reference_stack()
    legacy = _legacy_constraints()
    mode_rows = {
        mode: _mode_audit(mode, points, reference, legacy, N_max=N_max)
        for mode in TOWER_MODES
    }

    return {
        "input": str(phases_path),
        "basis": KEYS,
        "samples": int(points.shape[0]),
        "seed": seed,
        "N_max": float(N_max),
        "sampling": (
            "targeted mixture of v2.13 centroids, parity-zero bridges, lobe-lobe "
            "segments with local jitter, and broad stress points in the v2.13 box"
        ),
        "legacy_overlap_constraints": LEGACY_OVERLAP_CONSTRAINTS,
        "modes": mode_rows,
        "interpretation": (
            "A low surrogate_gate_count means the tower surrogate is mostly redundant "
            "with the corrected stack on this targeted sample. A high overlap with "
            "old distance/species means it is reproducing the old aggregate-curvature "
            "sector rather than adding a new independent wall."
        ),
        "guardrail": (
            "This is a targeted overlap audit, not a global Monte Carlo volume theorem "
            "and not a validation of any surrogate as the physical SDC."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="experiments/results/v2.13/phases_8d_1200.json")
    parser.add_argument("--out", default="experiments/results/v2.18/tower_surrogate_overlap.json")
    parser.add_argument("--samples", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=2718)
    parser.add_argument("--n-max", type=float, default=3.0)
    args = parser.parse_args()

    result = audit_tower_surrogate_overlap(
        args.input,
        samples=args.samples,
        seed=args.seed,
        N_max=args.n_max,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
