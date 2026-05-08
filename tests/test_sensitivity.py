import numpy as np

from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.sensitivity import (
    feasibility_probability,
    sensitivity_grid_2d,
    SensitivityResult,
)


def _three():
    return [ScalarPositivityG4(), ScalarPositivityG6(), ScalarConvexityG6vsG4()]


def test_returns_result():
    res = feasibility_probability(
        nominal={"g_4": 0.5, "g_6": 0.6},
        constraints=_three(),
        sigma=0.05,
        n_samples=50,
    )
    assert isinstance(res, SensitivityResult)


def test_high_probability_far_inside():
    res = feasibility_probability(
        nominal={"g_4": 0.7, "g_6": 0.9},  # well inside the wedge
        constraints=_three(),
        sigma=0.02,
        n_samples=200,
    )
    assert res.p_feasible > 0.9


def test_zero_probability_far_outside():
    res = feasibility_probability(
        nominal={"g_4": -1.0, "g_6": -1.0},
        constraints=_three(),
        sigma=0.05,
        n_samples=100,
    )
    assert res.p_feasible == 0.0


def test_intermediate_probability_near_boundary():
    res = feasibility_probability(
        nominal={"g_4": 0.5, "g_6": 0.26},  # just above g_4^2 = 0.25
        constraints=_three(),
        sigma=0.05,
        n_samples=400,
    )
    # half of the Gaussian samples cross the boundary g_6 = g_4^2
    assert 0.1 < res.p_feasible < 0.95


def test_grid_returns_array_with_correct_shape():
    res = sensitivity_grid_2d(
        x_param="g_4", x_range=(0.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(0.0, 1.0), y_steps=5,
        constraints=_three(),
        sigma=0.05, n_samples=20,
    )
    assert res["p_grid"].shape == (5, 5)
    assert (res["p_grid"] >= 0.0).all()
    assert (res["p_grid"] <= 1.0).all()
