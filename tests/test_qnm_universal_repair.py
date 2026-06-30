"""Tests for the universal-repair result (v2.331)."""

from experiments.qnm_universal_repair import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_parity_even_frameworks_add_parity():
    for r in _RES["repairs"]:
        if r["framework"] in ("string_tree_eft", "asymptotic_safety", "cdt"):
            assert r["mode"] == "add_parity"
            assert r["d_parity"] > 0.02
            assert r["repaired_parity"] >= 0.047


def test_lqg_trims_cubic_keeps_parity():
    lqg = next(r for r in _RES["repairs"] if r["framework"] == "lqg_induced")
    assert lqg["mode"] == "trim_cubic"
    assert lqg["d_g_R3"] < -0.05
    assert abs(lqg["d_parity"]) < 0.03      # parity kept


def test_all_land_in_data_window():
    for r in _RES["repairs"]:
        if not r.get("already_feasible"):
            assert 0.04 <= r["repaired_parity"] <= 0.10


def test_two_complementary_modes():
    modes = {r["mode"] for r in _RES["repairs"] if not r.get("already_feasible")}
    assert "add_parity" in modes and "trim_cubic" in modes


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "attractor" in f
    assert "two complementary" in f
    sc = _RES["honest_scope"].lower()
    assert "two modes" in sc
    assert "contingent on the birefringence" in sc
    assert "toy basis" in sc
