"""Tests for the theory+data region extent (v2.327)."""

from experiments.qnm_theory_data_region_extent import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_region_is_tiny():
    assert _RES["box_feasible_fraction"] < 1e-3


def test_parity_is_tightest_pinned():
    assert _RES["tightest_coupling"] == "g_R2_parity"
    widths = {k: e["width"] for k, e in _RES["coupling_extents"].items()}
    assert widths["g_R2_parity"] == min(widths.values())


def test_parity_interval_is_the_data_window():
    iv = _RES["coupling_extents"]["g_R2_parity"]["interval"]
    assert abs(iv[0] - 0.048) < 0.01
    assert abs(iv[1] - 0.078) < 0.01


def test_matter_sector_looser_than_parity():
    e = _RES["coupling_extents"]
    for m in ("g_4", "g_6", "g_8"):
        assert e[m]["width"] > e["g_R2_parity"]["width"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "tightly pinned" in f or "tiny region" in f
    assert "parity sector" in f
    assert "most testable" in f or "most sharply predicted" in f
    sc = _RES["honest_scope"].lower()
    assert "deterministic line searches" in sc
    assert "toy basis" in sc
