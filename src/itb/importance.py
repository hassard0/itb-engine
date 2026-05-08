"""Constraint-importance ranking (Idea #B from v0.2 learnings).

For each constraint, measure how much the allowed region grows when that
constraint is removed. The constraint with the largest growth is the one
doing the most work on the domain in question. The constraint with zero
growth is logically redundant given the others.

This is sensitivity analysis on the constraint set itself — a kind of
methodological introspection that tells us which physical principles are
actually constraining the theory space, and which are along for the ride."""

from dataclasses import dataclass

import numpy as np

from itb.constraints.base import Constraint
from itb.engine import check
from itb.theory import Theory


@dataclass
class ImportanceScore:
    constraint_name: str
    allowed_region_growth: int        # cells gained when this constraint is removed
    growth_fraction: float            # growth / baseline_allowed_count, or 0 if baseline 0


@dataclass
class ImportanceReport:
    baseline_allowed_count: int
    total_cells: int
    scores: list[ImportanceScore]


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


def constraint_importance(
    x_param: str,
    x_range: tuple[float, float],
    x_steps: int,
    y_param: str,
    y_range: tuple[float, float],
    y_steps: int,
    constraints: list[Constraint],
    fixed_coefficients: dict[str, float] | None = None,
) -> ImportanceReport:
    fixed = dict(fixed_coefficients or {})
    x_values = np.linspace(x_range[0], x_range[1], x_steps)
    y_values = np.linspace(y_range[0], y_range[1], y_steps)
    total = x_steps * y_steps
    baseline = _count_allowed(x_param, x_values, y_param, y_values, constraints, fixed)
    scores: list[ImportanceScore] = []
    for i, c in enumerate(constraints):
        without = constraints[:i] + constraints[i + 1:]
        without_count = _count_allowed(x_param, x_values, y_param, y_values, without, fixed)
        growth = max(without_count - baseline, 0)
        frac = (growth / baseline) if baseline > 0 else 0.0
        scores.append(ImportanceScore(
            constraint_name=c.name,
            allowed_region_growth=growth,
            growth_fraction=frac,
        ))
    scores.sort(key=lambda s: -s.allowed_region_growth)
    return ImportanceReport(
        baseline_allowed_count=baseline,
        total_cells=total,
        scores=scores,
    )
