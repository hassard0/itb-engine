from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.eft_validity import EFTValidityBox
from itb.constraints.graviton_eft import GravitonMixedPositivity
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.engine import check
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.lqg_induced import LQGInduced


def _full():
    return [
        ScalarPositivityG4(), ScalarPositivityG6(), ScalarConvexityG6vsG4(),
        GravitonMixedPositivity(), BekensteinTight(), EFTValidityBox(box=2.0),
    ]


def test_asymptotic_safety_survives_full_stack():
    theory = AsymptoticSafety().encode()
    report = check(theory, _full())
    assert report.feasible is True


def test_lqg_induced_survives_full_stack():
    theory = LQGInduced().encode()
    report = check(theory, _full())
    assert report.feasible is True


def test_three_frameworks_produce_distinct_fingerprints():
    from itb.fingerprint import fingerprint_framework, fingerprint_distance
    from itb.frameworks.string_tree_eft import StringTreeEFT

    fps = [
        fingerprint_framework(StringTreeEFT(), _full()),
        fingerprint_framework(AsymptoticSafety(), _full()),
        fingerprint_framework(LQGInduced(), _full()),
    ]
    # All pairwise distances strictly positive
    for i, a in enumerate(fps):
        for j, b in enumerate(fps):
            if i != j:
                assert fingerprint_distance(a, b) > 0


def test_lqg_induced_has_largest_g_R2_to_matter_ratio():
    """LQG-induced should have g_R2/sqrt(g_4*g_6) larger than the others —
    that's the framework signature."""
    import math
    from itb.frameworks.string_tree_eft import StringTreeEFT

    def ratio(t):
        c = t.coefficients
        return c["g_R2"] / math.sqrt(c["g_4"] * c["g_6"])

    s = ratio(StringTreeEFT().encode())
    a = ratio(AsymptoticSafety().encode())
    l = ratio(LQGInduced().encode())
    assert l > s
    assert l > a
