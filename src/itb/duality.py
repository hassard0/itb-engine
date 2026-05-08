"""Cross-class duality test (Theorize-doc Idea #8).

Question: do amplitude-bootstrap (class A) and information-theoretic (class B)
constraints give the same allowed region in their overlap regime?

Compute the allowed regions under each class separately, then report the
Jaccard index (IoU) between them and decompose the symmetric difference into
"only-A allows" and "only-B allows" cells. If A and B coincide perfectly,
they are dual: either suffices. If they differ, the symmetric difference is
the *new information* the second class provides over the first.
"""

from dataclasses import dataclass

import numpy as np

from itb.constraints.base import Constraint, ConstraintClass
from itb.engine import check
from itb.theory import Theory


@dataclass
class DualityReport:
    iou: float                 # Jaccard index of A-allowed and B-allowed sets
    a_only_count: int          # cells allowed by A but not B
    b_only_count: int          # cells allowed by B but not A
    both_count: int
    a_grid: np.ndarray
    b_grid: np.ndarray
    x_values: np.ndarray
    y_values: np.ndarray


def cross_class_duality_2d(
    constraints: list[Constraint],
    x_param: str,
    x_range: tuple[float, float],
    x_steps: int,
    y_param: str,
    y_range: tuple[float, float],
    y_steps: int,
    fixed_coefficients: dict[str, float] | None = None,
) -> DualityReport:
    fixed = dict(fixed_coefficients or {})
    a_set = [c for c in constraints if c.constraint_class is ConstraintClass.A_AMPLITUDE]
    b_set = [c for c in constraints if c.constraint_class is ConstraintClass.B_INFORMATION]
    if not a_set or not b_set:
        raise ValueError("need at least one constraint of each class A and B")

    x_values = np.linspace(x_range[0], x_range[1], x_steps)
    y_values = np.linspace(y_range[0], y_range[1], y_steps)
    a_grid = np.zeros((x_steps, y_steps), dtype=bool)
    b_grid = np.zeros((x_steps, y_steps), dtype=bool)
    for i, x in enumerate(x_values):
        for j, y in enumerate(y_values):
            coefficients = dict(fixed)
            coefficients[x_param] = float(x)
            coefficients[y_param] = float(y)
            theory = Theory(coefficients=coefficients)
            a_grid[i, j] = check(theory, a_set).feasible
            b_grid[i, j] = check(theory, b_set).feasible

    intersection = (a_grid & b_grid).sum()
    union = (a_grid | b_grid).sum()
    iou = float(intersection / union) if union > 0 else 0.0
    return DualityReport(
        iou=iou,
        a_only_count=int(((a_grid) & (~b_grid)).sum()),
        b_only_count=int(((~a_grid) & (b_grid)).sum()),
        both_count=int(intersection),
        a_grid=a_grid,
        b_grid=b_grid,
        x_values=x_values,
        y_values=y_values,
    )
