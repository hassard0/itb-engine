"""Tests for matter-sector s^3 forward-moment positivity (g_4 >= c_m*g_6)."""

import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.matter_s3_positivity import MatterS3Positivity
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.theory import Theory


def test_class_and_citation():
    c = MatterS3Positivity()
    assert c.constraint_class is ConstraintClass.A_AMPLITUDE
    assert "Caron-Huot" in c.citation


def test_nonbinding_at_canonical():
    """At c_m=1.0 every candidate passes (g_4/g_6 ratios 1.25-1.38) —
    an informative null, as expected for a Class-A matter constraint."""
    c = MatterS3Positivity(c_m=1.0)
    for fw in (StringTreeEFT(), AsymptoticSafety(), LQGInduced(),
               CausalDynamicalTriangulation()):
        assert c.evaluate(fw.encode()).satisfied is True


def test_binds_string_first_at_high_cm():
    """String has the smallest g_4/g_6 ratio (1.25), so it binds first."""
    c = MatterS3Positivity(c_m=1.3)
    assert c.evaluate(StringTreeEFT().encode()).satisfied is False
    assert c.evaluate(CausalDynamicalTriangulation().encode()).satisfied is True


def test_margin_and_gradient():
    c = MatterS3Positivity(c_m=1.0)
    t = Theory(coefficients={"g_4": 0.5, "g_6": 0.4})
    r = c.evaluate(t)
    assert r.margin == pytest.approx(0.1)
    g = c.gradient(t)
    assert g["g_4"] == pytest.approx(1.0)
    assert g["g_6"] == pytest.approx(-1.0)
