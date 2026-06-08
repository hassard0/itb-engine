"""Tests for forward-limit graviton dispersion positivity (g_R2 >= c*g_R3)."""

import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.graviton_forward_positivity import GravitonForwardPositivity
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.theory import Theory


def test_class_and_citation():
    c = GravitonForwardPositivity()
    assert c.constraint_class is ConstraintClass.A_AMPLITUDE
    assert "Caron-Huot" in c.citation


def test_canonical_excludes_only_lqg():
    """At canonical c=1.2 the leading-dominates-cubic bound fails LQG
    (g_R2=0.3, g_R3=0.30 -> margin -0.06) but passes string/AS/CDT."""
    c = GravitonForwardPositivity(c=1.2)
    assert c.evaluate(LQGInduced().encode()).satisfied is False
    assert c.evaluate(LQGInduced().encode()).margin == pytest.approx(-0.06)
    for fw in (StringTreeEFT(), AsymptoticSafety(), CausalDynamicalTriangulation()):
        assert c.evaluate(fw.encode()).satisfied is True


def test_asymptotic_safety_is_most_robust():
    """AS keeps the largest g_R2/g_R3 ratio (1.5), so it survives to the
    highest c; LQG (ratio 1.0) fails first."""
    as_ratio = 0.15 / 0.10
    lqg_ratio = 0.30 / 0.30
    assert as_ratio > lqg_ratio
    # AS still feasible at c just below its ratio; LQG already infeasible there
    c = GravitonForwardPositivity(c=1.4)
    assert c.evaluate(AsymptoticSafety().encode()).satisfied is True
    assert c.evaluate(LQGInduced().encode()).satisfied is False


def test_boundary_at_c_equals_ratio():
    """LQG sits exactly on the boundary at c=1.0 (g_R2 = g_R3)."""
    c = GravitonForwardPositivity(c=1.0)
    r = c.evaluate(LQGInduced().encode())
    assert r.margin == pytest.approx(0.0)
    assert r.satisfied is True


def test_gradient():
    c = GravitonForwardPositivity(c=1.2)
    g = c.gradient(Theory(coefficients={"g_R2": 0.2, "g_R3": 0.15}))
    assert g["g_R2"] == pytest.approx(1.0)
    assert g["g_R3"] == pytest.approx(-1.2)
