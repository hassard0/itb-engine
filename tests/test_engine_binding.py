from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.engine import check
from itb.theory import Theory


def test_binding_is_none_when_feasible():
    r = check(Theory(coefficients={"g_4": 0.5, "g_6": 0.5}),
              [ScalarPositivityG4(), ScalarPositivityG6()])
    assert r.feasible is True
    assert r.binding is None


def test_binding_is_first_violation():
    r = check(Theory(coefficients={"g_4": -1.0, "g_6": 0.5}),
              [ScalarPositivityG4(), ScalarPositivityG6()])
    assert r.feasible is False
    assert r.binding == "scalar_positivity_g4"


def test_binding_when_both_violated_picks_most_negative():
    r = check(Theory(coefficients={"g_4": -0.1, "g_6": -1.0}),
              [ScalarPositivityG4(), ScalarPositivityG6()])
    assert r.feasible is False
    assert r.binding == "scalar_positivity_g6"


def test_binding_class_in_report():
    r = check(Theory(coefficients={"g_4": -1.0}),
              [ScalarPositivityG4()])
    assert r.binding_class == "amplitude_bootstrap"
