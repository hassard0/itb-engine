"""Tests for the axion-DE swampland consistency + f_a triple convergence (v2.461)."""

from experiments.qnm_axion_de_swampland import run, one_plus_w, grad_over_v

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_fa_marginal_and_detectable():
    assert abs(_RES["fa_marginal_Mpl"] - 1.0) < 0.3
    assert _RES["one_plus_w0_at_marginal"] > 0.05     # detectable, not a pure CC


def test_desi_match_super_planckian():
    assert _RES["fa_for_desi_central_Mpl"] > 1.0       # the honest swampland tension


def test_physics_monotonic():
    # slow-roll deviation shrinks with larger f_a; refined-dS gradient shrinks too
    assert one_plus_w(2.0) < one_plus_w(1.0) < one_plus_w(0.5)
    assert grad_over_v(2.0) < grad_over_v(1.0)


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "triple convergence" in f
    assert "detectable dynamical dark energy" in f
    assert "super-planckian" in f  # the honest tension
    sc = _RES["honest_scope"].lower()
    assert "order-of-magnitude" in sc
    assert "conjecture-tier" in sc
    assert "mid-roll" in sc  # the 1+w0 estimate caveat
