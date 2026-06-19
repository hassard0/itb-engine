"""Framework-level tower-coordinate assignment scenarios (v2.22).

v2.21 translated the explicit tower axis into observable thresholds but did
not assign `phi_tower` to any named framework. This experiment asks how much
framework discrimination depends on the assignment assumption.

The assignments here are scenarios, not physics claims.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import ExplicitTowerModel, _critical_phi, _json_default
from experiments.stack import build_stack
from itb.engine import check
from itb.predict import FRAMEWORKS


CURVATURE_KEYS = ("g_R2", "g_C", "g_R3")
PARITY_KEYS = ("g_R2_parity", "g_R3_parity")


def _reference_stack():
    return [
        constraint
        for constraint in build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
        if constraint.name not in {
            "swampland_distance_conjecture",
            "species_scale_bound",
        }
    ]


def _curvature_load(name: str) -> float:
    c = FRAMEWORKS[name].encode().coefficients
    return sum(abs(float(c.get(key, 0.0))) for key in CURVATURE_KEYS)


def _parity_load(name: str) -> float:
    c = FRAMEWORKS[name].encode().coefficients
    return math.sqrt(sum(float(c.get(key, 0.0)) ** 2 for key in PARITY_KEYS))


def _framework_reference_verdicts() -> dict[str, dict]:
    stack = _reference_stack()
    rows = {}
    for name, framework in FRAMEWORKS.items():
        report = check(framework.encode(), stack)
        rows[name] = {
            "reference_feasible": report.feasible,
            "binding": report.binding,
            "curvature_load": _curvature_load(name),
            "parity_load": _parity_load(name),
        }
    return rows


def _ranked_assignment(
    weight_curvature: float,
    weight_parity: float,
    max_phi: float,
) -> dict[str, float]:
    scores = {
        name: weight_curvature * _curvature_load(name) + weight_parity * _parity_load(name)
        for name in FRAMEWORKS
    }
    max_score = max(scores.values()) or 1.0
    return {name: max_phi * score / max_score for name, score in scores.items()}


def _scenario_assignments() -> dict[str, dict[str, float | None]]:
    names = list(FRAMEWORKS)
    return {
        "unassigned": {name: None for name in names},
        "low_phi_all": {name: 0.25 for name in names},
        "near_threshold_all": {name: 0.75 for name in names},
        "curvature_ranked_moderate": _ranked_assignment(
            weight_curvature=1.0,
            weight_parity=0.0,
            max_phi=0.70,
        ),
        "curvature_ranked_strong": _ranked_assignment(
            weight_curvature=1.0,
            weight_parity=0.0,
            max_phi=1.20,
        ),
        "curvature_plus_parity_strong": _ranked_assignment(
            weight_curvature=1.0,
            weight_parity=3.0,
            max_phi=1.20,
        ),
    }


def _scenario_verdict(
    assignments: dict[str, float | None],
    model: ExplicitTowerModel,
    reference: dict[str, dict],
) -> dict:
    critical = _critical_phi(model)["critical_phi"]
    rows = {}
    tower_excluded = []
    unassigned = []
    for name, phi in assignments.items():
        ref_ok = bool(reference[name]["reference_feasible"])
        if phi is None:
            unassigned.append(name)
            rows[name] = {
                **reference[name],
                "phi_tower": None,
                "tower_assigned": False,
                "tower_allowed": None,
                "final_feasible": ref_ok,
                "tower_excluded": False,
            }
            continue
        tower = model.observables(phi)
        tower_allowed = bool(tower["satisfied"])
        final_feasible = ref_ok and tower_allowed
        excluded = ref_ok and not tower_allowed
        if excluded:
            tower_excluded.append(name)
        rows[name] = {
            **reference[name],
            "phi_tower": phi,
            "tower_assigned": True,
            "tower_allowed": tower_allowed,
            "tower_mass": tower["tower_mass"],
            "species_cutoff": tower["species_cutoff"],
            "cutoff_margin": tower["cutoff_margin"],
            "critical_phi_tower": critical,
            "final_feasible": final_feasible,
            "tower_excluded": excluded,
        }

    ref_feasible = [name for name, row in reference.items() if row["reference_feasible"]]
    return {
        "critical_phi_tower": critical,
        "reference_feasible_frameworks": ref_feasible,
        "n_reference_feasible": len(ref_feasible),
        "tower_excluded_reference_feasible": tower_excluded,
        "n_tower_excluded_reference_feasible": len(tower_excluded),
        "unassigned_frameworks": unassigned,
        "frameworks": rows,
    }


def diagnose_tower_framework_scenarios() -> dict:
    model = ExplicitTowerModel(lambda_eft=0.65)
    reference = _framework_reference_verdicts()
    scenarios = {
        name: _scenario_verdict(assignments, model, reference)
        for name, assignments in _scenario_assignments().items()
    }
    assigned_scenarios = [
        row for name, row in scenarios.items() if name != "unassigned"
    ]
    robust_exclusions = set(assigned_scenarios[0]["tower_excluded_reference_feasible"])
    for row in assigned_scenarios[1:]:
        robust_exclusions &= set(row["tower_excluded_reference_feasible"])

    any_exclusion = sorted({
        framework
        for row in assigned_scenarios
        for framework in row["tower_excluded_reference_feasible"]
    })

    return {
        "model": model.__dict__,
        "critical_phi_tower": _critical_phi(model)["critical_phi"],
        "literature_guardrail": {
            "claim": (
                "These are framework-level phi_tower assignment scenarios. They are "
                "not framework predictions and do not constitute physical SDC "
                "discrimination without an independently justified phi_tower model "
                "or measurement."
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
        "scenarios": scenarios,
        "robust_tower_exclusions_across_assigned_scenarios": sorted(robust_exclusions),
        "frameworks_excluded_in_at_least_one_assigned_scenario": any_exclusion,
        "interpretation": (
            "Tower-coordinate framework discrimination is scenario-dependent. A "
            "framework is robustly excluded only if it fails across all explicit "
            "assignment scenarios; otherwise the result is a requirement for a "
            "better phi_tower assignment, not a framework verdict."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/results/v2.22/tower_framework_scenarios.json")
    args = parser.parse_args()

    result = diagnose_tower_framework_scenarios()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
