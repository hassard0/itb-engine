"""Tests for the lqg anomaly decomposition (v2.282)."""

from experiments.qnm_lqg_anomaly_decomposition import (
    CURVATURE,
    MATTER,
    margins,
    run,
    scaled_theory,
)
from experiments.stack import build_stack, frameworks
from itb.constraints.gw_speed import GWSpeedBound
from itb.constraints.gw_dispersion import GWDispersionBound


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_lqg_fails_six_constraints():
    res = run()
    assert len(res["failing_constraints"]) == 6


def test_all_failures_heal_with_curvature_off():
    # turning the curvature sector fully off must heal every lqg failure
    res = run()
    for d in res["decomposition"]:
        assert d["curvature_off_margin"] >= 0, d["constraint"]


def test_forward_positivity_is_purely_curvature_driven():
    # graviton_forward_positivity = the moment-tower physics; matter scaling must NOT heal it
    res = run()
    fp = next(d for d in res["decomposition"] if d["constraint"] == "graviton_forward_positivity")
    assert fp["matter_off_margin"] < 0          # matter off does not heal it
    assert fp["curvature_off_margin"] >= 0       # curvature off does
    assert fp["classification"] == "curvature-driven"


def test_scaling_curvature_to_zero_changes_margin():
    # sanity: the scaled-theory helper actually moves the engine margins
    stack = build_stack() + [GWSpeedBound(low_cutoff=True), GWDispersionBound(low_cutoff=True)]
    lqg = [f for f in frameworks() if f.name == "lqg_induced"][0]
    base = dict(lqg.encode().coefficients)
    m_full = margins(scaled_theory(base, CURVATURE, 1.0, "x"), stack)
    m_off = margins(scaled_theory(base, CURVATURE, 0.0, "x"), stack)
    assert m_off["graviton_forward_positivity"] > m_full["graviton_forward_positivity"]
    # matter keys exist and are scalable
    assert all(k in base for k in MATTER)


def test_honest_scope_flags_engine_encoding():
    res = run()
    sc = res["honest_scope"].lower()
    assert "does not re-derive" in sc or "not a new constraint" in sc
    assert "+/-0.05" in sc or "0.05-step" in sc
    assert "lqg encoding" in sc or "representative" in sc
