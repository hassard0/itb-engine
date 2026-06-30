"""Tests for the new-theory arc synthesis capstone (v2.299)."""

from experiments.qnm_new_theory_arc_synthesis import run


def test_all_checks_pass():
    res = run()
    assert res["all_pass"] is True
    assert res["checks_passed"] == res["checks_total"] == 6
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_arc_has_seven_cycles():
    res = run()
    cycles = [a["cycle"] for a in res["arc"]]
    assert cycles == ["v2.292", "v2.293", "v2.294", "v2.295", "v2.296", "v2.297", "v2.298"]


def test_four_structures_converge_on_lqg():
    res = run()
    flags = res["lqg_flags"]
    assert flags["moment_tower_saturated"] is True
    assert flags["largest_W_plus"] is True
    assert flags["excluded_by_carving"] is True
    assert flags["forced_parity_odd_quartic"] is True


def test_other_frameworks_inside_on_every_axis():
    res = run()
    for n, v in res["framework_arc_verdicts"].items():
        if n != "lqg_induced":
            assert v["x_ratio"] < 1.0                 # not at the moment-tower boundary
            assert v["carving_excludes"] is False      # admitted by the carving
            assert abs(v["g_R4_parity_forced"]) < 1e-9  # no forced parity-odd quartic


def test_lqg_excluded_others_admitted_by_carving():
    res = run()
    t = res["framework_arc_verdicts"]
    assert t["lqg_induced"]["carving_excludes"] is True
    assert t["string_tree_eft"]["carving_excludes"] is False


def test_honest_scope_flags_conditional_and_toy():
    res = run()
    sc = res["honest_scope"].lower()
    assert "no new constraint" in sc
    assert "toy encoding" in sc
    assert "not a claim about physical loop quantum gravity" in sc
    assert "demoted" in sc
