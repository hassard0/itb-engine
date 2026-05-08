import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.eft_validity import EFTValidityBox
from itb.theory import Theory


def test_metadata_class_c():
    c = EFTValidityBox()
    assert c.constraint_class is ConstraintClass.C_UNIVERSALITY
    assert "EFT validity" in c.citation or "cutoff" in c.citation.lower()


def test_satisfied_when_coefficients_within_default_box():
    c = EFTValidityBox()
    r = c.evaluate(Theory(coefficients={"g_4": 0.5, "g_6": 0.5, "g_R2": 0.5}))
    assert r.satisfied is True


def test_violated_when_g_4_exceeds_box():
    c = EFTValidityBox(box=2.0)
    r = c.evaluate(Theory(coefficients={"g_4": 5.0, "g_6": 0.0, "g_R2": 0.0}))
    assert r.satisfied is False
    assert r.margin < 0


def test_violated_when_g_6_exceeds_box():
    c = EFTValidityBox(box=2.0)
    r = c.evaluate(Theory(coefficients={"g_4": 0.0, "g_6": 5.0, "g_R2": 0.0}))
    assert r.satisfied is False


def test_violated_when_g_R2_exceeds_box():
    c = EFTValidityBox(box=2.0)
    r = c.evaluate(Theory(coefficients={"g_4": 0.0, "g_6": 0.0, "g_R2": 5.0}))
    assert r.satisfied is False


def test_completeness_check_now_reports_bounded():
    """With EFT validity box added, the constraint set should produce a
    bounded allowed region — fixing the gap that v0.4 identified."""
    from itb.completeness import check_boundedness
    from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
    from itb.constraints.scalar_positivity import (
        ScalarPositivityG4,
        ScalarPositivityG6,
    )

    constraints = [
        ScalarPositivityG4(),
        ScalarPositivityG6(),
        ScalarConvexityG6vsG4(),
        EFTValidityBox(box=2.0),
    ]
    report = check_boundedness(
        constraints=constraints,
        params=["g_4", "g_6"],
        starting_box=2.0,
        max_box=8.0,
        steps_per_axis=11,
    )
    assert report.bounded is True
