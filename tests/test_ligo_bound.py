from itb.constraints.base import ConstraintClass
from itb.constraints.ligo_graviton_mass import LIGOGravitonMassBound
from itb.theory import Theory


def test_class_b_information():
    c = LIGOGravitonMassBound()
    assert c.constraint_class is ConstraintClass.B_INFORMATION
    assert "LIGO" in c.citation


def test_satisfied_when_g_R2_small():
    c = LIGOGravitonMassBound(bound=0.1)
    assert c.evaluate(Theory(coefficients={"g_R2": 0.05})).satisfied is True


def test_violated_when_g_R2_exceeds_bound():
    c = LIGOGravitonMassBound(bound=0.1)
    assert c.evaluate(Theory(coefficients={"g_R2": 0.5})).satisfied is False


def test_string_eft_passes_default_ligo_bound():
    """v0.5 string-EFT predicts g_R2 = 0.2; default bound is 0.1, so it FAILS."""
    from itb.frameworks.string_tree_eft import StringTreeEFT
    c = LIGOGravitonMassBound(bound=0.1)
    assert c.evaluate(StringTreeEFT().encode()).satisfied is False


def test_asymptotic_safety_passes_default_ligo_bound():
    """v0.7 AS predicts g_R2 = 0.15; default bound is 0.1, so it ALSO FAILS."""
    from itb.frameworks.asymptotic_safety import AsymptoticSafety
    c = LIGOGravitonMassBound(bound=0.1)
    # AS at g_R2 = 0.15 violates a bound of 0.1
    assert c.evaluate(AsymptoticSafety().encode()).satisfied is False


def test_pure_gr_passes_any_ligo_bound():
    from itb.frameworks.pure_gr import PureGR
    c = LIGOGravitonMassBound(bound=0.1)
    assert c.evaluate(PureGR().encode()).satisfied is True


def test_loose_bound_admits_more_theories():
    """If we relax the bound (e.g., taking cutoff farther from Planck), more
    theories pass."""
    from itb.frameworks.string_tree_eft import StringTreeEFT
    c_loose = LIGOGravitonMassBound(bound=0.5)
    assert c_loose.evaluate(StringTreeEFT().encode()).satisfied is True
