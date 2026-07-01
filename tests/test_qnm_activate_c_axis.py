"""Tests for the c-axis activation swing (v2.398)."""

from experiments.qnm_activate_c_axis import run

_RES = run(n_scan=300)


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_c_axis_is_hm_wedge():
    ac = _RES["a_over_c_range"]
    wedge = _RES["HM_wedge_analytic"]
    assert abs(ac[0] - wedge[0]) < 0.03
    assert abs(ac[1] - wedge[1]) < 0.06


def test_hm_sole_carver():
    assert all("hofman" in c for c in _RES["c_axis_lower_edge_binding"])
    assert all("hofman" in c for c in _RES["c_axis_upper_edge_binding"])


def test_constructed_dead_center_and_ghost_moves():
    lo, hi = _RES["feasible_gC_range"]
    assert lo < 0.193 < hi                       # a=c point interior (dead-center)
    g = _RES["ghost_mass_over_cutoff_range"]
    assert g[1] - g[0] > 0.5                      # ghost mass now varies with g_C


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "resolve c != a" in f or "resolving c != a" in f
    assert "dormant" in f
    assert "sole carver" in f
    sc = _RES["honest_scope"].lower()
    assert "activates a dormant-but-built axis" in sc or "required no new code" in sc
    assert "candidate theory is unchanged" in sc or "stays at a = c" in sc
