import math

import pytest

from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.path_distance import path_through_allowed_region, PathResult


def _three_constraints():
    return [ScalarPositivityG4(), ScalarPositivityG6(), ScalarConvexityG6vsG4()]


def test_short_path_within_allowed_region():
    res = path_through_allowed_region(
        start={"g_4": 0.2, "g_6": 0.5},
        end={"g_4": 0.4, "g_6": 0.6},
        x_param="g_4", x_range=(0.0, 1.0), x_steps=21,
        y_param="g_6", y_range=(0.0, 1.0), y_steps=21,
        constraints=_three_constraints(),
    )
    assert isinstance(res, PathResult)
    assert res.connected is True
    # Path length is roughly Euclidean distance plus grid discretization
    direct = math.hypot(0.2, 0.1)
    assert res.distance > 0
    assert res.distance < 3 * direct  # generous bound


def test_disconnected_when_endpoint_infeasible():
    res = path_through_allowed_region(
        start={"g_4": 0.5, "g_6": 0.5},
        end={"g_4": -0.5, "g_6": -0.5},     # infeasible
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=21,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=21,
        constraints=_three_constraints(),
    )
    assert res.connected is False


def test_disconnected_when_start_infeasible():
    res = path_through_allowed_region(
        start={"g_4": -0.5, "g_6": -0.5},
        end={"g_4": 0.5, "g_6": 0.5},
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=21,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=21,
        constraints=_three_constraints(),
    )
    assert res.connected is False


def test_path_cells_lie_in_allowed_region():
    from itb.engine import check
    from itb.theory import Theory
    res = path_through_allowed_region(
        start={"g_4": 0.2, "g_6": 0.5},
        end={"g_4": 0.7, "g_6": 0.9},
        x_param="g_4", x_range=(0.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(0.0, 1.0), y_steps=11,
        constraints=_three_constraints(),
    )
    assert res.connected is True
    for x, y in res.path_points:
        theory = Theory(coefficients={"g_4": x, "g_6": y})
        assert check(theory, _three_constraints()).feasible is True
