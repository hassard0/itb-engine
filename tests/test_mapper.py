import numpy as np

from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.mapper import sweep_2d, SweepResult


def test_sweep_returns_result():
    result = sweep_2d(
        x_param="g_4",
        x_range=(-1.0, 1.0),
        x_steps=5,
        y_param="g_6",
        y_range=(-1.0, 1.0),
        y_steps=5,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    assert isinstance(result, SweepResult)


def test_sweep_grid_shape():
    result = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=5,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    assert result.feasibility_grid.shape == (5, 5)


def test_sweep_first_quadrant_allowed():
    result = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=11,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    assert bool(result.feasibility_grid[8, 8]) is True


def test_sweep_third_quadrant_disallowed():
    result = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=11,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    assert bool(result.feasibility_grid[2, 2]) is False


def test_sweep_axes_recorded():
    result = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=5,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    np.testing.assert_allclose(result.x_values, np.linspace(-1.0, 1.0, 5))
    np.testing.assert_allclose(result.y_values, np.linspace(-1.0, 1.0, 5))
    assert result.x_param == "g_4"
    assert result.y_param == "g_6"
