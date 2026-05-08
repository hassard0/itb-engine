"""Theory-space mapper: sweeps over a parameter grid and records both
feasibility and the most-binding constraint per cell. Also exposes
boundary detection — cells adjacent to a feasibility flip — and
Newton-style boundary tracing using constraint gradients."""

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
    binding_grid: np.ndarray
    binding_class_grid: np.ndarray


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
    feasibility = np.zeros((x_steps, y_steps), dtype=bool)
    binding = np.full((x_steps, y_steps), "", dtype=object)
    binding_class = np.full((x_steps, y_steps), "", dtype=object)
    for i, x in enumerate(x_values):
        for j, y in enumerate(y_values):
            coefficients = dict(fixed)
            coefficients[x_param] = float(x)
            coefficients[y_param] = float(y)
            theory = Theory(coefficients=coefficients, name="sweep_point")
            report = check(theory, constraints)
            feasibility[i, j] = report.feasible
            if report.binding is not None:
                binding[i, j] = report.binding
                binding_class[i, j] = report.binding_class or ""
    return SweepResult(
        x_param=x_param,
        x_values=x_values,
        y_param=y_param,
        y_values=y_values,
        feasibility_grid=feasibility,
        binding_grid=binding,
        binding_class_grid=binding_class,
    )


def boundary_cells(sweep: SweepResult) -> list[tuple[int, int]]:
    """Return (i, j) indices of cells that are adjacent to a feasibility flip."""
    g = sweep.feasibility_grid
    cells: list[tuple[int, int]] = []
    nx, ny = g.shape
    for i in range(nx):
        for j in range(ny):
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ni, nj = i + di, j + dj
                if 0 <= ni < nx and 0 <= nj < ny and g[i, j] != g[ni, nj]:
                    cells.append((i, j))
                    break
    return cells


def trace_boundary_along_axis(
    constraint,
    start: dict[str, float],
    max_iters: int = 50,
    tol: float = 1e-9,
) -> dict[str, float]:
    """Newton-style root-find along the constraint's gradient direction
    starting from `start`, walking to the constraint boundary (margin = 0).

    For a linear constraint with unit gradient the boundary is reached in
    one Newton step; for nonlinear constraints multiple iterations may be
    needed, hence max_iters.
    """
    point = dict(start)
    for _ in range(max_iters):
        theory = Theory(coefficients=dict(point))
        margin = constraint.evaluate(theory).margin
        if abs(margin) < tol:
            return point
        grad = constraint.gradient(theory)
        norm_sq = sum(v * v for v in grad.values())
        if norm_sq == 0.0:
            return point
        for k, gv in grad.items():
            point[k] = point.get(k, 0.0) - margin * gv / norm_sq
    return point
