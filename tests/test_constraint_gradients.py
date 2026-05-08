import numpy as np

from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.theory import Theory


def test_g4_gradient_unit_in_g4_direction():
    c = ScalarPositivityG4()
    g = c.gradient(Theory(coefficients={"g_4": 0.7, "g_6": 0.2}))
    assert set(g.keys()) == {"g_4", "g_6"}
    assert g["g_4"] == 1.0
    assert g["g_6"] == 0.0


def test_g6_gradient_unit_in_g6_direction():
    c = ScalarPositivityG6()
    g = c.gradient(Theory(coefficients={"g_4": 0.7, "g_6": 0.2}))
    assert g["g_4"] == 0.0
    assert g["g_6"] == 1.0


def test_signed_distance_margin_normalized():
    c = ScalarPositivityG4()
    r = c.evaluate(Theory(coefficients={"g_4": 0.5}))
    assert r.signed_distance_margin == 0.5


def test_signed_distance_negative_means_violation():
    c = ScalarPositivityG4()
    r = c.evaluate(Theory(coefficients={"g_4": -0.3}))
    assert r.signed_distance_margin == -0.3
    assert r.satisfied is False
