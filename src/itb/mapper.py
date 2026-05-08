"""Theory-space mapper: sweep over a parameter grid and record feasibility.

Convention for grid indexing: feasibility_grid[i, j] corresponds to
x_values[i], y_values[j]. (Row-major over x, column-major over y.)
"""

from dataclasses import dataclass

import numpy as np

from itb.constraints.base import Constraint
from itb.engine import check
from itb.theory import Theory


@dataclass
class SweepResult:
    x_param: str
    x_values: np.ndarray
    y_param: str
    y_values: np.ndarray
    feasibility_grid: np.ndarray


def sweep_2d(
    x_param: str,
    x_range: tuple[float, float],
    x_steps: int,
    y_param: str,
    y_range: tuple[float, float],
    y_steps: int,
    constraints: list[Constraint],
    fixed_coefficients: dict[str, float] | None = None,
) -> SweepResult:
    fixed = dict(fixed_coefficients or {})
    x_values = np.linspace(x_range[0], x_range[1], x_steps)
    y_values = np.linspace(y_range[0], y_range[1], y_steps)
    grid = np.zeros((x_steps, y_steps), dtype=bool)
    for i, x in enumerate(x_values):
        for j, y in enumerate(y_values):
            coefficients = dict(fixed)
            coefficients[x_param] = float(x)
            coefficients[y_param] = float(y)
            theory = Theory(coefficients=coefficients, name="sweep_point")
            grid[i, j] = check(theory, constraints).feasible
    return SweepResult(
        x_param=x_param,
        x_values=x_values,
        y_param=y_param,
        y_values=y_values,
        feasibility_grid=grid,
    )
