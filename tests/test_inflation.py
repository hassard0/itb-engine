"""Tests for the Starobinsky R^2 inflation observable (v1.86)."""
import pytest

from itb.gravitational_observables import StarobinskyInflation
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.frameworks.pure_gr import PureGR
from itb.theory import Theory


def test_ns_r_formulas():
    """n_s = 1 - 2/N, r = 12/N^2."""
    inf = StarobinskyInflation(N_efolds=55)
    assert inf.n_s() == pytest.approx(1 - 2 / 55)
    assert inf.r() == pytest.approx(12 / 55 ** 2)
    # N=55 lands at the Planck sweet spot
    assert 0.96 < inf.n_s() < 0.967
    assert inf.r() < 0.036


def test_consistent_with_planck():
    """N=50-60 stays within Planck n_s and under the BK r limit."""
    for N in (50, 55, 60):
        inf = StarobinskyInflation(N)
        assert abs(inf.n_s() - 0.9649) < 2 * 0.0042 + 0.005
        assert inf.r() < 0.036


def test_viability_requires_positive_gR2():
    """A positive R^2 term gives the plateau; pure GR (g_R2=0) is not an R^2 inflaton."""
    inf = StarobinskyInflation()
    assert inf.viable(StringTreeEFT().encode())          # g_R2 = 0.2 > 0
    assert not inf.viable(PureGR().encode())             # g_R2 = 0


def test_observables_independent_of_coupling():
    """n_s, r are set by N, NOT by the Wilson coefficients (zero Jacobian)."""
    inf = StarobinskyInflation()
    J = inf.jacobian(Theory(coefficients={"g_R2": 0.2, "g_4": 0.5}), ["g_R2", "g_4"])
    assert (J == 0).all()


def test_in_predict_fingerprint():
    from itb.predict import predict
    p = predict("string_tree_eft")
    nr = p["observables"]["starobinsky_inflation_ns_r_N55"]
    assert nr is not None and len(nr) == 2
    assert 0.96 < nr[0] < 0.967 and nr[1] < 0.036
