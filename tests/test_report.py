from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.eft_validity import EFTValidityBox
from itb.constraints.graviton_eft import GravitonMixedPositivity
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.report import render_framework_comparison


def _full():
    return [
        ScalarPositivityG4(), ScalarPositivityG6(), ScalarConvexityG6vsG4(),
        GravitonMixedPositivity(), BekensteinTight(), EFTValidityBox(box=2.0),
    ]


def test_report_includes_all_frameworks():
    frameworks = [PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced()]
    md = render_framework_comparison(frameworks, _full())
    for fw in frameworks:
        assert fw.name in md


def test_report_has_distance_matrix():
    frameworks = [StringTreeEFT(), AsymptoticSafety(), LQGInduced()]
    md = render_framework_comparison(frameworks, _full())
    assert "Pairwise fingerprint distances" in md
    assert "string_tree_eft" in md


def test_report_lists_coefficient_table():
    frameworks = [PureGR(), StringTreeEFT()]
    md = render_framework_comparison(frameworks, _full())
    assert "g_4" in md and "g_6" in md and "g_R2" in md
