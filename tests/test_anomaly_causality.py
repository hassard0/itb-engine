import pytest

from itb.constraints.anomaly import AnomalyCancellation
from itb.constraints.base import ConstraintClass
from itb.constraints.causality import CausalityBound
from itb.theory import Theory


def test_anomaly_satisfied_on_surface():
    c = AnomalyCancellation(c_anom=1.0, tolerance=0.05)
    # Pick g_4 g_6 = g_R2^2: e.g. g_4 = 1, g_6 = 0.25, g_R2 = 0.5
    r = c.evaluate(Theory(coefficients={"g_4": 1.0, "g_6": 0.25, "g_R2": 0.5}))
    assert r.satisfied is True


def test_anomaly_violated_far_from_surface():
    c = AnomalyCancellation(c_anom=1.0, tolerance=0.05)
    r = c.evaluate(Theory(coefficients={"g_4": 1.0, "g_6": 1.0, "g_R2": 0.0}))
    # residual = 1.0; |1.0| > 0.05 so violated
    assert r.satisfied is False


def test_anomaly_class_c():
    assert AnomalyCancellation().constraint_class is ConstraintClass.C_UNIVERSALITY


def test_causality_satisfied_when_g_4_dominates():
    c = CausalityBound(gamma=1.0)
    r = c.evaluate(Theory(coefficients={"g_4": 1.0, "g_R2": 0.5}))
    assert r.satisfied is True
    assert r.margin == pytest.approx(0.5)


def test_causality_violated_when_g_R2_too_large():
    c = CausalityBound(gamma=1.0)
    r = c.evaluate(Theory(coefficients={"g_4": 0.2, "g_R2": 0.9}))
    assert r.satisfied is False


def test_causality_class_a():
    assert CausalityBound().constraint_class is ConstraintClass.A_AMPLITUDE


def test_string_eft_violates_anomaly_with_default_tolerance():
    """String tree EFT (g_4=0.5, g_6=0.4, g_R2=0.2) has residual = 0.5*0.4 - 1.0*0.04
    = 0.16, which exceeds default tolerance 0.15. So string-EFT is *just barely*
    excluded by anomaly cancellation as encoded — a real (toy) physics result."""
    from itb.engine import check
    from itb.frameworks.string_tree_eft import StringTreeEFT
    theory = StringTreeEFT().encode()
    report = check(theory, [AnomalyCancellation(c_anom=1.0, tolerance=0.15)])
    # residual = 0.16; |0.16| > 0.15 so excluded
    assert report.feasible is False


def test_lqg_induced_passes_causality():
    from itb.engine import check
    from itb.frameworks.lqg_induced import LQGInduced
    theory = LQGInduced().encode()
    report = check(theory, [CausalityBound(gamma=1.0)])
    # g_4=0.6, g_R2=0.3 -> margin 0.3 > 0
    assert report.feasible is True
