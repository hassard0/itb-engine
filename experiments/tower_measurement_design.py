"""Tower-coordinate measurement design against assignment scenarios (v2.23).

v2.22 showed that framework-level tower exclusions depend on how `phi_tower`
is assigned to named frameworks. This experiment asks a narrower question:
which mock measurements would reduce that assignment ambiguity?

Measurements here test scenario assignments. They are not framework-level
predictions unless a framework supplies an independently justified `phi_tower`.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import ExplicitTowerModel, _critical_phi, _json_default
from experiments.tower_framework_scenarios import (
    _framework_reference_verdicts,
    _scenario_assignments,
    _scenario_verdict,
)


DEFAULT_MASS_FLOORS = (0.30, 0.40, 0.4755, 0.50, 0.60, 0.80)
DEFAULT_PHI_UPPER_BOUNDS = (0.40, 0.60, 0.7433, 0.80, 1.00)
DEFAULT_MEASURED_PHI_INTERVALS = (
    (0.25, 0.05),
    (0.55, 0.05),
    (0.75, 0.05),
    (0.95, 0.10),
    (1.20, 0.10),
)


@dataclass(frozen=True)
class MeasurementCandidate:
    label: str
    kind: str
    description: str
    lower_phi: float | None = None
    upper_phi: float | None = None
    tower_mass_floor: float | None = None

    def compatible(self, phi_tower: float) -> bool:
        if self.lower_phi is not None and phi_tower < self.lower_phi:
            return False
        if self.upper_phi is not None and phi_tower > self.upper_phi:
            return False
        return True


def _fmt(value: float) -> str:
    return f"{value:g}"


def _phi_from_mass_floor(model: ExplicitTowerModel, mass_floor: float) -> float | None:
    if mass_floor <= 0.0:
        return None
    if mass_floor > model.m0:
        return 0.0
    if model.lambda_tower <= 0.0:
        return None
    return -math.log(mass_floor / model.m0) / model.lambda_tower


def _measurement_candidates(
    model: ExplicitTowerModel,
    mass_floors: list[float],
    phi_upper_bounds: list[float],
    measured_phi_intervals: list[tuple[float, float]],
) -> list[MeasurementCandidate]:
    candidates: list[MeasurementCandidate] = []
    for floor in mass_floors:
        phi_max = _phi_from_mass_floor(model, floor)
        candidates.append(
            MeasurementCandidate(
                label=f"mass_floor_{_fmt(floor)}",
                kind="tower_mass_floor",
                description=(
                    f"Mock lower bound m_tower >= {_fmt(floor)}, equivalent to "
                    f"phi_tower <= {_fmt(phi_max)} for the diagnostic model."
                ),
                upper_phi=phi_max,
                tower_mass_floor=floor,
            )
        )

    for phi_max in phi_upper_bounds:
        candidates.append(
            MeasurementCandidate(
                label=f"phi_upper_{_fmt(phi_max)}",
                kind="phi_upper_bound",
                description=f"Mock direct upper bound phi_tower <= {_fmt(phi_max)}.",
                upper_phi=phi_max,
            )
        )

    for center, sigma in measured_phi_intervals:
        lower = center - 2.0 * sigma
        upper = center + 2.0 * sigma
        candidates.append(
            MeasurementCandidate(
                label=f"phi_interval_{_fmt(center)}_pm_{_fmt(sigma)}",
                kind="measured_phi_interval",
                description=(
                    f"Mock two-sigma phi_tower interval [{_fmt(lower)}, {_fmt(upper)}] "
                    f"from a measurement centered at {_fmt(center)}."
                ),
                lower_phi=lower,
                upper_phi=upper,
            )
        )
    return candidates


def _framework_row(
    name: str,
    row: dict,
    candidate: MeasurementCandidate,
    model: ExplicitTowerModel,
) -> dict:
    ref_ok = bool(row["reference_feasible"])
    phi = row.get("phi_tower")
    if phi is None:
        return {
            "reference_feasible": ref_ok,
            "phi_tower": None,
            "measurement_scoreable": False,
            "measurement_compatible": None,
            "tower_allowed": row.get("tower_allowed"),
            "survives_measurement_and_tower": ref_ok,
            "exclusion_reason": None,
        }

    measurement_compatible = candidate.compatible(float(phi))
    tower = model.observables(float(phi))
    tower_allowed = bool(tower["satisfied"])
    survives = ref_ok and measurement_compatible and tower_allowed
    if not ref_ok:
        reason = "reference_excluded"
    elif not measurement_compatible:
        reason = "measurement_incompatible_assignment"
    elif not tower_allowed:
        reason = "tower_cutoff_excluded"
    else:
        reason = None
    return {
        "reference_feasible": ref_ok,
        "phi_tower": phi,
        "measurement_scoreable": True,
        "measurement_compatible": measurement_compatible,
        "tower_allowed": tower_allowed,
        "tower_mass": tower["tower_mass"],
        "species_cutoff": tower["species_cutoff"],
        "survives_measurement_and_tower": survives,
        "exclusion_reason": reason,
    }


def _evaluate_candidate(
    candidate: MeasurementCandidate,
    model: ExplicitTowerModel,
    scenarios: dict[str, dict],
    reference_feasible: list[str],
) -> dict:
    scenario_results = {}
    scoreable_results = {}
    for scenario_name, scenario in scenarios.items():
        rows = {
            name: _framework_row(name, row, candidate, model)
            for name, row in scenario["frameworks"].items()
        }
        scoreable = all(
            rows[name]["measurement_scoreable"]
            for name in reference_feasible
        )
        survivors = sorted(
            name
            for name in reference_feasible
            if rows[name]["survives_measurement_and_tower"]
        )
        premeasurement_survivors = sorted(
            name
            for name in reference_feasible
            if scenario["frameworks"][name]["final_feasible"]
        )
        newly_excluded = sorted(set(premeasurement_survivors) - set(survivors))
        measurement_incompatible = sorted(
            name
            for name in reference_feasible
            if rows[name]["exclusion_reason"] == "measurement_incompatible_assignment"
        )
        tower_excluded = sorted(
            name
            for name in reference_feasible
            if rows[name]["exclusion_reason"] == "tower_cutoff_excluded"
        )
        result = {
            "measurement_scoreable": scoreable,
            "unscoreable_reason": (
                None if scoreable else "phi_tower is unassigned for at least one reference-feasible framework"
            ),
            "premeasurement_surviving_reference_feasible": premeasurement_survivors,
            "n_premeasurement_surviving_reference_feasible": len(premeasurement_survivors),
            "surviving_reference_feasible": survivors,
            "n_surviving_reference_feasible": len(survivors),
            "newly_excluded_reference_feasible": newly_excluded,
            "n_newly_excluded_reference_feasible": len(newly_excluded),
            "measurement_incompatible_reference_feasible": measurement_incompatible,
            "n_measurement_incompatible_reference_feasible": len(measurement_incompatible),
            "tower_excluded_reference_feasible": tower_excluded,
            "n_tower_excluded_reference_feasible": len(tower_excluded),
            "scenario_ruled_out_before_measurement": (
                scoreable and len(premeasurement_survivors) == 0
            ),
            "scenario_ruled_out_after_measurement": scoreable and len(survivors) == 0,
            "scenario_newly_ruled_out_by_measurement": (
                scoreable and len(premeasurement_survivors) > 0 and len(survivors) == 0
            ),
            "scenario_reduced_by_measurement": (
                scoreable and len(survivors) < len(premeasurement_survivors)
            ),
            "frameworks": rows,
        }
        scenario_results[scenario_name] = result
        if scoreable:
            scoreable_results[scenario_name] = result

    ruled_out_scenarios = sorted(
        name
        for name, row in scoreable_results.items()
        if row["scenario_ruled_out_after_measurement"]
    )
    premeasurement_ruled_out_scenarios = sorted(
        name
        for name, row in scoreable_results.items()
        if row["scenario_ruled_out_before_measurement"]
    )
    newly_ruled_out_scenarios = sorted(
        name
        for name, row in scoreable_results.items()
        if row["scenario_newly_ruled_out_by_measurement"]
    )
    reduced_scenarios = sorted(
        name
        for name, row in scoreable_results.items()
        if row["scenario_reduced_by_measurement"]
    )
    surviving_scoreable = {
        name: row
        for name, row in scoreable_results.items()
        if not row["scenario_ruled_out_after_measurement"]
    }
    survivor_counts = [
        row["n_surviving_reference_feasible"]
        for row in scoreable_results.values()
    ]
    premeasurement_counts = [
        row["n_premeasurement_surviving_reference_feasible"]
        for row in scoreable_results.values()
    ]
    survivor_reduction_total = sum(
        row["n_premeasurement_surviving_reference_feasible"]
        - row["n_surviving_reference_feasible"]
        for row in scoreable_results.values()
    )
    surviving_union = set()
    for row in surviving_scoreable.values():
        surviving_union.update(row["surviving_reference_feasible"])
    conditional_absent = sorted(set(reference_feasible) - surviving_union) if surviving_scoreable else []

    return {
        "measurement": {
            "label": candidate.label,
            "kind": candidate.kind,
            "description": candidate.description,
            "lower_phi": candidate.lower_phi,
            "upper_phi": candidate.upper_phi,
            "tower_mass_floor": candidate.tower_mass_floor,
        },
        "scenario_results": scenario_results,
        "scoreable_scenarios": sorted(scoreable_results),
        "unscoreable_scenarios": sorted(set(scenarios) - set(scoreable_results)),
        "ruled_out_scoreable_scenarios": ruled_out_scenarios,
        "n_ruled_out_scoreable_scenarios": len(ruled_out_scenarios),
        "premeasurement_ruled_out_scoreable_scenarios": premeasurement_ruled_out_scenarios,
        "newly_ruled_out_scoreable_scenarios": newly_ruled_out_scenarios,
        "n_newly_ruled_out_scoreable_scenarios": len(newly_ruled_out_scenarios),
        "measurement_reduced_scoreable_scenarios": reduced_scenarios,
        "n_measurement_reduced_scoreable_scenarios": len(reduced_scenarios),
        "total_reference_feasible_survivor_reduction": survivor_reduction_total,
        "surviving_scoreable_scenarios": sorted(surviving_scoreable),
        "premeasurement_survivor_count_range_scoreable_scenarios": [
            min(premeasurement_counts) if premeasurement_counts else None,
            max(premeasurement_counts) if premeasurement_counts else None,
        ],
        "survivor_count_range_scoreable_scenarios": [
            min(survivor_counts) if survivor_counts else None,
            max(survivor_counts) if survivor_counts else None,
        ],
        "scenario_survivor_count_spread": (
            max(survivor_counts) - min(survivor_counts)
            if survivor_counts else None
        ),
        "conditional_frameworks_absent_from_all_surviving_scoreable_scenarios": conditional_absent,
        "claimable_framework_exclusions": [],
        "claim_guardrail": (
            "This measurement can reject or rank assignment scenarios. It is not "
            "a framework exclusion unless phi_tower is independently predicted "
            "for each framework or measured for the realized framework."
        ),
    }


def _rank_key(row: dict) -> tuple[int, int, int, int]:
    spread = row["scenario_survivor_count_spread"] or 0
    portfolio_collapse = not row["surviving_scoreable_scenarios"]
    return (
        int(portfolio_collapse),
        -row["n_newly_ruled_out_scoreable_scenarios"],
        -row["total_reference_feasible_survivor_reduction"],
        -spread,
    )


def diagnose_tower_measurement_design(
    mass_floors: list[float] | None = None,
    phi_upper_bounds: list[float] | None = None,
    measured_phi_intervals: list[tuple[float, float]] | None = None,
) -> dict:
    model = ExplicitTowerModel(lambda_eft=0.65)
    reference = _framework_reference_verdicts()
    assignments = _scenario_assignments()
    scenarios = {
        name: _scenario_verdict(assignment, model, reference)
        for name, assignment in assignments.items()
    }
    reference_feasible = scenarios["unassigned"]["reference_feasible_frameworks"]
    candidates = _measurement_candidates(
        model=model,
        mass_floors=list(DEFAULT_MASS_FLOORS) if mass_floors is None else mass_floors,
        phi_upper_bounds=(
            list(DEFAULT_PHI_UPPER_BOUNDS)
            if phi_upper_bounds is None
            else phi_upper_bounds
        ),
        measured_phi_intervals=(
            list(DEFAULT_MEASURED_PHI_INTERVALS)
            if measured_phi_intervals is None
            else measured_phi_intervals
        ),
    )
    evaluations = [
        _evaluate_candidate(candidate, model, scenarios, reference_feasible)
        for candidate in candidates
    ]
    evaluations.sort(key=_rank_key)
    scenario_disambiguators = [
        row
        for row in evaluations
        if (
            row["surviving_scoreable_scenarios"]
            and row["n_measurement_reduced_scoreable_scenarios"] > 0
        )
    ]
    model_crisis_measurements = [
        row for row in evaluations if not row["surviving_scoreable_scenarios"]
    ]
    no_incremental_measurement_impact = [
        row
        for row in evaluations
        if (
            row["surviving_scoreable_scenarios"]
            and row["n_measurement_reduced_scoreable_scenarios"] == 0
        )
    ]
    best = scenario_disambiguators[:5]

    return {
        "basis": ["phi_tower", "m_tower", "Lambda_species"],
        "model": model.__dict__,
        "critical_phi_tower": _critical_phi(model)["critical_phi"],
        "reference_feasible_frameworks": reference_feasible,
        "candidate_measurements": evaluations,
        "top_measurement_designs": [
            {
                "label": row["measurement"]["label"],
                "kind": row["measurement"]["kind"],
                "n_newly_ruled_out_scoreable_scenarios": (
                    row["n_newly_ruled_out_scoreable_scenarios"]
                ),
                "newly_ruled_out_scoreable_scenarios": (
                    row["newly_ruled_out_scoreable_scenarios"]
                ),
                "measurement_reduced_scoreable_scenarios": (
                    row["measurement_reduced_scoreable_scenarios"]
                ),
                "total_reference_feasible_survivor_reduction": (
                    row["total_reference_feasible_survivor_reduction"]
                ),
                "survivor_count_range_scoreable_scenarios": (
                    row["survivor_count_range_scoreable_scenarios"]
                ),
                "scenario_survivor_count_spread": row["scenario_survivor_count_spread"],
                "claimable_framework_exclusions": row["claimable_framework_exclusions"],
            }
            for row in best
        ],
        "no_incremental_measurement_impact": [
            {
                "label": row["measurement"]["label"],
                "kind": row["measurement"]["kind"],
                "premeasurement_ruled_out_scoreable_scenarios": (
                    row["premeasurement_ruled_out_scoreable_scenarios"]
                ),
            }
            for row in no_incremental_measurement_impact
        ],
        "model_crisis_measurements": [
            {
                "label": row["measurement"]["label"],
                "kind": row["measurement"]["kind"],
                "ruled_out_scoreable_scenarios": row["ruled_out_scoreable_scenarios"],
                "interpretation": (
                    "This candidate leaves no evaluated assigned scenario with a "
                    "reference-feasible survivor. Treat it as a stress test of the "
                    "tower model or scenario portfolio, not a clean discriminator."
                ),
            }
            for row in model_crisis_measurements
        ],
        "literature_guardrail": {
            "claim": (
                "This is a measurement design audit, not framework exclusion. "
                "It treats phi_tower observations as tests of assignment scenarios "
                "until a framework-specific tower model is supplied."
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
        "interpretation": (
            "Tower observations can make the assignment problem experimentally "
            "sharp: strong mass floors or phi upper bounds eliminate high-phi "
            "assignment scenarios. They still do not create a claimable framework "
            "exclusion while the unassigned scenario remains viable."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/results/v2.23/tower_measurement_design.json")
    args = parser.parse_args()

    result = diagnose_tower_measurement_design()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
