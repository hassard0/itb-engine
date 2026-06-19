"""Observable thresholds for the explicit tower-coordinate axis (v2.21).

v2.20 found a nonredundant 9D tower gate, but no framework discrimination
without a `phi_tower` assignment. This experiment translates the gate into
observable thresholds: tower-mass floors, species-cutoff floors, and measured
phi intervals.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import (
    DEFAULT_PHI_GRID,
    ExplicitTowerModel,
    _critical_phi,
    _json_default,
    _parse_float_list,
)


DEFAULT_CONFIDENCE_FRACTIONS = (0.10, 0.25, 0.50, 0.75, 0.90)
DEFAULT_MASS_FLOORS = (0.20, 0.30, 0.40, 0.4755, 0.50, 0.60, 0.80)
DEFAULT_CUTOFF_FLOORS = (0.50, 0.60, 0.65, 0.70, 0.80)


def _allowed_fraction_from_grid(
    model: ExplicitTowerModel,
    phi_grid: list[float],
) -> float:
    allowed = [bool(model.observables(phi)["satisfied"]) for phi in phi_grid]
    return sum(allowed) / len(allowed)


def _phi_from_mass_floor(model: ExplicitTowerModel, mass_floor: float) -> float | None:
    if mass_floor <= 0.0:
        return None
    if mass_floor > model.m0:
        return 0.0
    return -math.log(mass_floor / model.m0) / model.lambda_tower


def _mass_floor_rows(model: ExplicitTowerModel, mass_floors: list[float]) -> list[dict]:
    critical = _critical_phi(model)["critical_phi"]
    rows = []
    for floor in mass_floors:
        phi_max = _phi_from_mass_floor(model, floor)
        if phi_max is None:
            excludes_tower_gate = False
        else:
            excludes_tower_gate = critical is not None and phi_max <= critical
        rows.append({
            "tower_mass_floor": floor,
            "implied_phi_tower_max": phi_max,
            "rules_out_tower_excluded_region": bool(excludes_tower_gate),
            "observable_statement": (
                "A lower bound m_tower >= floor implies phi_tower <= "
                "-log(floor/m0)/lambda_tower."
            ),
        })
    return rows


def _cutoff_floor_rows(model: ExplicitTowerModel, cutoff_floors: list[float]) -> list[dict]:
    rows = []
    for floor in cutoff_floors:
        threshold_model = ExplicitTowerModel(
            lambda_eft=floor,
            m0=model.m0,
            lambda_tower=model.lambda_tower,
            density=model.density,
            exponent_p=model.exponent_p,
        )
        crit = _critical_phi(threshold_model)
        rows.append({
            "species_cutoff_floor": floor,
            "implied_phi_tower_max": crit["critical_phi"],
            "tower_mass_at_threshold": crit.get("tower_mass"),
            "observable_statement": (
                "A lower bound Lambda_s >= floor permits phi_tower only below "
                "the listed critical value."
            ),
        })
    return rows


def _fiber_fraction_targets(
    phi_grid: list[float],
    confidence_fractions: list[float],
) -> list[dict]:
    lo = min(phi_grid)
    hi = max(phi_grid)
    width = hi - lo
    rows = []
    for fraction in confidence_fractions:
        phi_max = lo + fraction * width
        rows.append({
            "allowed_fiber_fraction_target": fraction,
            "required_phi_tower_upper_bound": phi_max,
            "required_tower_mass_floor": math.exp(-phi_max),
            "interpretation": (
                "For the uniform diagnostic phi_grid prior, this phi upper bound "
                "leaves approximately the listed fraction of the tower fiber."
            ),
        })
    return rows


def _measurement_scenarios(
    model: ExplicitTowerModel,
    phi_grid: list[float],
) -> list[dict]:
    scenarios = []
    critical_phi = _critical_phi(model)["critical_phi"]
    for measured_phi, sigma in (
        (0.25, 0.05),
        (0.55, 0.05),
        (0.75, 0.05),
        (0.95, 0.10),
        (1.20, 0.10),
    ):
        lower = max(min(phi_grid), measured_phi - 2.0 * sigma)
        upper = min(max(phi_grid), measured_phi + 2.0 * sigma)
        allowed_grid = [phi for phi in phi_grid if lower <= phi <= upper]
        compatible = [
            phi for phi in allowed_grid if bool(model.observables(phi)["satisfied"])
        ]
        scenarios.append({
            "measured_phi_tower": measured_phi,
            "sigma": sigma,
            "two_sigma_interval": [lower, upper],
            "grid_points_in_interval": len(allowed_grid),
            "compatible_allowed_grid_points": len(compatible),
            "rules_out_entire_tower_fiber": len(allowed_grid) > 0 and not compatible,
            "above_critical_phi": critical_phi is not None and lower > critical_phi,
        })
    return scenarios


def diagnose_tower_observable_thresholds(
    phi_grid: list[float] | None = None,
    lambda_eft_values: list[float] | None = None,
    mass_floors: list[float] | None = None,
    cutoff_floors: list[float] | None = None,
    confidence_fractions: list[float] | None = None,
) -> dict:
    grid = phi_grid or list(DEFAULT_PHI_GRID)
    eft_values = lambda_eft_values or [0.50, 0.60, 0.65, 0.70]
    masses = mass_floors or list(DEFAULT_MASS_FLOORS)
    cutoffs = cutoff_floors or list(DEFAULT_CUTOFF_FLOORS)
    fractions = confidence_fractions or list(DEFAULT_CONFIDENCE_FRACTIONS)
    model = ExplicitTowerModel(lambda_eft=0.65)

    eft_rows = []
    for lambda_eft in eft_values:
        sweep_model = ExplicitTowerModel(lambda_eft=lambda_eft)
        crit = _critical_phi(sweep_model)
        eft_rows.append({
            "lambda_eft": lambda_eft,
            "critical_phi_tower": crit["critical_phi"],
            "critical_tower_mass": crit.get("tower_mass"),
            "critical_species_cutoff": crit.get("species_cutoff"),
            "allowed_fraction_on_phi_grid": _allowed_fraction_from_grid(
                sweep_model,
                grid,
            ),
        })

    return {
        "basis": ["phi_tower", "m_tower", "Lambda_species"],
        "phi_grid": grid,
        "model": model.__dict__,
        "literature_guardrail": {
            "claim": (
                "These thresholds translate the v2.20 diagnostic tower coordinate "
                "into observable requirements. They do not assign phi_tower to any "
                "framework and do not constitute a physical SDC solution."
            ),
            "primary_sources": [
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
        "lambda_eft_thresholds": eft_rows,
        "tower_mass_floor_thresholds": _mass_floor_rows(model, masses),
        "species_cutoff_floor_thresholds": _cutoff_floor_rows(model, cutoffs),
        "fiber_fraction_targets": _fiber_fraction_targets(grid, fractions),
        "measurement_scenarios": _measurement_scenarios(model, grid),
        "interpretation": (
            "The explicit tower axis becomes a discriminator only after a tower "
            "observable bounds phi_tower, m_tower, or Lambda_species. Without that "
            "observable, the 8D framework projection remains unchanged."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/results/v2.21/tower_observable_thresholds.json")
    parser.add_argument(
        "--phi-grid",
        default=",".join(str(value) for value in DEFAULT_PHI_GRID),
        help="comma-separated phi_tower grid values",
    )
    parser.add_argument(
        "--lambda-eft-values",
        default="0.50,0.60,0.65,0.70",
        help="comma-separated EFT cutoff values",
    )
    args = parser.parse_args()

    result = diagnose_tower_observable_thresholds(
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
