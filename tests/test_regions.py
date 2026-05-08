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
