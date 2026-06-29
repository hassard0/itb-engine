"""Tests for the QG-phenomenology + swampland arc synthesis (v2.256)."""

from experiments.qnm_qg_phenomenology_synthesis import arc_map, cross_checks, run


def test_cross_arc_consistency_holds():
    res = run()
    assert res["all_consistent"] is True
    for c in res["cross_arc_consistency"]:
        assert c["ok"] is True


def test_planck_convention_and_engine_checks_present():
    names = " ".join(c["check"] for c in cross_checks())
    assert "M_Pl" in names and "sqrt(8pi)" in names
    assert "distance_conjecture" in names and "cosmic_birefringence" in names


def test_arc_has_phenomenology_and_consistency_axes():
    amap = arc_map()
    axes = [a["axis"] for a in amap]
    assert any("PHENOMENOLOGY" in a for a in axes)
    assert any("CONSISTENCY" in a for a in axes)
    # three phenomenology cycles, two consistency cycles
    phen = next(a for a in amap if "PHENOMENOLOGY" in a["axis"])
    assert len(phen["cycles"]) == 3


def test_honest_scope_synthesis():
    res = run()
    sc = res["honest_scope"].lower()
    assert "synthesis" in sc and "not a new measurement" in sc
    assert "conjecture" in sc
    assert "g_R4_c3" in res["honest_scope"]
