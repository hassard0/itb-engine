"""Theory-path distance: shortest path between two theories that stays inside
the allowed region.

Implementation: discretize the parameter region into a grid, mark each cell as
feasible/infeasible, and BFS from the start cell to the end cell on the
feasibility graph (4-connected). The path length is reported in axis units.

If start and end are in disconnected feasibility components, the result has
`connected = False` and `distance = inf`. This is the diagnostic for Idea #C —
disconnected allowed components mean genuinely different phases of theory."""

from collections import deque
from dataclasses import dataclass
import math

import numpy as np

from itb.constraints.base import Constraint
from itb.engine import check
from itb.theory import Theory


@dataclass
class PathResult:
    connected: bool
    distance: float
    path_points: list[tuple[float, float]]
    path_indices: list[tuple[int, int]]


def _nearest_index(values: np.ndarray, target: float) -> int:
    return int(np.argmin(np.abs(values - target)))


def path_through_allowed_region(
    start: dict[str, float],
    end: dict[str, float],
    x_param: str,
    x_range: tuple[float, float],
    x_steps: int,
    y_param: str,
    y_range: tuple[float, float],
    y_steps: int,
    constraints: list[Constraint],
    fixed_coefficients: dict[str, float] | None = None,
) -> PathResult:
    fixed = dict(fixed_coefficients or {})
    x_values = np.linspace(x_range[0], x_range[1], x_steps)
    y_values = np.linspace(y_range[0], y_range[1], y_steps)
    feasibility = np.zeros((x_steps, y_steps), dtype=bool)
    for i, x in enumerate(x_values):
        for j, y in enumerate(y_values):
            coefficients = dict(fixed)
            coefficients[x_param] = float(x)
            coefficients[y_param] = float(y)
            feasibility[i, j] = check(
                Theory(coefficients=coefficients), constraints
            ).feasible

    si = _nearest_index(x_values, start[x_param])
    sj = _nearest_index(y_values, start[y_param])
    ei = _nearest_index(x_values, end[x_param])
    ej = _nearest_index(y_values, end[y_param])

    if not feasibility[si, sj] or not feasibility[ei, ej]:
        return PathResult(
            connected=False,
            distance=float("inf"),
            path_points=[],
            path_indices=[],
        )

    parent: dict[tuple[int, int], tuple[int, int] | None] = {(si, sj): None}
    queue: deque[tuple[int, int]] = deque([(si, sj)])
    found = False
    while queue:
        i, j = queue.popleft()
        if (i, j) == (ei, ej):
            found = True
            break
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nj = i + di, j + dj
            if (
                0 <= ni < x_steps
                and 0 <= nj < y_steps
                and feasibility[ni, nj]
                and (ni, nj) not in parent
            ):
                parent[(ni, nj)] = (i, j)
                queue.append((ni, nj))

    if not found:
        return PathResult(
            connected=False,
            distance=float("inf"),
            path_points=[],
            path_indices=[],
        )

    indices: list[tuple[int, int]] = []
    cur: tuple[int, int] | None = (ei, ej)
    while cur is not None:
        indices.append(cur)
        cur = parent[cur]
    indices.reverse()
    points = [(float(x_values[i]), float(y_values[j])) for i, j in indices]
    distance = 0.0
    for (xa, ya), (xb, yb) in zip(points, points[1:]):
        distance += math.hypot(xb - xa, yb - ya)
    return PathResult(
        connected=True,
        distance=distance,
        path_points=points,
        path_indices=indices,
    )
