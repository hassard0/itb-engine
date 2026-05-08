from itb.constraints.scalar_positivity import ScalarPositivityG4
from itb.engine import check
from itb.theory import Theory


def test_default_tolerance_treats_exact_zero_as_feasible():
    r = check(Theory(coefficients={"g_4": 0.0}), [ScalarPositivityG4()])
    assert r.feasible is True


def test_strict_tolerance_treats_tiny_negative_as_infeasible():
    r = check(
        Theory(coefficients={"g_4": -1e-12}),
        [ScalarPositivityG4()],
        tolerance=0.0,
    )
    assert r.feasible is False


def test_loose_tolerance_treats_small_negative_as_feasible():
    r = check(
        Theory(coefficients={"g_4": -1e-3}),
        [ScalarPositivityG4()],
        tolerance=1e-2,
    )
    assert r.feasible is True


def test_tolerance_recorded_in_report():
    r = check(
        Theory(coefficients={"g_4": 0.5}),
        [ScalarPositivityG4()],
        tolerance=1e-4,
    )
    assert r.tolerance == 1e-4
