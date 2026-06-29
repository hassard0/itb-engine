"""Tests for the axial-vs-polar isospectrality-breaking response (v2.224)."""

from experiments.qnm_parity_sensitivity import parity_breaking, run, sensitivity
from experiments.qnm_isospectrality import zerilli_potential
from experiments.qnm_wkb_solver import rw_potential


def test_breaking_grows_monotonically_with_j():
    res = run()
    assert res["breaking_monotonic_in_j"] is True
    # long-range deformation breaks isospectrality weakly; near-horizon strongly
    assert res["breaking_j2"] < 0.2
    assert res["breaking_j10"] > 0.8


def test_axial_and_polar_responses_differ():
    # the same deformation produces a different QNM shift in each parity sector
    dV = lambda r: (2.0 / r) ** 10
    sa = sensitivity(lambda r: rw_potential(r, 2, 2), dV)
    sp = sensitivity(lambda r: zerilli_potential(r, 2), dV)
    assert abs(sp - sa) / abs(sa) > 0.5


def test_low_power_nearly_isospectral_response():
    # a j=2 (long-range) deformation gives nearly the same response in both sectors
    rows = parity_breaking(L=2, n=0)
    j2 = next(r for r in rows if r["j"] == 2)
    assert j2["breaking_ratio"] < 0.2


def test_honest_scope_ratio_robust_absolute_caveated():
    res = run()
    sc = res["honest_scope"].lower()
    assert "method-consistent" in sc
    assert "v2.212" in res["honest_scope"]
    assert "not claim-grade numbers" in sc or "only the parity-ratio" in sc
    assert "g_R4_c3" in res["honest_scope"]
