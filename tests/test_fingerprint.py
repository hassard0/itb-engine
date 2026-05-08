import numpy as np

from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.eft_validity import EFTValidityBox
from itb.constraints.graviton_eft import GravitonMixedPositivity
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.fingerprint import (
    Fingerprint,
    fingerprint_distance,
    fingerprint_framework,
    fingerprint_matrix,
)
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.observables import ScalarForwardAmplitude


def _full():
    return [
        ScalarPositivityG4(), ScalarPositivityG6(), ScalarConvexityG6vsG4(),
        GravitonMixedPositivity(), BekensteinTight(), EFTValidityBox(box=2.0),
    ]


def test_fingerprint_for_pure_gr():
    fp = fingerprint_framework(PureGR(), _full())
    assert isinstance(fp, Fingerprint)
    assert fp.framework_name == "pure_gr"
    assert fp.feasible is True


def test_fingerprint_for_string_tree_eft():
    fp = fingerprint_framework(StringTreeEFT(), _full())
    assert fp.feasible is True
    assert fp.fragility_distance >= 0


def test_distance_zero_for_self():
    fp = fingerprint_framework(StringTreeEFT(), _full())
    assert fingerprint_distance(fp, fp) == 0.0


def test_distance_positive_for_different_frameworks():
    a = fingerprint_framework(PureGR(), _full())
    b = fingerprint_framework(StringTreeEFT(), _full())
    assert fingerprint_distance(a, b) > 0


def test_observable_values_included_when_observable_supplied():
    obs = {"forward": ScalarForwardAmplitude(s_values=np.array([0.5, 1.0]))}
    fp = fingerprint_framework(StringTreeEFT(), _full(), observables=obs)
    assert "forward" in fp.observable_values
    assert fp.observable_values["forward"].shape == (2,)


def test_matrix_is_symmetric_with_zero_diagonal():
    fps = [
        fingerprint_framework(PureGR(), _full()),
        fingerprint_framework(StringTreeEFT(), _full()),
    ]
    m = fingerprint_matrix(fps)
    assert m.shape == (2, 2)
    np.testing.assert_allclose(m, m.T)
    assert m[0, 0] == 0.0
    assert m[1, 1] == 0.0
