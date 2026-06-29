"""Tests for the ISCO / accretion efficiency observable (v2.237)."""

import math

from experiments.qnm_isco_accretion import isco, run


def test_schwarzschild_isco_closed_forms():
    b = isco(0.0)
    assert abs(b["r_isco"] - 6.0) < 1e-5
    assert abs(b["E_isco"] - math.sqrt(8 / 9)) < 1e-5
    assert abs(b["efficiency"] - (1 - math.sqrt(8 / 9))) < 1e-5
    assert abs(b["Omega_isco"] - 1 / (6 * math.sqrt(6))) < 1e-5


def test_run_all_match():
    res = run()
    assert res["all_match"] is True


def test_deformation_shrinks_isco_and_raises_efficiency():
    res = run()
    s3 = res["deformation_sensitivity"]["k=3"]
    # a positive eps/r^3 bump pulls the ISCO inward and raises efficiency + frequency
    assert s3["r_isco_d_eps"] < 0
    assert s3["efficiency_d_eps"] > 0
    assert s3["Omega_isco_d_eps"] > 0
    # more localized (k=4) deformation has a weaker effect
    s4 = res["deformation_sensitivity"]["k=4"]
    assert abs(s4["r_isco_d_eps"]) < abs(s3["r_isco_d_eps"])


def test_honest_scope_multimessenger():
    res = run()
    sc = res["honest_scope"].lower()
    assert "schwarzschild" in sc and "illustrative" in sc
    assert "multi-messenger" in res["finding"].lower()
    assert "g_R4_c3" in res["honest_scope"]
