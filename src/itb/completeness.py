"""Completeness check (Idea #E): is the allowed region bounded?

Iteratively expand the box around the parameter region of interest. If allowed
points appear on the outer face of the box at every scale we test, the region
is unbounded in that direction — meaning the constraint set is incomplete and
we need additional constraints (UV cutoffs, hierarchy bounds, etc.) to close it.

For our toy with positivity bounds plus convexity, the allowed region is the
parabolic wedge above g_6 = g_4^2 in the first quadrant. It is unbounded (g_4
and g_6 can grow arbitrarily). This is correct for purely IR positivity bounds —
adding upper bounds requires UV physics input."""

from dataclasses import dataclass

import numpy as np

from itb.constraints.base import Constraint
from itb.engine import check
from itb.theory import Theory


@dataclass
class BoundednessReport:
    bounded: bool
    final_box_size: float
    unbounded_directions: list[str]
    fraction_allowed_at_final_box: float


def _allowed_on_outer_face(
    box_size: float,
    params: list[str],
    constraints: list[Constraint],
    steps_per_axis: int,
    fixed_coefficients: dict[str, float],
) -> dict[str, bool]:
    """For each param, check whether any allowed point exists on the outer
    face (positive direction) of the box. This signals unboundedness."""
    out: dict[str, bool] = {}
    if len(params) != 2:
        # Only 2D supported in v0.4
        for p in params:
            out[p] = False
        return out

    p0, p1 = params
    coords = np.linspace(-box_size, box_size, steps_per_axis)
    # Check the +box_size face for p0: vary p1 across the face
    found_face_p0 = False
    for v in coords:
        coefficients = dict(fixed_coefficients)
        coefficients[p0] = box_size
        coefficients[p1] = float(v)
        if check(Theory(coefficients=coefficients), constraints).feasible:
            found_face_p0 = True
            break
    out[p0] = found_face_p0

    found_face_p1 = False
    for v in coords:
        coefficients = dict(fixed_coefficients)
        coefficients[p0] = float(v)
        coefficients[p1] = box_size
        if check(Theory(coefficients=coefficients), constraints).feasible:
            found_face_p1 = True
            break
    out[p1] = found_face_p1
    return out


def _fraction_allowed_in_box(
    box_size: float,
    params: list[str],
    constraints: list[Constraint],
    steps_per_axis: int,
    fixed_coefficients: dict[str, float],
) -> float:
    if len(params) != 2:
        return 0.0
    p0, p1 = params
    coords = np.linspace(-box_size, box_size, steps_per_axis)
    n_total = 0
    n_feasible = 0
    for x in coords:
        for y in coords:
            coefficients = dict(fixed_coefficients)
            coefficients[p0] = float(x)
            coefficients[p1] = float(y)
            n_total += 1
            if check(Theory(coefficients=coefficients), constraints).feasible:
                n_feasible += 1
    return (n_feasible / n_total) if n_total else 0.0


def check_boundedness(
    constraints: list[Constraint],
    params: list[str],
    starting_box: float = 2.0,
    max_box: float = 8.0,
    box_growth: float = 2.0,
    steps_per_axis: int = 11,
    fixed_coefficients: dict[str, float] | None = None,
) -> BoundednessReport:
    """Expand the box geometrically; if the outer face still contains allowed
    points at the largest box, declare the region unbounded in that direction."""
    fixed = dict(fixed_coefficients or {})
    box = starting_box
    last_face_check: dict[str, bool] = {}
    while box <= max_box:
        last_face_check = _allowed_on_outer_face(
            box, params, constraints, steps_per_axis, fixed,
        )
        if not any(last_face_check.values()):
            # No allowed points on any outer face at this scale — bounded.
            return BoundednessReport(
                bounded=True,
                final_box_size=box,
                unbounded_directions=[],
                fraction_allowed_at_final_box=_fraction_allowed_in_box(
                    box, params, constraints, steps_per_axis, fixed,
                ),
            )
        if box >= max_box:
            break
        box = min(box * box_growth, max_box)
    unbounded_dirs = [p for p, found in last_face_check.items() if found]
    return BoundednessReport(
        bounded=False,
        final_box_size=box,
        unbounded_directions=unbounded_dirs,
        fraction_allowed_at_final_box=_fraction_allowed_in_box(
            box, params, constraints, steps_per_axis, fixed,
        ),
    )
