from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.theory import Theory


def test_returns_theory():
    fw = StringTreeEFT()
    theory = fw.encode()
    assert isinstance(theory, Theory)


def test_metadata_string_origin():
    theory = StringTreeEFT().encode()
    assert theory.name == "string_tree_eft"
    assert "string" in theory.source.lower() or "α'" in theory.source


def test_predicts_positive_g_4_and_g_6():
    """Tree-level string corrections produce positive higher-order coefficients."""
    theory = StringTreeEFT().encode()
    assert theory.coefficients["g_4"] > 0
    assert theory.coefficients["g_6"] > 0


def test_satisfies_amplitude_bootstrap_constraints():
    from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
    from itb.constraints.scalar_positivity import (
        ScalarPositivityG4,
        ScalarPositivityG6,
    )
    from itb.engine import check

    theory = StringTreeEFT().encode()
    constraints = [
        ScalarPositivityG4(),
        ScalarPositivityG6(),
        ScalarConvexityG6vsG4(),
    ]
    report = check(theory, constraints)
    assert report.feasible is True


def test_string_eft_is_within_full_constraint_set():
    """The acid test: does string-EFT survive ALL classes simultaneously?"""
    from itb.constraints.bekenstein_tight import BekensteinTight
    from itb.constraints.eft_validity import EFTValidityBox
    from itb.constraints.graviton_eft import GravitonMixedPositivity
    from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
    from itb.constraints.scalar_positivity import (
        ScalarPositivityG4,
        ScalarPositivityG6,
    )
    from itb.engine import check

    theory = StringTreeEFT().encode()
    constraints = [
        ScalarPositivityG4(),
        ScalarPositivityG6(),
        ScalarConvexityG6vsG4(),
        GravitonMixedPositivity(),
        BekensteinTight(),
        EFTValidityBox(box=2.0),
    ]
    report = check(theory, constraints)
    # If this fails it is the most interesting kind of failure: it would
    # mean the engine has detected that string theory's predicted Wilson
    # coefficients are inconsistent with the union of all our constraints,
    # which would be a real physics result. (We expect it to pass given
    # how we set up the toy values, but the check is the point.)
    assert report.feasible is True, (
        f"String tree EFT failed: binding={report.binding}, "
        f"results={[(r.constraint_name, r.margin) for r in report.results]}"
    )
