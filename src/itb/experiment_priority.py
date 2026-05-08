"""Experimental sensitivity ranking: which experiment, if run with its
forecast precision, would eliminate the most theory space?

Method: given a list of candidate measurements, each modeled as a
`MeasuredWilsonCoefficient` constraint with a forecast central value and
uncertainty, compute the count of allowed cells in a 2D sweep
(a) under the existing constraint set without the experiment, and
(b) under the existing constraint set with the experiment added.

The exclusion power of the experiment is the difference: how many cells
become forbidden when this experiment is included. Larger = more
informative = experimentally higher priority.

This is the engine's first directly research-actionable output: a ranked
list telling physicists which experiment, if it produces a null result,
would carve out the largest region of currently-allowed theory space."""

from dataclasses import dataclass

import numpy as np

from itb.constraints.base import Constraint
from itb.constraints.experimental import MeasuredWilsonCoefficient
from itb.engine import check
from itb.theory import Theory


@dataclass
class ExperimentForecast:
    label: str
    coefficient_name: str
    central_value: float
    sigma: float
    sigma_threshold: float = 2.0


@dataclass
class ExperimentRanking:
    label: str
    coefficient_name: str
    cells_excluded: int
    fraction_excluded: float
    baseline_allowed: int


def _count_allowed(
    x_param: str, x_values: np.ndarray,
    y_param: str, y_values: np.ndarray,
    constraints: list[Constraint],
    fixed: dict[str, float],
) -> int:
    n = 0
    for x in x_values:
        for y in y_values:
            coefficients = dict(fixed)
            coefficients[x_param] = float(x)
            coefficients[y_param] = float(y)
            theory = Theory(coefficients=coefficients)
            if check(theory, constraints).feasible:
                n += 1
    return n


def rank_experiments(
    base_constraints: list[Constraint],
    experiments: list[ExperimentForecast],
    x_param: str,
    x_range: tuple[float, float],
    x_steps: int,
    y_param: str,
    y_range: tuple[float, float],
    y_steps: int,
    fixed_coefficients: dict[str, float] | None = None,
) -> list[ExperimentRanking]:
    fixed = dict(fixed_coefficients or {})
    x_values = np.linspace(x_range[0], x_range[1], x_steps)
    y_values = np.linspace(y_range[0], y_range[1], y_steps)
    baseline = _count_allowed(
        x_param, x_values, y_param, y_values, base_constraints, fixed
    )
    rankings: list[ExperimentRanking] = []
    for exp in experiments:
        exp_constraint = MeasuredWilsonCoefficient(
            coefficient_name=exp.coefficient_name,
            central_value=exp.central_value,
            sigma=exp.sigma,
            sigma_threshold=exp.sigma_threshold,
            experiment_label=exp.label,
        )
        with_exp = base_constraints + [exp_constraint]
        n_with = _count_allowed(
            x_param, x_values, y_param, y_values, with_exp, fixed
        )
        excluded = max(baseline - n_with, 0)
        frac = (excluded / baseline) if baseline > 0 else 0.0
        rankings.append(ExperimentRanking(
            label=exp.label,
            coefficient_name=exp.coefficient_name,
            cells_excluded=excluded,
            fraction_excluded=frac,
            baseline_allowed=baseline,
        ))
    rankings.sort(key=lambda r: -r.cells_excluded)
    return rankings


def render_priority_list(rankings: list[ExperimentRanking]) -> str:
    lines: list[str] = []
    lines.append("# Experimental priority ranking")
    lines.append("")
    if rankings:
        lines.append(f"Baseline allowed cells (without any experiment): {rankings[0].baseline_allowed}")
        lines.append("")
    lines.append("| rank | experiment | observable | cells excluded | fraction excluded |")
    lines.append("|---|---|---|---|---|")
    for i, r in enumerate(rankings, 1):
        lines.append(
            f"| {i} | {r.label} | {r.coefficient_name} | "
            f"{r.cells_excluded} | {100 * r.fraction_excluded:.1f}% |"
        )
    return "\n".join(lines)
