"""Tests for the Leaver continued-fraction machinery + blocker diagnosis (v2.260)."""

from experiments.qnm_leaver_continued_fraction import (
    constant_cf_tail,
    continued_fraction,
    run,
    solve_root_demo,
    validate_machinery,
)


def test_cf_evaluator_matches_analytic_tail():
    m = validate_machinery()
    assert m["match"] is True
    assert abs(m["cf_numeric"] - m["cf_analytic"]) < 1e-9


def test_constant_tail_solves_quadratic():
    # T = (b - sqrt(b^2-4 a g))/2 satisfies T(b - T) = a g
    a, b, g = 1.0, 5.0, 2.0
    T = constant_cf_tail(a, b, g)
    assert abs(T * (b - T) - a * g) < 1e-12


def test_root_finder_recovers_known_root():
    r = solve_root_demo()
    assert r["recovered"] is True
    assert abs(r["root_found"] - r["omega_star"]) < 1e-9


def test_machinery_works_but_solver_not_delivered():
    res = run()
    assert res["machinery_works"] is True
    # honest: no QNM value is claimed; the coefficients are the missing piece
    assert "NOT delivered" in res["honest_scope"]
    assert res["blocker_diagnosis"]["status"].startswith("dedicated")


def test_honest_scope_negative_result():
    res = run()
    sc = res["honest_scope"].lower()
    assert "negative-result" in sc and "not delivered" in sc
    assert "wkb solver remains" in sc
    assert "g_R4_c3" in res["honest_scope"]
