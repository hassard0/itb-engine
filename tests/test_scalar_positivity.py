from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.constraints.base import ConstraintClass
from itb.theory import Theory


def test_g4_positive_satisfied():
    c = ScalarPositivityG4()
    result = c.evaluate(Theory(coefficients={"g_4": 0.5}))
    assert result.satisfied is True
    assert result.margin == 0.5


def test_g4_negative_violated():
    c = ScalarPositivityG4()
    result = c.evaluate(Theory(coefficients={"g_4": -0.1}))
    assert result.satisfied is False
    assert result.margin == -0.1


def test_g4_zero_at_boundary():
    c = ScalarPositivityG4()
    result = c.evaluate(Theory(coefficients={"g_4": 0.0}))
    assert result.satisfied is True
    assert result.margin == 0.0


def test_g4_missing_coefficient_defaults_to_zero():
    c = ScalarPositivityG4()
    result = c.evaluate(Theory(coefficients={}))
    assert result.satisfied is True


def test_g6_positive_satisfied():
    c = ScalarPositivityG6()
    result = c.evaluate(Theory(coefficients={"g_6": 0.2}))
    assert result.satisfied is True
    assert result.margin == 0.2


def test_g6_negative_violated():
    c = ScalarPositivityG6()
    result = c.evaluate(Theory(coefficients={"g_6": -0.5}))
    assert result.satisfied is False
    assert result.margin == -0.5


def test_metadata_correctly_set():
    c = ScalarPositivityG4()
    assert c.name == "scalar_positivity_g4"
    assert "Adams" in c.citation
    assert c.constraint_class is ConstraintClass.A_AMPLITUDE
