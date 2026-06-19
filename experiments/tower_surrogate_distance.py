"""Tower/species surrogate diagnostics for replacing the hard distance prior.

The current `swampland_distance_conjecture` proxy is a discontinuous coefficient
aspect-ratio bound. v2.16 showed that smoothing or sectorizing that proxy
reconnects the v2.13 parity lobes. This experiment asks a narrower next
question: do simple continuous tower/species surrogates pass basic acceptance
tests before we consider using them as replacements?
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, ".")
from experiments.phases import KEYS
from experiments.stack import build_stack
from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.engine import check
from itb.predict import FRAMEWORKS
from itb.theory import Theory


TOWER_MODES = (
    "curvature_l1",
    "curvature_l2",
    "curvature_plus_parity_l2",
    "curvature_l2_plus_parity_norm",
)
DEFAULT_NMAX_VALUES = (2.0, 2.2, 2.4, 2.6, 2.8, 3.0)
EPSILON_VALUES = (0.0, 1e-8, 1e-6, 1e-4, 1e-3, 0.01, 0.1, 1.0)
CURVATURE_SCALE_VALUES = (0.0, 0.5, 1.0, 1.5, 2.0)
CURVATURE_KEYS = ("g_R2", "g_C", "g_R3")
PARITY_KEYS = ("g_R2_parity", "g_R3_parity")


class TowerSpeciesSurrogatePrior(Constraint):
    """Continuous tower-load surrogate for species/distance diagnostics.

    This is not a canonical Swampland Distance Conjecture. It is an acceptance
    test for surrogate priors with explicit tower/species semantics:

        N_tower(g) = 1 + nu * tower_load(g) <= N_max.
    """

    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(
        self,
        mode: str,
        N_max: float = 3.0,
        nu: float = 2.0,
        parity_weight: float = 1.0,
    ):
        if mode not in TOWER_MODES:
            raise ValueError(f"unknown tower surrogate mode: {mode}")
        self.mode = mode
        self.N_max = float(N_max)
        self.nu = float(nu)
        self.parity_weight = float(parity_weight)
        self.name = f"tower_species_surrogate_{mode}"
        self.citation = "v2.17 continuous species/tower surrogate diagnostic"

    def _curvature_values(self, theory: Theory) -> list[float]:
        return [float(theory.coefficients.get(key, 0.0)) for key in CURVATURE_KEYS]

    def _parity_values(self, theory: Theory) -> list[float]:
        return [float(theory.coefficients.get(key, 0.0)) for key in PARITY_KEYS]

    def tower_load(self, theory: Theory) -> float:
        curvature = self._curvature_values(theory)
        parity = self._parity_values(theory)
        if self.mode == "curvature_l1":
            return sum(abs(value) for value in curvature)
        if self.mode == "curvature_l2":
            return math.sqrt(sum(value * value for value in curvature))
        if self.mode == "curvature_plus_parity_l2":
            return math.sqrt(
                sum(value * value for value in curvature)
                + self.parity_weight * sum(value * value for value in parity)
            )
        if self.mode == "curvature_l2_plus_parity_norm":
            curvature_norm = math.sqrt(sum(value * value for value in curvature))
            parity_norm = math.sqrt(sum(value * value for value in parity))
            return curvature_norm + self.parity_weight * parity_norm
        raise AssertionError("mode validated in __init__")

    def tower_species(self, theory: Theory) -> float:
        return 1.0 + self.nu * self.tower_load(theory)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        load = self.tower_load(theory)
        species = 1.0 + self.nu * load
        margin = self.N_max - species
        return ConstraintResult(
            self.name,
            margin >= 0.0,
            margin,
            margin,
            {
                "mode": self.mode,
                "tower_load": load,
                "N_tower": species,
                "N_max": self.N_max,
                "nu": self.nu,
                "parity_weight": self.parity_weight,
                "bound": "1 + nu*tower_load(g) <= N_max",
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


def _remove_constraints(names: set[str]) -> list[Constraint]:
    return [constraint for constraint in _base_stack() if constraint.name not in names]


def _stack_with_tower(prior: TowerSpeciesSurrogatePrior) -> list[Constraint]:
    return _remove_constraints({"swampland_distance_conjecture", "species_scale_bound"}) + [prior]


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


def _topology_diagnostic(
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
        "minimum_worst_lobe_margin": min(
            float(scan["worst"]["margin"]) for scan in lobe_to_zero
        ),
        "direct_pair_failures": [
            {"pair": scan["pair"], "first_failure": scan["first_failure"]}
            for scan in direct_pair_scans
            if not scan["feasible"]
        ],
    }


def _framework_verdicts(constraints: list[Constraint]) -> dict[str, dict]:
    verdicts = {}
    for name, framework in FRAMEWORKS.items():
        report = check(framework.encode(), constraints)
        worst = min(report.results, key=lambda result: result.margin)
        verdicts[name] = {
            "feasible": report.feasible,
            "binding": report.binding,
            "worst_constraint": worst.constraint_name,
            "worst_margin": float(worst.margin),
        }
    return verdicts


def _framework_summary(
    constraints: list[Constraint],
    reference_constraints: list[Constraint],
    prior: TowerSpeciesSurrogatePrior | None = None,
) -> dict:
    reference = _framework_verdicts(reference_constraints)
    candidate = _framework_verdicts(constraints)
    additional_exclusions = [
        name
        for name, verdict in candidate.items()
        if reference[name]["feasible"] and not verdict["feasible"]
    ]
    rescued = [
        name
        for name, verdict in candidate.items()
        if not reference[name]["feasible"] and verdict["feasible"]
    ]
    prior_only_failures = []
    prior_loads = {}
    if prior is not None:
        for name, framework in FRAMEWORKS.items():
            theory = framework.encode()
            prior_report = check(theory, [prior])
            prior_loads[name] = {
                "N_tower": prior.tower_species(theory),
                "tower_load": prior.tower_load(theory),
                "satisfied": prior_report.feasible,
            }
            if not prior_report.feasible:
                prior_only_failures.append(name)
    return {
        "reference_feasible_count": sum(v["feasible"] for v in reference.values()),
        "candidate_feasible_count": sum(v["feasible"] for v in candidate.values()),
        "additional_exclusions_vs_reference": additional_exclusions,
        "rescued_vs_reference": rescued,
        "prior_only_failures": prior_only_failures,
        "prior_loads": prior_loads,
    }


def _centroid_loads(centroids: list[np.ndarray], prior: TowerSpeciesSurrogatePrior) -> list[dict]:
    rows = []
    for idx, centroid in enumerate(centroids):
        theory = _theory(centroid)
        zero = _theory(_parity_zero(centroid))
        rows.append({
            "component": idx,
            "N_tower_centroid": prior.tower_species(theory),
            "N_tower_parity_zero": prior.tower_species(zero),
            "tower_load_centroid": prior.tower_load(theory),
            "tower_load_parity_zero": prior.tower_load(zero),
        })
    return rows


def _epsilon_to_zero_continuity(
    centroids: list[np.ndarray],
    constraints: list[Constraint],
    prior: TowerSpeciesSurrogatePrior,
) -> dict:
    component_rows = []
    punctured_components = []
    for idx, centroid in enumerate(centroids):
        rows = []
        for epsilon in EPSILON_VALUES:
            x = centroid.copy()
            x[KEYS.index("g_R2_parity")] *= epsilon
            x[KEYS.index("g_R3_parity")] *= epsilon
            theory = _theory(x)
            report = check(theory, constraints)
            prior_result = prior.evaluate(theory)
            rows.append({
                "epsilon": float(epsilon),
                "full_stack_feasible": report.feasible,
                "prior_margin": float(prior_result.margin),
                "N_tower": prior.tower_species(theory),
            })
        endpoint_zero = rows[0]["full_stack_feasible"]
        punctured_gap = bool(
            endpoint_zero
            and any(not row["full_stack_feasible"] for row in rows[1:-1])
        )
        if punctured_gap:
            punctured_components.append(idx)
        component_rows.append({
            "component": idx,
            "punctured_gap_near_zero": punctured_gap,
            "rows": rows,
        })
    return {
        "has_punctured_gap_near_zero": bool(punctured_components),
        "punctured_components": punctured_components,
        "components": component_rows,
    }


def _curvature_monotonicity(prior: TowerSpeciesSurrogatePrior) -> dict:
    base = {key: 0.0 for key in KEYS}
    base.update({
        "g_4": 0.55,
        "g_6": 0.35,
        "g_8": 0.35,
        "g_R2": 0.24,
        "g_C": 0.34,
        "g_R3": 0.11,
        "g_R2_parity": 0.05,
        "g_R3_parity": 0.03,
    })
    rows = []
    for scale in CURVATURE_SCALE_VALUES:
        coefficients = dict(base)
        for key in CURVATURE_KEYS:
            coefficients[key] = base[key] * scale
        theory = Theory(coefficients=coefficients)
        result = prior.evaluate(theory)
        rows.append({
            "curvature_scale": float(scale),
            "tower_load": prior.tower_load(theory),
            "N_tower": prior.tower_species(theory),
            "margin": float(result.margin),
        })
    loads = [row["tower_load"] for row in rows]
    margins = [row["margin"] for row in rows]
    return {
        "rows": rows,
        "tower_load_non_decreasing": all(
            loads[i] <= loads[i + 1] + 1e-12 for i in range(len(loads) - 1)
        ),
        "margin_non_increasing": all(
            margins[i] >= margins[i + 1] - 1e-12 for i in range(len(margins) - 1)
        ),
    }


def _candidate_result(
    mode: str,
    nmax: float,
    centroids: list[np.ndarray],
    zero_points: list[np.ndarray],
    reference_constraints: list[Constraint],
    samples: int,
) -> dict:
    prior = TowerSpeciesSurrogatePrior(mode=mode, N_max=nmax)
    constraints = _stack_with_tower(prior)
    topology = _topology_diagnostic(centroids, zero_points, constraints, samples=samples)
    framework = _framework_summary(constraints, reference_constraints, prior=prior)
    accepted = (
        topology["all_connected_by_parity_zero_detour"]
        and not framework["additional_exclusions_vs_reference"]
        and not framework["prior_only_failures"]
    )
    return {
        "mode": mode,
        "N_max": float(nmax),
        "accepted_basic_surrogate_gate": accepted,
        "topology": topology,
        "frameworks": framework,
        "centroid_tower_loads": _centroid_loads(centroids, prior),
        "epsilon_to_zero_continuity": _epsilon_to_zero_continuity(
            centroids,
            constraints,
            prior,
        ),
        "curvature_monotonicity": _curvature_monotonicity(prior),
    }


def diagnose_tower_surrogates(
    phases_path: str | Path,
    samples: int = 101,
    nmax_values: list[float] | None = None,
) -> dict:
    phases_doc = json.loads(Path(phases_path).read_text(encoding="utf-8"))
    centroids = _centroids(phases_doc)
    zero_points = [_parity_zero(x) for x in centroids]
    nmax_sweep = nmax_values or list(DEFAULT_NMAX_VALUES)
    default_stack = _base_stack()
    no_distance_stack = _remove_constraints({"swampland_distance_conjecture"})
    tower_reference_stack = _remove_constraints(
        {"swampland_distance_conjecture", "species_scale_bound"}
    )

    candidates = {}
    sweeps = {}
    for mode in TOWER_MODES:
        candidates[mode] = _candidate_result(
            mode,
            3.0,
            centroids,
            zero_points,
            tower_reference_stack,
            samples,
        )
        rows = [
            _candidate_result(
                mode,
                nmax,
                centroids,
                zero_points,
                tower_reference_stack,
                samples,
            )
            for nmax in nmax_sweep
        ]
        sweeps[mode] = {
            "rows": rows,
            "first_accepting_N_max": next(
                (
                    row["N_max"]
                    for row in rows
                    if row["accepted_basic_surrogate_gate"]
                ),
                None,
            ),
        }

    return {
        "input": str(phases_path),
        "basis": KEYS,
        "samples_per_segment": samples,
        "N_max_sweep": nmax_sweep,
        "literature_guardrail": {
            "claim": (
                "Species/tower surrogates are closer to the Distance Conjecture "
                "than a coefficient max/min rule because they encode light-state "
                "counting and a lowered gravity cutoff. They still lack an explicit "
                "moduli-space metric and tower spectrum, so they are acceptance "
                "tests, not canonical SDC replacements."
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
                {
                    "title": "van de Heisteeg, Vafa, Wiesner, and Wu, Moduli-dependent Species Scale",
                    "url": "https://arxiv.org/abs/2212.06841",
                },
            ],
        },
        "baselines": {
            "default": _topology_diagnostic(
                centroids,
                zero_points,
                default_stack,
                samples=samples,
            ),
            "no_hard_distance_prior": _topology_diagnostic(
                centroids,
                zero_points,
                no_distance_stack,
                samples=samples,
            ),
            "no_distance_or_species_prior": _topology_diagnostic(
                centroids,
                zero_points,
                tower_reference_stack,
                samples=samples,
            ),
        },
        "candidates_at_N_max_3": candidates,
        "N_max_sweeps": sweeps,
        "interpretation": (
            "A candidate passes only a basic surrogate gate if it reconnects the "
            "parity lobes, adds no framework exclusions relative to the stack with "
            "the hard distance/species sector removed, and does not fail any known "
            "framework by itself. Passing this gate is necessary but not sufficient "
            "for a physical Distance Conjecture encoding."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="experiments/results/v2.13/phases_8d_1200.json")
    parser.add_argument("--out", default="experiments/results/v2.17/tower_surrogate_distance.json")
    parser.add_argument("--samples", type=int, default=101)
    parser.add_argument(
        "--nmax-values",
        default=",".join(str(value) for value in DEFAULT_NMAX_VALUES),
        help="comma-separated N_max values for tower-surrogate calibration",
    )
    args = parser.parse_args()

    result = diagnose_tower_surrogates(
        args.input,
        samples=args.samples,
        nmax_values=_parse_float_list(args.nmax_values),
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
