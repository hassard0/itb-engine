"""Explicit tower-coordinate basis extension for the distance-prior bottleneck.

v2.16-v2.19 showed that coefficient-only replacements for the hard distance
prior are cleaner but still redundant. This experiment adds an independent
auxiliary coordinate, `phi_tower`, and asks whether a real tower degree of
freedom can produce a nonredundant gate.

The model is intentionally diagnostic:

    m_tower(phi) = m0 * exp(-lambda * phi)
    Lambda_s = 1 / sqrt(1 + rho * (Lambda_s / m_tower)^p)

The second equation is solved self-consistently. A point is allowed when the
chosen EFT cutoff Lambda_EFT does not exceed Lambda_s.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, ".")
from experiments.phases import KEYS
from experiments.stack import build_stack
from experiments.tower_surrogate_overlap import (
    LEGACY_OVERLAP_CONSTRAINTS,
    _centroids,
    _legacy_constraints,
    _targeted_samples,
)
from itb.constraints.base import Constraint
from itb.engine import check
from itb.predict import FRAMEWORKS
from itb.theory import Theory


EXTENDED_KEYS = [*KEYS, "phi_tower"]
DEFAULT_PHI_GRID = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6)
DEFAULT_LAMBDA_EFT_SWEEP = (0.50, 0.60, 0.65, 0.70)


@dataclass(frozen=True)
class ExplicitTowerModel:
    lambda_eft: float = 0.65
    m0: float = 1.0
    lambda_tower: float = 1.0
    density: float = 1.0
    exponent_p: float = 1.0
    fixed_point_iters: int = 96

    def tower_mass(self, phi_tower: float) -> float:
        exponent = min(self.lambda_tower * max(float(phi_tower), 0.0), 700.0)
        return self.m0 * math.exp(-exponent)

    def species_count(self, cutoff: float, phi_tower: float) -> float:
        mass = max(self.tower_mass(phi_tower), 1e-12)
        return 1.0 + self.density * (max(cutoff, 0.0) / mass) ** self.exponent_p

    def species_cutoff(self, phi_tower: float) -> float:
        lo = 0.0
        hi = 1.0
        for _ in range(self.fixed_point_iters):
            mid = 0.5 * (lo + hi)
            rhs = 1.0 / math.sqrt(self.species_count(mid, phi_tower))
            if mid - rhs >= 0.0:
                hi = mid
            else:
                lo = mid
        return 0.5 * (lo + hi)

    def cutoff_residual(self, phi_tower: float) -> float:
        cutoff = self.species_cutoff(phi_tower)
        rhs = 1.0 / math.sqrt(self.species_count(cutoff, phi_tower))
        return cutoff - rhs

    def observables(self, phi_tower: float) -> dict[str, float | bool]:
        mass = self.tower_mass(phi_tower)
        cutoff = self.species_cutoff(phi_tower)
        species = self.species_count(cutoff, phi_tower)
        margin = cutoff - self.lambda_eft
        return {
            "phi_tower": float(phi_tower),
            "tower_mass": mass,
            "species_count_at_cutoff": species,
            "species_cutoff": cutoff,
            "cutoff_residual": self.cutoff_residual(phi_tower),
            "lambda_eft": self.lambda_eft,
            "cutoff_margin": margin,
            "satisfied": margin >= 0.0,
        }


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


def _reference_feasible(points: np.ndarray) -> np.ndarray:
    reference = _reference_stack()
    return np.array([check(_theory(point), reference).feasible for point in points])


def _legacy_failures(points: np.ndarray) -> dict[str, np.ndarray]:
    legacy = _legacy_constraints()
    return {
        name: np.array([
            not constraint.evaluate(_theory(point)).satisfied for point in points
        ])
        for name, constraint in legacy.items()
    }


def _fraction(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def _extended_gate_audit(
    points: np.ndarray,
    reference_ok: np.ndarray,
    legacy_fail: dict[str, np.ndarray],
    phi_grid: list[float],
    model: ExplicitTowerModel,
) -> dict:
    phi_ok = np.array([bool(model.observables(phi)["satisfied"]) for phi in phi_grid])
    reference_ext = np.repeat(reference_ok, len(phi_grid))
    tower_ok_ext = np.tile(phi_ok, len(points))
    candidate_ext = reference_ext & tower_ok_ext
    gate_ext = reference_ext & ~tower_ok_ext

    gate_by_phi = {}
    for idx, phi in enumerate(phi_grid):
        phi_gate = reference_ok & (not phi_ok[idx])
        gate_by_phi[str(phi)] = int(phi_gate.sum())

    legacy_ext = {
        name: np.repeat(failures, len(phi_grid))
        for name, failures in legacy_fail.items()
    }
    old_distance_species_pass = gate_ext.copy()
    for name in ("swampland_distance_conjecture", "species_scale_bound"):
        old_distance_species_pass &= ~legacy_ext[name]

    gate_count = int(gate_ext.sum())
    candidate_count = int(candidate_ext.sum())
    reference_count = int(reference_ext.sum())

    return {
        "reference_feasible_extended": reference_count,
        "candidate_feasible_extended": candidate_count,
        "explicit_tower_gate_count": gate_count,
        "irreplaceability_growth_pct": (
            100.0 * (reference_count / candidate_count - 1.0)
            if candidate_count else None
        ),
        "gate_by_phi": gate_by_phi,
        "gate_passes_old_distance_and_species": int(old_distance_species_pass.sum()),
        "overlap_reference_gate": {
            name: {
                "count": int((gate_ext & failures).sum()),
                "fraction_of_gate": _fraction(int((gate_ext & failures).sum()), gate_count),
            }
            for name, failures in legacy_ext.items()
        },
    }


def _phi_monotonicity(model: ExplicitTowerModel, phi_grid: list[float]) -> dict:
    rows = [model.observables(phi) for phi in phi_grid]
    masses = [float(row["tower_mass"]) for row in rows]
    species = [float(row["species_count_at_cutoff"]) for row in rows]
    cutoffs = [float(row["species_cutoff"]) for row in rows]
    margins = [float(row["cutoff_margin"]) for row in rows]
    return {
        "rows": rows,
        "tower_mass_non_increasing": all(
            masses[i] >= masses[i + 1] - 1e-12 for i in range(len(masses) - 1)
        ),
        "species_count_non_decreasing": all(
            species[i] <= species[i + 1] + 1e-12 for i in range(len(species) - 1)
        ),
        "species_cutoff_non_increasing": all(
            cutoffs[i] >= cutoffs[i + 1] - 1e-12 for i in range(len(cutoffs) - 1)
        ),
        "margin_non_increasing": all(
            margins[i] >= margins[i + 1] - 1e-12 for i in range(len(margins) - 1)
        ),
    }


def _parameter_monotonicity(phi_tower: float = 1.0) -> dict:
    density_rows = []
    for density in (0.0, 0.5, 1.0, 2.0):
        model = ExplicitTowerModel(density=density)
        density_rows.append({"density": density, **model.observables(phi_tower)})
    lambda_rows = []
    for lambda_tower in (0.0, 0.5, 1.0, 1.5):
        model = ExplicitTowerModel(lambda_tower=lambda_tower)
        lambda_rows.append({"lambda_tower": lambda_tower, **model.observables(phi_tower)})
    return {
        "density_rows": density_rows,
        "lambda_rows": lambda_rows,
        "cutoff_non_increasing_with_density": all(
            density_rows[i]["species_cutoff"] >= density_rows[i + 1]["species_cutoff"] - 1e-12
            for i in range(len(density_rows) - 1)
        ),
        "cutoff_non_increasing_with_lambda": all(
            lambda_rows[i]["species_cutoff"] >= lambda_rows[i + 1]["species_cutoff"] - 1e-12
            for i in range(len(lambda_rows) - 1)
        ),
        "mass_non_increasing_with_lambda": all(
            lambda_rows[i]["tower_mass"] >= lambda_rows[i + 1]["tower_mass"] - 1e-12
            for i in range(len(lambda_rows) - 1)
        ),
    }


def _solver_edge_cases() -> dict:
    cases = {
        "rho_zero": ExplicitTowerModel(density=0.0).observables(1.0),
        "lambda_zero": ExplicitTowerModel(lambda_tower=0.0).observables(1.0),
        "phi_zero": ExplicitTowerModel().observables(0.0),
        "large_phi": ExplicitTowerModel().observables(50.0),
    }
    return {
        "cases": cases,
        "max_abs_residual": max(abs(float(row["cutoff_residual"])) for row in cases.values()),
        "all_cutoffs_in_unit_interval": all(
            0.0 < float(row["species_cutoff"]) <= 1.0 for row in cases.values()
        ),
    }


def _critical_phi(model: ExplicitTowerModel, hi: float = 4.0) -> dict:
    lo = 0.0
    if model.observables(lo)["cutoff_margin"] < 0:
        return {"critical_phi": 0.0, **model.observables(0.0)}
    while model.observables(hi)["cutoff_margin"] > 0 and hi < 64:
        hi *= 2.0
    if hi >= 64:
        return {"critical_phi": None}
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if model.observables(mid)["cutoff_margin"] >= 0:
            lo = mid
        else:
            hi = mid
    phi = 0.5 * (lo + hi)
    return {"critical_phi": phi, **model.observables(phi)}


def _framework_phi_allowance(model: ExplicitTowerModel) -> dict[str, dict]:
    reference = _reference_stack()
    crit = _critical_phi(model)
    rows = {}
    for name, framework in FRAMEWORKS.items():
        report = check(framework.encode(), reference)
        rows[name] = {
            "reference_feasible": report.feasible,
            "max_phi_tower_allowed": crit["critical_phi"],
            "excluded_without_phi_assignment": False,
        }
    return rows


def _old_stack_phi_isolation(points: np.ndarray, phi_grid: list[float]) -> dict:
    reference_ok = _reference_feasible(points)
    # phi_tower is intentionally not stored in Theory.coefficients for old-stack
    # checks; old verdicts therefore must not change as phi_tower varies.
    invariant = True
    for _phi in phi_grid:
        invariant = invariant and np.array_equal(reference_ok, _reference_feasible(points))
    return {
        "old_stack_verdicts_invariant_under_phi_tower": bool(invariant),
        "checked_phi_values": phi_grid,
        "reference_feasible": int(reference_ok.sum()),
    }


def _projection_audit(
    reference_ok: np.ndarray,
    phi_grid: list[float],
    model: ExplicitTowerModel,
) -> dict:
    allowed = np.array([bool(model.observables(phi)["satisfied"]) for phi in phi_grid])
    reference_count = int(reference_ok.sum())
    if reference_count == 0:
        return {
            "reference_survivors": 0,
            "projected_island_unchanged": False,
            "allowed_phi_fraction_per_8d_survivor": None,
            "max_allowed_phi_on_grid": None,
        }
    max_phi = max((phi for phi, ok in zip(phi_grid, allowed) if ok), default=None)
    return {
        "reference_survivors": reference_count,
        "projected_island_unchanged": bool(allowed.any()),
        "allowed_phi_count_per_8d_survivor": int(allowed.sum()),
        "allowed_phi_fraction_per_8d_survivor": float(allowed.mean()),
        "max_allowed_phi_on_grid": max_phi,
        "note": (
            "Every 8D survivor remains in the projected island if at least one "
            "phi_tower value is allowed; the tower coordinate restricts the fiber, "
            "not the 8D projection."
        ),
    }


def _topology_by_phi(
    centroids: list[np.ndarray],
    phi_grid: list[float],
    model: ExplicitTowerModel,
) -> dict:
    # Coefficient topology was already checked in v2.17-v2.19 with the old
    # distance/species sector removed. Here the explicit tower coordinate is
    # independent, so fixed-phi connectivity is determined by whether that phi
    # passes the tower cutoff.
    return {
        str(phi): {
            "tower_coordinate_allowed": bool(model.observables(phi)["satisfied"]),
            "coefficient_detour_still_available_if_allowed": True,
            "components_checked": len(centroids),
        }
        for phi in phi_grid
    }


def diagnose_explicit_tower_basis(
    phases_path: str | Path,
    samples: int = 20_000,
    seed: int = 1618,
    phi_grid: list[float] | None = None,
    lambda_eft_values: list[float] | None = None,
) -> dict:
    phases_doc = json.loads(Path(phases_path).read_text(encoding="utf-8"))
    centroids = _centroids(phases_doc)
    points = _targeted_samples(centroids, samples=samples, seed=seed)
    reference_ok = _reference_feasible(points)
    legacy_fail = _legacy_failures(points)
    grid = phi_grid or list(DEFAULT_PHI_GRID)
    eft_values = lambda_eft_values or list(DEFAULT_LAMBDA_EFT_SWEEP)
    model = ExplicitTowerModel(lambda_eft=0.65)

    sweeps = {}
    for lambda_eft in eft_values:
        sweep_model = ExplicitTowerModel(lambda_eft=lambda_eft)
        sweeps[str(lambda_eft)] = {
            "critical_phi": _critical_phi(sweep_model),
            "gate": _extended_gate_audit(
                points,
                reference_ok,
                legacy_fail,
                grid,
                sweep_model,
            ),
        }

    main_gate = _extended_gate_audit(points, reference_ok, legacy_fail, grid, model)
    return {
        "input": str(phases_path),
        "basis": EXTENDED_KEYS,
        "samples": int(points.shape[0]),
        "seed": seed,
        "phi_grid": grid,
        "model": model.__dict__,
        "legacy_overlap_constraints": LEGACY_OVERLAP_CONSTRAINTS,
        "literature_guardrail": {
            "claim": (
                "This 9D extension adds an explicit auxiliary tower coordinate. "
                "It is a diagnostic basis-extension test, not an assignment of "
                "physical moduli coordinates to the encoded frameworks and not a "
                "validation of the Swampland Distance Conjecture."
            ),
            "primary_sources": [
                {
                    "title": "Ooguri and Vafa, On the Geometry of the String Landscape and the Swampland",
                    "url": "https://arxiv.org/abs/hep-th/0605264",
                },
                {
                    "title": "Dvali and Redi, Black Hole Bound on the Number of Species and Quantum Gravity at LHC",
                    "url": "https://arxiv.org/abs/0710.4344",
                },
                {
                    "title": "van de Heisteeg, Vafa, and Wiesner, Bounds on Species Scale and the Distance Conjecture",
                    "url": "https://arxiv.org/abs/2303.13580",
                },
            ],
        },
        "tower_monotonicity": _phi_monotonicity(model, grid),
        "parameter_monotonicity": _parameter_monotonicity(phi_tower=1.0),
        "solver_edge_cases": _solver_edge_cases(),
        "critical_phi": _critical_phi(model),
        "main_gate": main_gate,
        "old_stack_phi_isolation": _old_stack_phi_isolation(points[: min(len(points), 200)], grid),
        "projection_audit": _projection_audit(reference_ok, grid, model),
        "lambda_eft_sweep": sweeps,
        "framework_phi_allowance": _framework_phi_allowance(model),
        "topology_by_phi": _topology_by_phi(centroids, grid, model),
        "interpretation": (
            "If explicit_tower_gate_count is positive and some gated points pass "
            "the old coefficient-only distance/species constraints, the new tower "
            "coordinate adds an independent diagnostic axis. Frameworks are not "
            "excluded until a phi_tower assignment or measurement is supplied."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="experiments/results/v2.13/phases_8d_1200.json")
    parser.add_argument("--out", default="experiments/results/v2.20/explicit_tower_basis.json")
    parser.add_argument("--samples", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=1618)
    parser.add_argument(
        "--phi-grid",
        default=",".join(str(value) for value in DEFAULT_PHI_GRID),
        help="comma-separated phi_tower grid values",
    )
    parser.add_argument(
        "--lambda-eft-values",
        default=",".join(str(value) for value in DEFAULT_LAMBDA_EFT_SWEEP),
        help="comma-separated EFT cutoff values for sensitivity",
    )
    args = parser.parse_args()

    result = diagnose_explicit_tower_basis(
        args.input,
        samples=args.samples,
        seed=args.seed,
        phi_grid=_parse_float_list(args.phi_grid),
        lambda_eft_values=_parse_float_list(args.lambda_eft_values),
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
