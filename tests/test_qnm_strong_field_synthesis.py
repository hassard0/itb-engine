"""Tests for the strong-field program synthesis capstone (v2.242)."""

from experiments.qnm_strong_field_synthesis import cross_checks, program_map, run


def test_cross_program_consistency_holds():
    res = run()
    assert res["all_consistent"] is True
    for c in res["cross_program_consistency"]:
        assert c["ok"] is True


def test_all_checks_present():
    checks = cross_checks()
    # the load-bearing shared-physics checks
    names = " ".join(c["check"] for c in checks)
    assert "Omega_c" in names and "ISCO" in names and "Love number" in names
    assert len(checks) >= 8


def test_program_map_themes():
    themes = {t["theme"] for t in program_map()}
    assert "Kerr generalization" in themes
    assert any("Operator-sector" in t for t in themes)
    assert len(program_map()) == 5


def test_honest_scope_synthesis():
    res = run()
    sc = res["honest_scope"].lower()
    assert "synthesis" in sc and "not a new measurement" in sc
    assert "g_R4_c3" in res["honest_scope"]
