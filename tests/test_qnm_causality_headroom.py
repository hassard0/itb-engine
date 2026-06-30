"""Tests for the CEMZ causality-headroom result (v2.339)."""

from experiments.qnm_causality_headroom import run, cemz_bound

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_all_candidates_causal():
    for r in _RES["causality_table"]:
        assert r["causal"] is True
        assert r["headroom"] > 0


def test_constructed_deepest_inside():
    rows = _RES["causality_table"]
    assert rows[0]["theory"] == "engine_constructed"
    assert rows[0]["fraction_of_bound"] < 0.5


def test_lqg_nearest_edge():
    rows = _RES["causality_table"]
    assert rows[-1]["theory"] == "lqg_induced"
    assert rows[-1]["fraction_of_bound"] > 0.8


def test_trimmed_cubic_gives_headroom():
    rows = _RES["causality_table"]
    smallest_cubic = min(rows, key=lambda r: r["g_R3"])
    most_headroom = max(rows, key=lambda r: r["headroom"])
    assert smallest_cubic["theory"] == "engine_constructed"
    assert most_headroom["theory"] == "engine_constructed"
    # bound formula sanity
    assert abs(cemz_bound(0.529, 0.193) - 0.8 * (0.529 * 0.193) ** 0.5) < 1e-9


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "causal" in f and "headroom" in f
    assert "trimmed cubic" in f
    assert "higher-spin tower" in f
    sc = _RES["honest_scope"].lower()
    assert "ordering" in sc
    assert "toy basis" in sc
