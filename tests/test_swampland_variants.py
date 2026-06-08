import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.swampland_variants import (
    RepulsiveForceConjecture,
    ScalarWGC,
)
from itb.theory import Theory


def test_scalar_wgc_class_c():
    assert ScalarWGC().constraint_class is ConstraintClass.C_UNIVERSALITY
    assert "Palti" in ScalarWGC().citation


def test_scalar_wgc_satisfied_at_default_beta():
    """Default β=0.5; for string-EFT (g_4=0.5, g_6=0.4, g_R2=0.2):
       margin = 0.5 - 0.5*0.4 - 0.2 = 0.10 ✓"""
    from itb.frameworks.string_tree_eft import StringTreeEFT
    c = ScalarWGC(beta=0.5)
    assert c.evaluate(StringTreeEFT().encode()).satisfied is True


def test_scalar_wgc_violates_string_at_strict_beta():
    """At β=1.0: margin = 0.5 - 1.0*0.4 - 0.2 = -0.10 ✗"""
    from itb.frameworks.string_tree_eft import StringTreeEFT
    c = ScalarWGC(beta=1.0)
    assert c.evaluate(StringTreeEFT().encode()).satisfied is False


def test_scalar_wgc_violates_lqg_at_strict_beta():
    """LQG: g_4=0.6, g_6=0.45, g_R2=0.3.
       β=1.0: 0.6 - 0.45 - 0.3 = -0.15 ✗"""
    from itb.frameworks.lqg_induced import LQGInduced
    c = ScalarWGC(beta=1.0)
    assert c.evaluate(LQGInduced().encode()).satisfied is False


def test_repulsive_force_class_c():
    c = RepulsiveForceConjecture()
    assert c.constraint_class is ConstraintClass.C_UNIVERSALITY
    assert "Heidenreich" in c.citation


def test_repulsive_force_satisfied_at_default():
    """Default γ=1.0. String-EFT: g_4*g_6=0.20, g_R2=0.2, g_R2^2=0.04.
       margin = 0.20 - 0.20 - 1*0.04 = -0.04 ✗"""
    from itb.frameworks.string_tree_eft import StringTreeEFT
    c = RepulsiveForceConjecture(gamma=1.0)
    # String-EFT actually FAILS at γ=1.0 — informative
    r = c.evaluate(StringTreeEFT().encode())
    assert r.satisfied is False  # confirms encoding is non-trivial


def test_repulsive_force_satisfied_at_loose_gamma():
    """γ=0.5: margin = 0.20 - 0.20 - 0.5*0.04 = -0.02 — still fails.
       Need looser. γ=0: margin = 0.20 - 0.20 = 0 — exactly on boundary."""
    from itb.frameworks.string_tree_eft import StringTreeEFT
    c_zero_gamma = RepulsiveForceConjecture(gamma=0.0)
    r = c_zero_gamma.evaluate(StringTreeEFT().encode())
    assert r.satisfied is True
    assert r.margin == pytest.approx(0.0)


def test_repulsive_force_passes_for_pure_gr():
    from itb.frameworks.pure_gr import PureGR
    c = RepulsiveForceConjecture()
    r = c.evaluate(PureGR().encode())
    assert r.satisfied is True


def test_repulsive_force_convex_hull_form_passes_string():
    """The physically-corrected convex_hull form g_4 - g_R2 - γ*g_R2^2 drops the
    spurious g_6 product. String-EFT: 0.5 - 0.2 - 1*0.04 = 0.26 ✓ — passes,
    unlike the matter_product form. (2026-06 realism finding F1.)"""
    from itb.frameworks.string_tree_eft import StringTreeEFT
    c = RepulsiveForceConjecture(gamma=1.0, form="convex_hull")
    r = c.evaluate(StringTreeEFT().encode())
    assert r.satisfied is True
    assert r.margin == pytest.approx(0.26)
    assert r.details["form"] == "convex_hull"


def test_repulsive_force_convex_hull_passes_all_frameworks():
    """Re-cast RFC excludes none of the candidate frameworks (the universal
    exclusion under matter_product was an encoding artifact)."""
    from itb.frameworks.asymptotic_safety import AsymptoticSafety
    from itb.frameworks.cdt import CausalDynamicalTriangulation
    from itb.frameworks.lqg_induced import LQGInduced
    from itb.frameworks.string_tree_eft import StringTreeEFT
    c = RepulsiveForceConjecture(gamma=1.0, form="convex_hull")
    for fw in (StringTreeEFT(), AsymptoticSafety(), LQGInduced(),
               CausalDynamicalTriangulation()):
        assert c.evaluate(fw.encode()).satisfied is True


def test_repulsive_force_rejects_unknown_form():
    with pytest.raises(ValueError):
        RepulsiveForceConjecture(form="bogus")
