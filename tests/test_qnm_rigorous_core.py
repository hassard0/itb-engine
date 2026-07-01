"""Tests for the rigorous-core engine-improvement cycle (v2.411)."""

from experiments.qnm_rigorous_core import run
from experiments.stack import RIGOR, rigor_of, rigorous_core_stack, build_stack, filter_by_rigor

_RES = run(n_pts=1500)


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_rigor_registry_capability():
    # the new engine capability exists and covers the whole stack
    full = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                       include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)
    names = [c.name for c in full]
    assert all(n in RIGOR for n in names)
    core = rigorous_core_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                               include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)
    assert all(rigor_of(c.name) == "rigorous" for c in core)
    assert len(core) == _RES["tier_counts"]["rigorous"] == 19


def test_candidate_in_core_and_lqg_excluded():
    assert _RES["constructed_feasible_under_rigorous_core"] is True
    assert "lqg_induced" in _RES["excluded_by_rigorous_core"]
    # LQG is killed by a genuine amplitude/causality bound, not a borderline one
    v = _RES["frameworks_under_rigorous_core"]["lqg_induced"]["rigorous_violations"]
    assert any(b in v for b in ("graviton_forward_positivity", "cross_sector_efthedron", "cft_flat_space_bound"))


def test_proxy_tier_does_size_carving():
    lf = _RES["local_feasible_fraction"]
    assert lf["core_looser_x"] > 5.0    # the toy tiers do most of the SIZE shrinking


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "first-class rigor classification" in f
    assert "excludes lqg-induced gravity" in f or "exclude lqg-induced gravity" in f
    assert "zero-toy" in f or "no toy input" in f
    sc = _RES["honest_scope"].lower()
    assert "judgement" in sc
    assert "framework encoding" in sc or "encoding-conditional" in sc
    assert "source-exact in form" in sc or "not 'zero approximation'" in sc
