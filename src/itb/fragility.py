"""Fragility mapping: apply the smallest-violating-perturbation analysis
across a 2D parameter sweep, producing a heatmap that answers "how robust
is each allowed point, and which constraint is closest to ruling it out?"

For excluded points the distance is zero (already violating). For allowed
points the distance is the Euclidean perturbation that would push the
nearest constraint to its boundary. The most-fragile constraint name is
recorded per cell.
"""

from dataclasses import dataclass

import numpy as np

from itb.constraints.base import Constraint
from itb.perturbation import smallest_violating_perturbation
from itb.theory import Theory


@dataclass
class FragilityMap:
    x_param: str
    x_values: np.ndarray
    y_param: str
    y_values: np.ndarray
    distance_grid: np.ndarray         # float: distance to nearest violation
    most_fragile_grid: np.ndarray     # str: name of nearest constraint


def fragility_map_2d(
    x_param: str,
    x_range: tuple[float, float],
    x_steps: int,
    y_param: str,
    y_range: tuple[float, float],
    y_steps: int,
    constraints: list[Constraint],
    fixed_coefficients: dict[str, float] | None = None,
) -> FragilityMap:
    fixed = dict(fixed_coefficients or {})
    x_values = np.linspace(x_range[0], x_range[1], x_steps)
    y_values = np.linspace(y_range[0], y_range[1], y_steps)
    distances = np.zeros((x_steps, y_steps), dtype=float)
    fragile = np.full((x_steps, y_steps), "", dtype=object)
    for i, x in enumerate(x_values):
        for j, y in enumerate(y_values):
            coefficients = dict(fixed)
            coefficients[x_param] = float(x)
            coefficients[y_param] = float(y)
            theory = Theory(coefficients=coefficients, name="fragility_point")
            res = smallest_violating_perturbation(theory, constraints)
            distances[i, j] = res.distance
            fragile[i, j] = res.binding_constraint
    return FragilityMap(
        x_param=x_param,
        x_values=x_values,
        y_param=y_param,
        y_values=y_values,
        distance_grid=distances,
        most_fragile_grid=fragile,
    )
