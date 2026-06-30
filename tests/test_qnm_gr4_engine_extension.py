"""Tests for the g_R4 core-engine extension (v2.292)."""

from experiments.qnm_gr4_engine_extension import run, with_gR4
from experiments.stack import build_stack
from itb.engine import check
from itb.constraints.curvature_dispersion_tower import (
    CurvatureMomentTowerMandate,
    CurvatureRiemann4Positivity,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_new_constraints_are_optin_in_build_stack():
    default = build_stack()
    tower = build_stack(include_curvature_tower=True)
    assert len(tower) == len(default) + 2
    names_default = {c.name for c in default}
    names_tower = {c.name for c in tower}
    assert "curvature_moment_tower_g_R4_mandate" not in names_default
    assert "curvature_moment_tower_g_R4_mandate" in names_tower
    assert "curvature_riemann4_positivity" in names_tower


def test_moment_tower_mandate_formula():
    c = CurvatureMomentTowerMandate()
    # g_R3^2 <= g_R2 g_R4 : margin = g_R2 g_R4 - g_R3^2
    from itb.theory import Theory
    r = c.evaluate(Theory(coefficients={"g_R2": 0.2, "g_R3": 0.15, "g_R4": 0.1125}))
    assert abs(r.margin - (0.2 * 0.1125 - 0.15**2)) < 1e-12
    assert r.satisfied is True            # exactly at the forced minimum
    r0 = c.evaluate(Theory(coefficients={"g_R2": 0.2, "g_R3": 0.15, "g_R4": 0.0}))
    assert r0.satisfied is False          # g_R4 = 0 violates the mandate


def test_riemann4_positivity():
    c = CurvatureRiemann4Positivity()
    from itb.theory import Theory
    assert c.evaluate(Theory(coefficients={"g_R4": 0.1})).satisfied is True
    assert c.evaluate(Theory(coefficients={"g_R4": -0.01})).satisfied is False


def test_mandate_binds_curvature_frameworks_at_zero():
    # each curvature framework is infeasible against the tower at g_R4=0, feasible at the forced min
    res = run()
    tower = [CurvatureRiemann4Positivity(), CurvatureMomentTowerMandate()]
    for r in res["framework_mandate"]:
        if r["g_R3"] > 0:
            assert r["feasible_at_gR4_0"] is False
            assert r["feasible_at_forced_min"] is True
            base = {"g_R2": r["g_R2"], "g_R3": r["g_R3"]}
            assert not check(with_gR4(base, 0.0), tower).feasible


def test_forced_minima_reproduce_v234():
    res = run()
    by = {r["framework"]: r["forced_gR4_min"] for r in res["framework_mandate"]}
    assert abs(by["string_tree_eft"] - 0.1125) < 5e-3
    assert abs(by["lqg_induced"] - 0.30) < 5e-3
    assert by["pure_gr"] == 0.0


def test_honest_scope_flags_first_slice():
    res = run()
    sc = res["honest_scope"].lower()
    assert "core-engine extension" in sc
    assert "next slice" in sc
    assert "representative" in sc
