import pytest

from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.perturbation import smallest_violating_perturbation
from itb.theory import Theory


def test_returns_zero_for_already_violating_theory():
    res = smallest_violating_perturbation(
        theory=Theory(coefficients={"g_4": -0.5, "g_6": 0.5}),
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    assert res.distance == 0.0


def test_returns_distance_to_g4_axis_for_pure_g4_violation_path():
    res = smallest_violating_perturbation(
        theory=Theory(coefficients={"g_4": 0.5, "g_6": 0.5}),
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    assert res.distance == pytest.approx(0.5, abs=1e-6)


def test_returns_binding_constraint_at_perturbed_point():
    res = smallest_violating_perturbation(
        theory=Theory(coefficients={"g_4": 0.7, "g_6": 0.2}),
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    assert res.binding_constraint == "scalar_positivity_g6"
    assert res.distance == pytest.approx(0.2, abs=1e-6)


def test_perturbed_point_is_on_constraint_boundary():
    res = smallest_violating_perturbation(
        theory=Theory(coefficients={"g_4": 0.5, "g_6": 0.5}),
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    if res.binding_constraint == "scalar_positivity_g4":
        assert abs(res.perturbed_theory.coefficients["g_4"]) < 1e-6
    else:
        assert abs(res.perturbed_theory.coefficients["g_6"]) < 1e-6
