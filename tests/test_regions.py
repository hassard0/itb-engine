import numpy as np
import pytest

from itb.regions import Region


def _grid(values):
    return np.array(values, dtype=bool)


def test_region_holds_grid_and_axes():
    r = Region(
        feasibility=_grid([[True, False], [True, True]]),
        axes={"g_4": np.array([0.0, 1.0]), "g_6": np.array([0.0, 1.0])},
        binding={},
    )
    assert r.feasibility.shape == (2, 2)
    assert "g_4" in r.axes


def test_intersection_logical_and():
    a = Region(_grid([[True, True], [False, True]]),
               {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])}, {})
    b = Region(_grid([[True, False], [True, True]]),
               {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])}, {})
    c = a & b
    np.testing.assert_array_equal(c.feasibility, [[True, False], [False, True]])


def test_union_logical_or():
    a = Region(_grid([[True, False], [False, False]]),
               {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])}, {})
    b = Region(_grid([[False, True], [True, False]]),
               {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])}, {})
    c = a | b
    np.testing.assert_array_equal(c.feasibility, [[True, True], [True, False]])


def test_difference_a_minus_b():
    a = Region(_grid([[True, True], [True, True]]),
               {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])}, {})
    b = Region(_grid([[True, False], [False, True]]),
               {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])}, {})
    c = a - b
    np.testing.assert_array_equal(c.feasibility, [[False, True], [True, False]])


def test_complement():
    a = Region(_grid([[True, False], [False, True]]),
               {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])}, {})
    np.testing.assert_array_equal((~a).feasibility,
                                  [[False, True], [True, False]])


def test_axes_must_match():
    a = Region(_grid([[True]]), {"x": np.array([0.0]), "y": np.array([0.0])}, {})
    b = Region(_grid([[True]]), {"x": np.array([1.0]), "y": np.array([0.0])}, {})
    with pytest.raises(ValueError):
        _ = a & b


def test_region_from_sweep_carries_binding():
    from itb.constraints.scalar_positivity import (
        ScalarPositivityG4,
        ScalarPositivityG6,
    )
    from itb.mapper import sweep_2d
    from itb.regions import region_from_sweep

    s = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=5,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    r = region_from_sweep(s)
    assert r.feasibility.shape == (5, 5)
    assert r.binding.get("grid") is not None
    assert r.binding.get("class_grid") is not None


def test_intersection_drops_binding():
    from itb.constraints.scalar_positivity import (
        ScalarPositivityG4,
        ScalarPositivityG6,
    )
    from itb.mapper import sweep_2d
    from itb.regions import region_from_sweep

    s1 = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=3,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=3,
        constraints=[ScalarPositivityG4()],
    )
    s2 = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=3,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=3,
        constraints=[ScalarPositivityG6()],
    )
    inter = region_from_sweep(s1) & region_from_sweep(s2)
    assert inter.binding == {}
